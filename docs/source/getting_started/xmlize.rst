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

    <environment xmlns="https://admin-shell.io/aas/3/0"><submodels><submodel><id>some-unique-global-identifier</id><submodelElements><property><idShort>some_property</idShort><valueType>xs:int</valueType><value>1984</value></property></submodelElements></submodel></submodels></environment>


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

Disregarding XML Attributes
===========================
The specification mandates to use no XML attributes, but some libraries and tools still add their own XML attributes in the XML serialization of an AAS.
You need to remove them to avoid de-serialization errors.

To that end, you need to operate directly on an iterator of XML events and elements coming from :py:func:`xml.etree.ElementTree.iterparse`.
The attributes need to be cleared as you iterate and re-yield over the iterator.

Here is an example snippet:

.. testcode::

    import io
    import xml.etree.ElementTree
    from typing import Tuple, Iterator

    import aas_core3.xmlization as aas_xmlization

    text = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<environment\n'
        '    xmlns="https://admin-shell.io/aas/3/0"\n'
        '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '    xsi:schemaLocation="https://admin-shell.io/aas/3/0/AAS.xsd">\n'
        '</environment>\n'
    )

    iterator = xml.etree.ElementTree.iterparse(
        io.StringIO(text),
        # The XML de-serializer needs to operate on 'start' and 'end' events.
        events=("start", "end")
    )

    def with_attributes_removed(
            an_iterator: Iterator[Tuple[str, xml.etree.ElementTree.Element]]
    ) -> Iterator[Tuple[str, xml.etree.ElementTree.Element]]:
        """
        Map the :paramref:`iterator` such that all attributes are removed.

        :param an_iterator: to be mapped
        :yield: event and element without attributes from :paramref:`iterator`
        """
        for event, element in an_iterator:
            element.attrib.clear()

            yield event, element

    environment = aas_xmlization.environment_from_iterparse(
        iterator=with_attributes_removed(iterator)
    )

    # The attributes are lost in the subsequent serialization.
    serialization = aas_xmlization.to_str(environment)

    assert (
        '<environment xmlns="https://admin-shell.io/aas/3/0"/>'
        == serialization
    )
