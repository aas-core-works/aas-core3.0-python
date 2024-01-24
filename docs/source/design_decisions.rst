****************
Design Decisions
****************

We explain a couple of design decisions and trade-offs we deliberately made during the development of the SDK.
These are our opinions — you may or may not agree, which is totally OK as there are always more than one way to do things and do them well.

However, the decisions elaborated here are not meant to convince you.
We want to give you insight about why we did certain things, and why we didn't implement them in some other way.

Aggregations as Lists instead of Dictionaries
=============================================
We decided to implement all the aggregations in the meta-model as `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_  instead of `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_.

Some structures just "scream" for a dictionary, such as submodel elements property in a :py:class:`aas_core3.types.Submodel`.
The submodel elements need to be unique w.r.t. their ID-shorts.
So why didn't we model them as dictionaries, where keys are ID-shorts?

There are multiple reasons:

* "There are only two hard things in Computer Science: cache invalidation and naming things" (see this `StackExchange <https://skeptics.stackexchange.com/questions/19836/has-phil-karlton-ever-said-there-are-only-two-hard-things-in-computer-science>`_).
  For example, the key in the dictionary and the ``id_short`` property of the submodel element need to be always in sync.
  Keeping such things in sync can be hard.
* When de-serializing, you need to hash on all the key/value pairs.
  In many situations, you do not perform any look-ups, but want to read the whole environment only once, and act upon it.
  Hashing would have wasted computational resources.
* You may want to index on more things than ``id_short``.
  For example, retrieving submodel elements by their ``semantic_id`` is almost equally important.
* The order of the key/value pairs in a dictionary might not follow the order in the underlying serialized file.
  For example, if ``dict`` is used, the order is random.
  This would make the round-trip de-serialization 🠒 serialization non-deterministic.
* Generating code based on dictionaries would have incurred additional complexity in aas-core-meta and aas-core-codegen as we would need to capture indexing in our machine-readable meta-models.

We therefore leave indexing (and syncing of the indices) to the user instead of pre-maturely providing a basic index on one of the features.

No Parent ⟷ Child Associations
==============================

We did not model the parent ⟷ child relations between the model elements for similar reasons why we did not implement dictionaries.
Namely, keeping the associations in sync is hard.
While you might have clear parent ⟷ child relationship when you deserialize an environment, this relationship becomes less clear when you start re-using objects between environments.

Moreover, you need to sync the parent when an instance associated as its child is deleted.
The complexity of this sync becomes hard (and computationally costly) as your object tree grows.
What if you re-assign the instance to multiple parents?

For example, an instance of :py:class:`aas_core3.types.Submodel` may appear in multiple instances of :py:class:`aas_core3.types.Environment`.
Which environment is the parent?

Multiple solutions are possible, and they depend on the application domain.
In some cases, where you deal with static data, a simple dictionary parent 🠒 child is sufficient.
In other cases, more involved data structures and updating strategies are needed.

As we did not want to prejudice the SDK for a particular application domain, we left out parent ⟷ child associations.

We indeed discussed a couple of concrete solutions, but failed to find a unifying approach which would satisfy multiple scenarios.

Values as Strings
=================

As you can see, say, in :py:class:`aas_core3.types.Property` class, the ``value`` property holds strings.
This is indeed intentional though it might seem a bit outlandish.

You have to bear in mind that the lexical space of XML basic data types, which we use to encode values in such properties, is large, and larger than Python primitive types.

For example, ``xs:double``'s can have an arbitrary prefix of zeros (``001234`` is a valid ``xs:double``).

For another example, ``xs:decimal`` allows for an arbitrary size and precision.
In Python, `decimal.Decimal <https://docs.python.org/3/library/decimal.html>`_ is probably our best bet, but we have to fix the precision up-front.
It might well be that our application domain requires later more precision than what we specified at first!

Writing code for a setting where various systems interoperate with mixed application domains is difficult.
We wanted to stick to the specification, which mandates XML basic data types, and thus leave the parsing of values up to the users.
Thus, we do not restrict the domain where our SDK can be used.
The users will know the best what precision and form they need.

No AAS Registry
===============

An AAS Registry is considered an external dependency, since it requires network requests.
We left it out-of-scope on purpose as this SDK focuses on the data exchange.
Further aas-core projects will work on an AAS registry.

One important consequence of leaving out the registry is that some constraints in the meta-model can not be enforced, as we do not know how to resolve the references.

The full list of omitted constraints is available in `the code of aas-core-meta <https://github.com/aas-core-works/aas-core-meta>`_.

No Runtime Type Guards
======================
We do not perform any runtime type-guards for performance reasons.
It would be simply too slow to check runtime types at *every* entry point in the library.
We assume that the user of the library employs `mypy <https://mypy-lang.org/>`_ and makes sure the objects passed into the library are correct.

In practice, we intentionally do not check for the following issue stemming from the unexpected types (see `issue #436 <https://github.com/aas-core-works/aas-core-codegen/issues/436>`_):

.. code-block:: python

    prop = aas_types.Property(
        id_short="Weight",
        # Note that the value here is an int and not a str!
        # Mypy would have complained.
        value=1,
        value_type=aas_types.DataTypeDefXSD.DOUBLE
    )
    print(
        json.dumps(
            aas_jsonization.to_jsonable(prop),
            indent=2
        )
    )

which outputs:

.. code-block:: javascript

    {
      "idShort": "Weight",
        "valueType": "xs:double",
        // Note that the value here is a number
        // and not a string — we did not check that
        // the runtime types are correct, and the `json`
        // module simply converted it to a number!
      "value": 1,
      "modelType": "Property"
    }
