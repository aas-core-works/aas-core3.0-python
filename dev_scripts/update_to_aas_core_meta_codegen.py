"""
Update everything in this project to the latest aas-core-meta and -codegen.

Git is expected to be installed.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
from typing import Optional, List, Callable, AnyStr, Sequence


def _make_sure_no_changed_files(
    repo_dir: pathlib.Path, expected_branch: str
) -> Optional[int]:
    """
    Make sure that no files are modified in the given repository.

    Return exit code if something is unexpected.
    """
    diff_name_status = subprocess.check_output(
        ["git", "diff", "--name-status", expected_branch],
        cwd=str(repo_dir),
        encoding="utf-8",
    ).strip()

    if len(diff_name_status.splitlines()) > 0:
        print(
            f"The following files are modified "
            f"compared to branch {expected_branch!r} in {repo_dir}:\n"
            f"{diff_name_status}\n"
            f"\n"
            f"Please stash the changes first before you update to aas-core-meta.",
            file=sys.stderr,
        )
        return 1

    return None


def _run_in_parallel(
    calls: Sequence[Callable[[], subprocess.Popen[AnyStr]]],
    on_status_update: Callable[[int], None],
) -> Optional[int]:
    """
    Run the given scripts in parallel.

    Return an error code, if any.
    """
    procs = []  # type: List[subprocess.Popen[AnyStr]]

    try:
        for call in calls:
            proc = call()
            procs.append(proc)

        failure = False
        remaining_procs = sum(1 for proc in procs if proc.returncode is None)

        next_print = time.time() + 15
        while remaining_procs > 0:
            if time.time() > next_print:
                on_status_update(remaining_procs)
                next_print = time.time() + 15

            time.sleep(1)

            for proc in procs:
                proc.poll()

                if proc.returncode is not None:
                    if proc.returncode != 0:
                        failure = True

            if failure:
                print(
                    "One or more processes failed. Terminating all the processes...",
                    file=sys.stderr,
                )
                for proc in procs:
                    proc.terminate()

                print("Terminated all the processes.", file=sys.stderr)
                return 1

            for proc in procs:
                proc.poll()

            remaining_procs = sum(1 for proc in procs if proc.returncode is None)

        return None
    finally:
        for proc in procs:
            if proc.returncode is None:
                proc.terminate()


def _regenerate_code(our_repo: pathlib.Path) -> Optional[int]:
    """
    Call codegen script.

    Return an error code, if any.
    """
    codegen_dir = our_repo / "dev_scripts/codegen"

    meta_model_path = codegen_dir / "meta_model.py"

    target_dir = our_repo

    print("Starting to run codegen script")
    start = time.perf_counter()

    proc = subprocess.run(
        [
            sys.executable,
            "codegen.py",
            "--meta_model",
            str(meta_model_path),
            "--target",
            str(target_dir),
        ],
        cwd=str(codegen_dir),
        check=True,
    )

    if proc.returncode != 0:
        return proc.returncode

    duration = time.perf_counter() - start
    print(f"Generating the code took: {duration:.2f} seconds.")

    return None


def _reformat_code(our_repo: pathlib.Path) -> None:
    """Reformat the generated code."""
    print("Re-formatting the code...")

    precommit_script = our_repo / "continuous_integration/precommit.py"

    subprocess.check_call(
        [sys.executable, str(precommit_script), "--select", "reformat", "--overwrite"],
        cwd=our_repo,
    )


def _run_tests_and_rerecord(our_repo: pathlib.Path) -> Optional[int]:
    """
    Run the tests with the environment variables set to re-record.

    Return the error code, if any.
    """
    print("Running tests & re-recording the test traces...")

    env = os.environ.copy()
    env["AAS_CORE3_0_PYTHON_TESTS_RECORD_MODE"] = "true"

    # NOTE (mristin):
    # We need to include the repository root on the PYTHNPATH since the newer
    # versions of Python (such as 3.11 and 3.12) exclude ``tests/`` from it --
    # they rely on setup.py excluding them in ``find_package``:
    #
    # ``packages=find_packages(exclude=["tests", ...]),``
    #
    # . This means that the ``tests`` module will not be on the Python path, as newer
    # versions of setuptools only put packages explicitly found by ``find_packages``.

    python_path = env.get("PYTHONPATH", None)
    if python_path is None:
        python_path = str(our_repo)
    else:
        python_path = f"{python_path}{os.pathsep}{str(our_repo)}"

    env["PYTHONPATH"] = python_path

    test_files = sorted((our_repo / "tests").glob("**/test_*.py"))

    # pylint: disable=consider-using-with
    calls = [
        lambda a_pth=pth, cwd=our_repo: subprocess.Popen(  # type: ignore
            [sys.executable, str(a_pth)],
            cwd=str(cwd),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
            env=env,
        )
        for pth in test_files
    ]  # type: Sequence[Callable[[], subprocess.Popen[str]]]
    # pylint: enable=consider-using-with

    test_files_joined = ",\n".join(str(pth) for pth in test_files)
    print(f"Starting to run test modules:\n{test_files_joined}")
    start = time.perf_counter()

    exit_code = _run_in_parallel(
        calls=calls,
        on_status_update=(
            lambda remaining: print(
                f"There are {remaining} test module(s) still running..."
            )
        ),
    )
    if exit_code is not None:
        return exit_code

    duration = time.perf_counter() - start
    print(f"Re-recording took: {duration:.2f} seconds.")

    return None


def _create_branch_commit_and_push(
    our_repo: pathlib.Path,
    aas_core_meta_revision: str,
    aas_core_codegen_revision: str,
    aas_core_testgen_revision: str,
) -> None:
    """Create a feature branch, commit the changes and push it."""
    branch = (
        f"Update-to-aas-core-meta-codegen-testgen-{aas_core_meta_revision}-"
        f"{aas_core_codegen_revision}-{aas_core_testgen_revision}"
    )
    print(f"Creating the branch {branch!r}...")
    subprocess.check_call(["git", "checkout", "-b", branch], cwd=our_repo)

    print("Adding files...")
    subprocess.check_call(["git", "add", "."], cwd=our_repo)

    # pylint: disable=line-too-long
    message = f"""\
