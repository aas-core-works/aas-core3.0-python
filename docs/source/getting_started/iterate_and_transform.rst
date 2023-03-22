.. _iterate_and_transform:

*********************
Iterate and Transform
*********************

The SDK provides various ways how you can loop through the elements of the model, and how these elements can be transformed.
Each following section will look into one of the approaches.

``over_X_or_empty``
===================

For all the optional lists, there is a corresponding ``over_{property name}_or_empty`` getter.
It gives you an :py:class:`Iterator`.
If the property is not set, this getter will yield empty.
Otherwise, it will yield from the actual property value.

For example, see :py:meth:`aas_core3.types.Environment.over_submodels_or_empty`.


``descend_once`` and ``descend``
================================

If you are writing a simple script and do not care about the performance, the SDK provides two methods in the most general interface :py:class:`aas_core3.types.Class`, :py:meth:`~aas_core3.types.Class.descend_once` and :py:meth:`~aas_core3.types.Class.descend`, which you can use to loop through the instances.

Both :py:meth:`~aas_core3.types.Class.descend_once` and :py:meth:`~aas_core3.types.Class.descend` iterate over referenced children of an instance of :py:class:`~aas_core3.types.Class`.
:py:meth:`~aas_core3.types.Class.descend_once`, as it names suggests, stops after all the children has been iterated over.
:py:meth:`~aas_core3.types.Class.descend` continues recursively to grand-children, grand-grand-children *etc.*

Here is a short example how you can get all the properties from an environment whose ID-short starts with ``another``:

.. testcode::

    import aas_core3.types as aas_types

    # Prepare the environment
    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id_short="someIdShort",
                id="some-unique-global-identifier",
                submodel_elements=[
                    aas_types.Property(
                        id_short="some_property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1984"
                    ),
                    aas_types.Property(
                        id_short="another_property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1985"
                    ),
                    aas_types.Property(
                        id_short="yet_another_property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1986"
                    )
                ]
            )
        ]
    )

    for something in environment.descend():
        if (
            isinstance(something, aas_types.Property)
            and "another" in something.id_short
        ):
            print(something.id_short)

.. testoutput::

    another_property
    yet_another_property

Iteration with :py:meth:`~aas_core3.types.Class.descend_once` and :py:meth:`~aas_core3.types.Class.descend` works well if the performance is irrelevant.
However, if the performance matters, this is not a good approach.
First, all the children will be visited (even though you need only a small subset).
Second, you need to switch with :py:func:`isinstance` on the runtime type, which grows linearly in computational cost with the number of types you switch on.

Let's see in the next section how we could use a more efficient, but also a more complex approach.

Visitor
=======

`Visitor pattern`_ is a common design pattern in software engineering.
We will not explain the details of the pattern here as you can read about in the ample literature in books or in Internet.

The cornerstone of the visitor pattern is `double dispatch`_: instead of casting to the desired type during the iteration, the method :py:meth:`aas_core3.types.Class.accept` directly dispatches to the appropriate visitation method.

.. _Visitor pattern: https://en.wikipedia.org/wiki/Visitor_pattern
.. _double dispatch: https://en.wikipedia.org/wiki/Double_dispatch

This allows us to spare runtime type switches and directly dispatch the execution.
The SDK already implements :py:meth:`~aas_core3.types.Class.accept` methods, so you only have to implement the visitor.

The visitor class has a visiting method for each class of the meta-model.
In the SDK, we provide different flavors of the visitor abstract classes which you can readily implement:

* :py:class:`~aas_core3.types.AbstractVisitor` which needs all the visit methods to be implemented,
* :py:class:`~aas_core3.types.PassThroughVisitor` which visits all the elements and does nothing, and
* :py:class:`~aas_core3.types.AbstractVisitorWithContext` which propagates a context object along the iteration.

Let us re-write the above example related to :py:meth:`~aas_core3.types.Class.descend` method with a visitor pattern:

.. testcode::

    import aas_core3.types as aas_types

    class Visitor(aas_types.PassThroughVisitor):
        def visit_property(self, that: aas_types.Property):
            if "another" in that.id_short:
                print(that.id_short)

    # Prepare the environment
    environment = aas_types.Environment(
        submodels=[
            aas_types.Submodel(
                id_short="someIdShort",
                id="some-unique-global-identifier",
                submodel_elements=[
                    aas_types.Property(
                        id_short="some_property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1984"
                    ),
                    aas_types.Property(
                        id_short="another_property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1985"
                    ),
                    aas_types.Property(
                        id_short="yet_another_property",
                        value_type=aas_types.DataTypeDefXSD.INT,
                        value="1986"
                    )
                ]
            )
        ]
    )

    # Iterate
    visitor = Visitor()
    visitor.visit(environment)

Expected output:

.. testoutput::

    another_property
    yet_another_property

There are important differences to iteration with :py:meth:`~aas_core3.types.Class.descend`:

* Due to `double dispatch`_, we spare a cast.
  This is usually more efficient.
* The iteration logic in :py:meth:`~aas_core3.types.Class.descend` lives very close to where it is executed.
  In contrast, the visitor needs to be defined as a separate class.
  While sometimes faster, writing the visitor makes the code less readable.

Descend or Visitor?
===================

In general, people familiar with the `visitor pattern`_ and object-oriented programming will prefer, obviously, visitor class.
People who like functional programming, generator expressions and ilks  will prefer :py:meth:`~aas_core3.types.Class.descend`.

It is difficult to discuss different tastes, so you should probably come up with explicit code guidelines in your code and stick to them.

Make sure you always profile before you sacrifice readability and blindly apply one or the other approach for performance reasons.

Transformer
===========

A transformer pattern is an analogous to `visitor pattern`_, where we "transform" the visited element into some other form (be it a string or a different object).
It is very common in compiler design, where the abstract syntax tree is transformed into a different representation.

The SDK provides different flavors of a transformer:

* :py:class:`~aas_core3.types.AbstractTransformer`, where the model element is directly transformed into something, and
* :py:class:`~aas_core3.types.AbstractTransformerWithContext`, which propagates the context object along the transformations.

Usually you implement for each concrete class how it should be transformed.
If you want to specify only a subset of transformations, and provide the default value for the remainder, the SDK provides :py:class:`~aas_core3.types.TransformerWithDefault` and :py:class:`~aas_core3.types.TransformerWithDefaultAndContext`.

We deliberately omit an example due to the length of the code.
Please let us know by `creating an issue <https://github.com/aas-core-works/aas-core3.0-python/issues>`__ if you would like to have an example here.
