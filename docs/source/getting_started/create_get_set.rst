**********************************************
Create, Get and Set Properties of an AAS Model
**********************************************

The module :py:mod:`aas_core3.types` contains all the data types of the meta-model.
This includes enumerations, abstract and concrete classes.

The module :py:mod:`aas_core3.types` also contains visitors and transformers, but we will write more about them in :ref:`iterate_and_transform` section.

Creation
========

We use constructors to create an AAS model.

Usually you start bottom-up, all the way up to the :py:class:`aas_core3.types.Environment`.

Getting and Setting Properties
==============================

All properties of the classes are modeled as Python properties.

After initialization of a class, you can directly get and modify its properties.

Getters with a Default Value
============================

For optional properties which come with a default value, we provide special getters, ``{property name}_or_default``.
If the property is ``None``, this getter will give you the default value.
Otherwise, if the property is set, the actual value of the property will be returned.

For example, see :py:meth:`aas_core3.types.HasKind.kind_or_default`.

Example: Create an Environment with a Submodel
==============================================

Here is a very rudimentary example where we show how to create an environment which contains a submodel.

The submodel will contain two elements, a property and a blob.

.. doctest::

    import aas_core3.types as aas_types

    # Create the first element
    some_element = aas_types.Property(
        id_short="some_property",
        value_type=aas_types.DataTypeDefXSD.INT,
        value="1984"
    )

    # Create the second element
    another_element = aas_types.Blob(
        id_short="some_blob",
        content_type="application/octet-stream",
        value=b'\xDE\xAD\xBE\xEF'
    )

    # You can directly access the element properties.
    another_element.value = b'\xDE\xAD\xC0\xDE'

    # Nest the elements in a submodel
    submodel = aas_types.Submodel(
        id="some-unique-global-identifier",
        submodel_elements=[
            some_element,
            another_element
        ]
    )

    # Now create the environment to wrap it all up
    environment = aas_types.Environment(
        submodels=[submodel]
    )

    # You can access the propreties from the children as well.
    environment.submodels[0].submodel_elements[1].value = b'\xC0\x01\xCA\xFE'

    # Now you can do something with the environment...
