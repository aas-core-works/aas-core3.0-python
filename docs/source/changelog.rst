**********
Change Log
**********

1.0.4 (2024-04-16)
==================
The ``dataSpecification`` field in ``EmbeddedDataSpecification`` is made
optional, according to the book.

1.0.3 (2024-03-22)
==================
* Update to aas-core-meta, codegen, testgen cb28d18, c414f32, 6ff39c260 (#23)

  We propagate the fix from abnf-to-regex related to maximum qualifiers
  which had been mistakenly represented as exact repetition before.

1.0.2 (2024-03-13)
==================
* Update to aas-core-meta, codegen, testgen 79314c6, 94399e1, e1087880 (#20)

  This patch release brings about the fix for patterns concerning dates and
  date-times with zone offset `14:00` which previously allowed for
  a concatenation without a plus sign.

1.0.1 (2024-02-14)
==================
* Test and fix for text attached to end XML elements (#18).

  This patch fixes for the edge case where ElementTree's
  ```XMLPullParser`` attaches the text to the end element instead of
  the start element. Previously, some XML files were wrongly reported
  as incorrect.

  We do not know what causes this different behavior of the parser,
  but suspect that it has something to do with the size of the parser's
  buffer.

1.0.0 (2024-02-02)
==================
This is the first stable release. The release candidates stood
the test of time, so we are now confident to publish a stable
version.

1.0.0rc3 (2023-09-08)
=====================
* Update to aas-core-meta, codegen, testgen 4d7e59e, 18986a0, and
  9b43de2e (#12)

  In this version, we fix:

  * Constraints AASc-3a-010 and AASd-131, propagated from aas-core-meta
    pull requests 281 and 280, respectively.

  We also add the following minor feature:

  * Add ```__repr__`` to ```verification.Error`` to facilitate
    debugging in the downstream clients. Propagated from
    aas-core-codegen pull request 400.

1.0.0rc2 (2023-06-28)
=====================
* Update to aas-core-meta, codegen, testgen 44756fb, 607f65c,
  bf3720d7 (#7)

  * This is an important patch propagating in particular the following fixes which affected the constraints and their documentation:

    * Pull requests in aas-core-meta 271, 272 and 273 which affect the nullability checks in constraints,
    * Pull request in aas-core-meta 275 which affects the documentation of many constraints.

1.0.0rc1 (2023-03-03)
=====================
* Initial version