Update to aas-core-meta, codegen, testgen {aas_core_meta_revision}, {aas_core_codegen_revision}, {aas_core_testgen_revision}

We update the development requirements to and re-generate everything
with:
* [aas-core-meta {aas_core_meta_revision}],
* [aas-core-codegen {aas_core_codegen_revision}] and
* [aas-core3.0-testgen {aas_core_testgen_revision}].

[aas-core-meta {aas_core_meta_revision}]: https://github.com/aas-core-works/aas-core-meta/commit/{aas_core_meta_revision}
[aas-core-codegen {aas_core_codegen_revision}]: https://github.com/aas-core-works/aas-core-codegen/commit/{aas_core_codegen_revision}
[aas-core3.0-testgen {aas_core_testgen_revision}]: https://github.com/aas-core-works/aas-core3.0-testgen/commit/{aas_core_testgen_revision}
"""

    # pylint: enable=line-too-long

    print("Committing...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = pathlib.Path(tmp_dir) / "commit-message.txt"
        tmp_file.write_text(message, encoding="utf-8")

        subprocess.check_call(["git", "commit", "--file", str(tmp_file)], cwd=our_repo)

    print(f"Pushing to remote {branch}...")
    subprocess.check_call(["git", "push", "-u"], cwd=our_repo)


_AAS_CORE_CODEGEN_SHA_RE = re.compile(
    r"aas-core-codegen@git\+https://github.com/aas-core-works/aas-core-codegen@([a-zA-Z0-9]+)"
)


def _get_codegen_revision(our_repo: pathlib.Path) -> str | None:
    pyproject_toml_path = our_repo / "dev_scripts/pyproject.toml"

    codegen_sha: str | None = None

    sha_re = re.compile(_AAS_CORE_CODEGEN_SHA_RE)

    try:
        with pyproject_toml_path.open("r") as pyproject_toml_file:
            for line in pyproject_toml_file:
                matches = sha_re.search(line)

                if matches is None:
                    continue

                codegen_sha = matches.group(1)
                break

    except OSError as os_error:
        print(f"Cannot read codegen revision: {os_error}.")

    if codegen_sha is None:
        print("Cannot read codegen revision.")

    return codegen_sha


_AAS_CORE_META_SHA_RE = re.compile(
    r"https://raw.githubusercontent.com/aas-core-works/aas-core-meta/([a-zA-Z0-9]+)/aas_core_meta/v.*.py"
)


def _get_meta_model_revision(our_repo: pathlib.Path) -> str | None:
    meta_model_path = our_repo / "dev_scripts/codegen/meta_model.py"

    meta_model_sha: str | None = None

    sha_re = re.compile(_AAS_CORE_META_SHA_RE)

    try:
        with meta_model_path.open("r") as meta_model_file:
            for line in meta_model_file:
                matches = sha_re.search(line)

                if matches is None:
                    continue

                meta_model_sha = matches.group(1)[:8]
                break

    except OSError as os_error:
        print(f"Cannot read meta model revision: {os_error}.")

    if meta_model_sha is None:
        print("Cannot read meta model revision.")

    return meta_model_sha


def _get_testgen_revision(our_repo: pathlib.Path) -> str | None:
    testgen_rev_path = our_repo / "tests/testgen_rev.txt"

    testgen_rev: str | None = None

    try:
        with testgen_rev_path.open("r") as testgen_rev_file:
            testgen_rev = testgen_rev_file.read().strip()
    except OSError as os_error:
        print(f"Cannot read testgen revision: {os_error}.")

    if testgen_rev is None:
        print("Cannot read testgen revision.")

    return testgen_rev


def main() -> int:
    """Execute the main routine."""
    this_path = pathlib.Path(os.path.realpath(__file__))
    our_repo = this_path.parent.parent

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--expected_our_branch",
        help="Git branch expected in this repository",
        default="main",
    )

    args = parser.parse_args()

    expected_our_branch = str(args.expected_our_branch)

    # region Our repo

    our_branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=str(our_repo),
        encoding="utf-8",
    ).strip()
    if our_branch != expected_our_branch:
        print(
            f"--expected_our_branch is {expected_our_branch}, "
            f"but got {our_branch} in: {our_repo}",
            file=sys.stderr,
        )
        return 1

    # endregion

    exit_code = _make_sure_no_changed_files(
        repo_dir=our_repo, expected_branch=expected_our_branch
    )
    if exit_code is not None:
        return exit_code

    exit_code = _regenerate_code(our_repo=our_repo)
    if exit_code is not None:
        return exit_code

    _reformat_code(our_repo=our_repo)

    exit_code = _run_tests_and_rerecord(our_repo=our_repo)
    if exit_code is not None:
        return exit_code

    aas_core_codegen_revision = _get_codegen_revision(our_repo=our_repo)
    if aas_core_codegen_revision is None:
        return 1

    aas_core_meta_revision = _get_meta_model_revision(our_repo=our_repo)
    if aas_core_meta_revision is None:
        return 1

    aas_core_testgen_revision = _get_testgen_revision(our_repo=our_repo)
    if aas_core_testgen_revision is None:
        return 1

    _create_branch_commit_and_push(
        our_repo=our_repo,
        aas_core_meta_revision=aas_core_meta_revision,
        aas_core_codegen_revision=aas_core_codegen_revision,
        aas_core_testgen_revision=aas_core_testgen_revision,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
