*********************
JSON De/serialization
*********************

Our SDK handles the de/serialization of the AAS models from and to JSON format through the module :py:mod:`aas_core3.jsonization`.

Serialize
=========

To serialize, you call the function :py:func:`aas_core3.jsonization.to_jsonable` on an instance of :py:class:`aas_core3.types.Environment` which will convert it to a JSON-able mapping.

Here is a snippet that converts the environment first into a JSON-able mapping, and next converts the JSON-able mapping to text:

.. testcode::

    import json

    import aas_core3.types as aas_types
    import aas_core3.jsonization as aas_jsonization

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

    # Serialize to a JSON-able mapping
    jsonable = aas_jsonization.to_jsonable(environment)

    # Print the mapping as text
    print(json.dumps(jsonable, indent=2))

Expected output:

.. testoutput::

    {
      "submodels": [
        {
          "id": "some-unique-global-identifier",
          "submodelElements": [
            {
              "idShort": "some_property",
              "valueType": "xs:int",
              "value": "1984",
              "modelType": "Property"
            }
          ],
          "modelType": "Submodel"
        }
      ]
    }

De-serialize
============

Our SDK can convert a JSON-able mapping back to an instance of :py:class:`aas_core3.types.Environment`.
To that end, you call the function :py:func:`aas_core3.jsonization.environment_from_jsonable`.


Here is an example snippet:

.. testcode::

    import json

    import aas_core3.jsonization as aas_jsonization

    text = """\
        {
          "submodels": [
            {
              "id": "some-unique-global-identifier",
              "submodelElements": [
                {
                  "idShort": "someProperty",
                  "valueType": "xs:boolean",
                  "modelType": "Property"
                }
              ],
              "modelType": "Submodel"
            }
          ]
        }"""

    jsonable = json.loads(text)

    environment = aas_jsonization.environment_from_jsonable(
        jsonable
    )

    for something in environment.descend():
        print(type(something))

Expected output:

.. testoutput::

    <class 'aas_core3.types.Submodel'>
    <class 'aas_core3.types.Property'>

Errors
======

If there are any errors during the de-serialization, an :py:class:`aas_core3.jsonization.DeserializationException` will be thrown.
Errors occur whenever we encounter invalid JSON values.
For example, this is the case when the de-serialization function expects a JSON object, but encounters a JSON array instead.
