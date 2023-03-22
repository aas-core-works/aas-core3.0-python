******
Verify
******

Our SDK allows you to verify that a model satisfies the constraints of the meta-model.

The verification logic is concentrated in the module :py:mod:`aas_core3.verification`, and all it takes is a call to :py:func:`aas_core3.verification.verify` function.
The function :py:func:`aas_core3.verification.verify` will check that constraints in the given model element are satisfied, including the recursion into children elements.
The function returns an iterator of :py:class:`aas_core3.verification.Error`'s, which you can use for further processing (*e.g.*, report to the user).

Here is a short example snippet:

.. testcode::

    import aas_core3.types as aas_types
    import aas_core3.verification as aas_verification

    # Prepare the environment
    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id_short="someIdShort",
                id="some-unique-global-identifier",
                submodel_elements=[
                    aas_types.Property(
                        # The ID-shorts must be proper variable names,
                        # but there is a dash ("-") in this ID-short.
                        id_short = "some-Property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1984"
                    )
                ]
            )
        ]
    )

    for error in aas_verification.verify(environment):
        print(f"{error.path}: {error.cause}")

Expected output:

.. testoutput::

        .submodels[0].submodel_elements[0].id_short: ID-short of Referables shall only feature letters, digits, underscore (``_``); starting mandatory with a letter. *I.e.* ``[a-zA-Z][a-zA-Z0-9_]*``.

Limit the Number of Reported Errors
===================================

Since the function :py:func:`aas_core3.verification.verify` gives you an iterator, you can use :py:mod:`itertools` on it.

Here is a snippet which reports only the first 10 errors:

.. code-block:: python3

    # ... code from above ...

    import itertools

    for error in itertools.islice(
            aas_verification.verify(environment),
            10
    ):
        print(f"{error.path}: {error.cause}")


Omitted Constraints
===================

Not all constraints specified in the meta-model can be verified.
Some constraints require external dependencies such as an AAS registry.
Verifying the constraints with external dependencies is out-of-scope of our SDK, as we still lack standardized interfaces to those dependencies.

However, all the constraints which need no external dependency are verified.
For a full list of exception, please see the description of the module :py:mod:`aas_core3.types`.
