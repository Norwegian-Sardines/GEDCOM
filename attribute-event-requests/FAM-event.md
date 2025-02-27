# Family Events

This document tracks the set of Family Events, both those in FamilySearch GEDCOM 7 and those considered for future addition.
Guides for using this document can be found in the associated [README.md](README.md).

# Table

| G7 Tag | Since | Name | Notes |
|:------:|-------|------|-------|
| `ANUL` | 4.0 | [Annulment](#annulment) |  |
| `CENS` | 3.0 | [Census](#census) |  |
|   | Proposed | [Child Recognition](#child-recognition) |  |
| \* | Proposed | [Common Law Marriage](#common-law-marriage) | see `MARR.TYPE` definition |
| `DIV` | 3.0 | [Divorce](#divorce) |  |
| `DIVF` | 4.0 | [Divore Filed](#divore-filed) |  |
| `ENGA` | 4.0 | [Engagement](#engagement) |  |
| `MARR` | 3.0 | [Marriage](#marriage) |  |
| `MARB` | 4.0 | [Marriage Bann](#marriage-bann) | Is this similar to engagement announcement. |
| `MARL` | 4.0 | [Marriage License](#marriage-license) |  |
| `MARS` | 4.0 | [Marriage Settlement](#marriage-settlement) |  |
# Details
--------------------------
## Annulment
### Description
Declaring a marriage void from the beginning (never existed).

### Value


### Absence


### Used
*In [GEDCOM X](https://github.com/FamilySearch/gedcomx/blob/master/specifications/event-types-specification.md)* with URI `http://gedcomx.org/Annulment`

--------------------------
## Census
### Description
Periodic count of the population for a designated locality, such as a national or state census.

### Value


### Absence


### Used
*In [GEDCOM X](https://github.com/FamilySearch/gedcomx/blob/master/specifications/event-types-specification.md)* with `URI http://gedcomx.org/Census`

--------------------------
## Child Recognition
### Description
A legal action which grants a parent-child relationship between a child and a parent; often as part of legitimizing a step-parent relationship or as legal recognition of a biological relationship that was not recognized at the time of birth.

### Value
Found in the following historical records

- As "reconnaissance d'enfant" in legal registries in France
- As "Legitimation" in legal registries in Germany

### Absence
The most closely related structures are:

- `ADOP`: both events establish a legal parent relationship after birth. In some countries they are the same as one another; in other countries they have different criteria and/or legal ramifications.

### Used
Applications using this structure have not yet been identified.

--------------------------
## Common Law Marriage
### Description
*proposed description missing*

*In [GEDCOM X](https://github.com/FamilySearch/gedcomx/blob/master/specifications/fact-types-specification.md) as* "The fact of a marriage by common law."

### Value
Found in the following historical records:

- (records not yet identified)

### Absence
The most closely related structures are:

- `MARR`: can express a marriage of any type, potentially including common law marriages. Common law marriages can differ from other marriages, however, in that they may lack a ceremony or event marking the entrance into the married state.

```
1 MARR
2 TYPE Common Law
```

Related proposals include

- Lived Together (in the Family Attributes document): some interpretations of common law marriage and cohabitation are very similar to one another

### Used
- Part of the [GEDCOM X specification](https://github.com/FamilySearch/gedcomx/blob/master/specifications/fact-types-specification.md) with URI `http://gedcomx.org/CommonLawMarriage`
- Used by the [FamilySearch API](https://www.familysearch.org/developers/docs/guides/facts) via GEDCOM X.

--------------------------
## Divorce
### Description
Dissolving a marriage through civil action.

### Value


### Absence


### Used
*In [GEDCOM X](https://github.com/FamilySearch/gedcomx/blob/master/specifications/fact-types-specification.md)* with URI `http://gedcomx.org/Divorce`

--------------------------
## Divore Filed
### Description
Filing for a divorce by a spouse.

### Value


### Absence


### Used


--------------------------
## Engagement
### Description
Recording or announcing an agreement between 2 people to become married.

### Value


### Absence


### Used


--------------------------
## Marriage
### Description
A legal, common-law, or customary event such as a wedding or marriage ceremony that joins 2 partners to create or extend a family unit.

### Value


### Absence


### Used
- *In [GEDCOM X](https://github.com/FamilySearch/gedcomx/blob/master/specifications/fact-types-specification.md)* with URI `http://gedcomx.org/Marriage`

--------------------------
## Marriage Bann
### Description
Official public notice given that 2 people intend to marry.

### Value


### Absence


### Used


--------------------------
## Marriage License
### Description
Obtaining a legal license to marry.

### Value


### Absence


### Used


--------------------------
## Marriage Settlement
### Description
Creating an agreement between 2 people contemplating marriage, at which time they agree to release or modify property rights that would otherwise arise from the marriage.

### Value


### Absence


### Used


--------------------------
