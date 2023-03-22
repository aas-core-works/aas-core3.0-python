********************
XML De/serialization
********************

The code that de/serializes AAS models from and to XML documents lives in the module :py:mod:`aas_core3.xmlization`.

Serialize
=========

You serialize the AAS model to XML-encoded text by calling the function :py:func:`aas_core3.xmlization.to_str`.

If you want the same text to be written incrementally to a :py:class:`typing.TextIO` stream, you can use the function :py:func:`aas_core3.xmlization.write`.

Here is an example snippet:

.. testcode::

    import aas_core3.types as aas_types
    import aas_core3.xmlization as aas_xmlization

    # Prepare the environment
    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id_short="someIdShort",
                id="some-unique-global-identifier",
                submodel_elements=[
                    aas_types.Property(
                        id_short = "some_property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1984"
                    )
                ]
            )
        ]
    )

    # Serialize to an XML-encoded string
    text = aas_xmlization.to_str(environment)

    print(text)

Expected output:

.. testoutput::

    <environment xmlns="https://admin-shell.io/aas/3/0"><submodels><submodel><idShort>someIdShort</idShort><id>some-unique-global-identifier</id><submodelElements><property><idShort>some_property</idShort><valueType>xs:int</valueType><value>1984</value></property></submodelElements></submodel></submodels></environment>


De-serialize
============

You can de-serialize an environment from XML coming from four different sources by using different functions:

* :py:func:`aas_core3.xmlization.environment_from_iterparse`, where a stream coming from :py:func:`xml.etree.ElementTree.iterparse` is expected with ``events`` set to ``["start", "end"]``,
* :py:func:`aas_core3.xmlization.environment_from_stream`, which expects a textual stream behaving according to :py:class:`typing.TextIO`,
* :py:func:`aas_core3.xmlization.environment_from_file`, which expects a path to the file containing the XML of the environment, or
* :py:func:`aas_core3.xmlization.environment_from_str`, which de-serialized the environment from an XML-encoded string.

Here is a snippet which parses XML as text and then de-serializes it into an instance of :py:class:`~aas_core3.types.Environment`:

.. testcode::

    import aas_core3.xmlization as aas_xmlization

    text = (
        "<environment xmlns=\"https://admin-shell.io/aas/3/0\">" +
        "<submodels><submodel>" +
        "<idShort>someIdShort</idShort>"
        "<id>some-unique-global-identifier</id>" +
        "<submodelElements><property><idShort>someProperty</idShort>" +
        "<valueType>xs:boolean</valueType></property></submodelElements>" +
        "</submodel></submodels></environment>"
    )

    environment = aas_xmlization.environment_from_str(text)

    for something in environment.descend():
        print(type(something))

Expected output:

.. testoutput::

    <class 'aas_core3.types.Submodel'>
    <class 'aas_core3.types.Property'>

Errors
======

If the XML document comes in an unexpected form, our SDK throws a :py:class:`aas_core3.xmlization.DeserializationException`.
This can happen, for example, if unexpected XML elements or XML attributes are encountered, or an expected XML element is missing.
