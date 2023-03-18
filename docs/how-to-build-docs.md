# How to Build the Documentation

Activate your virtual environment for the documentation.

Change to the root of the repository.

Install the code in the environment:

```
pip3 install --editable .
```

Install the documentation requirements:

```
pip3 install -r docs/requirements.txt
```

Build with Sphinx:

```
cd docs
sphinx-build source build
```

The documentation is in the `docs/build` directory.

Test the examples in the documentation with the ``doctest`` builder:

```
sphinx-build source -b doctest
```
