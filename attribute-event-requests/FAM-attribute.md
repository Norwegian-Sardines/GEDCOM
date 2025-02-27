# Family Attributes

This document tracks the set of Family Attributes, both those in FamilySearch GEDCOM 7 and those considered for future addition.
Guides for using this document can be found in the associated [README.md](README.md).

# Table

| G7 Tag | Since | Name | Notes |
|:------:|-------|------|-------|
| \* | 5.0 | [Childless](#childless) | encoded as `NCHI 0` |
| \* | Proposed | [Lived Together](#lived-together) | perhaps `RESI` |
| `NCHI` | 5.0 | [Number of Children](#number-of-children) |  |
| `RESI` | 3.0 | [Residence](#residence) |  |
# Details
--------------------------
## Childless
### Description
The assertion that a family does not have children can be made using the `NCHI` structure with payload "`0`".
This is distinct from simply not having any `CHIL` structures,
which might mean there are children that have not yet been added to the data.

### Value


### Absence
encoded as `NCHI 0`

### Used
- Part of the [GEDCOM X specification](https://github.com/FamilySearch/gedcomx/blob/master/specifications/fact-types-specification.md) as a distinct structure with URI `http://familysearch.org/v1/CoupleNeverHadChildren`

--------------------------
## Lived Together
### Description
*proposed description missing*

*In [FamilySearch API documentation](https://www.familysearch.org/developers/docs/guides/facts)* without a definition

### Value
Found in the following historical records:

- (records not yet identified)

### Absence
The most closely related structures are:

- `FAM`.`RESI`: provides the place of residence for the couple, which generally implies they lived together. However, "lived together" is sometimes used as a euphemism for "acted as a couple without a preceding marriage ceremony," which is only indirectly implied by the presence of a `FAM`.`RESI`.
- `MARR`: some interpretations of living together as a couple and some definitions of marriage make living together a type of marriage; other definitions do not.

Related proposals include

- Common Law Marriage (in the Family Events document): some interpretations of common law marriage and cohabitation are very similar to one another

### Used
- Used by the [FamilySearch API](https://www.familysearch.org/developers/docs/guides/facts) with URI `http://familysearch.org/v1/LivedTogether`

--------------------------
## Number of Children
### Description


### Value


### Absence


### Used


--------------------------
## Residence
### Description
An address or place of residence where an individual resided.

### Value


### Absence


### Used


--------------------------
