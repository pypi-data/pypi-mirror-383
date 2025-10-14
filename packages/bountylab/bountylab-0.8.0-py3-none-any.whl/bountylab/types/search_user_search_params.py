# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SearchUserSearchParams",
    "Filters",
    "FiltersUnionMember0",
    "FiltersUnionMember1",
    "FiltersUnionMember2",
    "FiltersUnionMember3",
    "FiltersUnionMember4",
    "FiltersUnionMember5",
    "FiltersUnionMember6",
    "FiltersUnionMember7",
    "FiltersUnionMember8",
    "FiltersUnionMember9",
    "FiltersUnionMember10",
    "FiltersUnionMember11",
    "FiltersUnionMember12",
    "FiltersUnionMember13",
    "FiltersUnionMember14",
    "FiltersUnionMember15",
    "FiltersUnionMember16",
    "FiltersUnionMember17",
    "FiltersUnionMember18",
    "FiltersUnionMember19",
    "FiltersUnionMember20",
    "FiltersUnionMember21",
    "FiltersUnionMember22",
    "FiltersUnionMember23",
    "FiltersUnionMember24",
    "FiltersUnionMember25",
    "FiltersUnionMember26",
    "FiltersUnionMember27",
    "FiltersUnionMember28",
    "FiltersUnionMember29",
    "FiltersUnionMember30",
    "FiltersUnionMember31",
    "FiltersUnionMember32",
    "FiltersUnionMember33",
    "FiltersUnionMember34",
    "FiltersUnionMember35",
    "FiltersUnionMember36",
    "FiltersUnionMember37",
    "FiltersUnionMember38",
    "FiltersUnionMember39",
    "FiltersUnionMember40",
    "FiltersUnionMember41",
    "FiltersUnionMember42",
    "FiltersUnionMember43",
    "FiltersUnionMember44",
    "FiltersUnionMember45",
    "FiltersUnionMember46",
    "FiltersUnionMember47",
    "FiltersUnionMember48",
    "FiltersUnionMember49",
    "FiltersUnionMember50",
    "FiltersUnionMember51",
    "FiltersUnionMember52",
    "FiltersUnionMember53",
    "FiltersUnionMember54",
    "FiltersUnionMember55",
    "FiltersUnionMember56",
    "FiltersUnionMember57",
    "FiltersUnionMember58",
    "FiltersUnionMember59",
    "FiltersUnionMember60",
    "FiltersUnionMember61",
    "FiltersUnionMember62",
    "FiltersUnionMember63",
    "FiltersUnionMember64",
    "FiltersUnionMember65",
    "FiltersUnionMember66",
    "FiltersUnionMember67",
    "FiltersUnionMember68",
    "FiltersUnionMember69",
    "FiltersUnionMember70",
    "FiltersUnionMember71",
    "FiltersUnionMember72",
    "FiltersUnionMember73",
    "FiltersUnionMember74",
    "FiltersUnionMember75",
    "FiltersUnionMember76",
    "FiltersUnionMember77",
    "FiltersUnionMember78",
    "FiltersUnionMember79",
    "FiltersUnionMember80",
    "FiltersUnionMember81",
    "FiltersUnionMember82",
    "FiltersUnionMember83",
    "FiltersUnionMember84",
    "FiltersUnionMember85",
    "FiltersUnionMember86",
    "FiltersUnionMember87",
    "FiltersUnionMember88",
    "FiltersUnionMember89",
    "FiltersUnionMember90",
    "FiltersUnionMember91",
    "FiltersUnionMember92",
    "FiltersUnionMember93",
    "FiltersUnionMember94",
    "FiltersUnionMember95",
    "FiltersUnionMember96",
    "FiltersUnionMember97",
    "FiltersUnionMember98",
    "FiltersUnionMember99",
    "FiltersUnionMember100",
    "FiltersUnionMember101",
    "FiltersUnionMember102",
    "FiltersUnionMember103",
    "FiltersUnionMember104",
    "FiltersUnionMember105",
    "FiltersUnionMember106",
    "FiltersUnionMember107",
    "FiltersUnionMember108",
    "FiltersUnionMember109",
    "FiltersUnionMember110",
    "FiltersUserCompositeFilter",
    "FiltersUserCompositeFilterFilter",
    "FiltersUserCompositeFilterFilterUnionMember0",
    "FiltersUserCompositeFilterFilterUnionMember1",
    "FiltersUserCompositeFilterFilterUnionMember2",
    "FiltersUserCompositeFilterFilterUnionMember3",
    "FiltersUserCompositeFilterFilterUnionMember4",
    "FiltersUserCompositeFilterFilterUnionMember5",
    "FiltersUserCompositeFilterFilterUnionMember6",
    "FiltersUserCompositeFilterFilterUnionMember7",
    "FiltersUserCompositeFilterFilterUnionMember8",
    "FiltersUserCompositeFilterFilterUnionMember9",
    "FiltersUserCompositeFilterFilterUnionMember10",
    "FiltersUserCompositeFilterFilterUnionMember11",
    "FiltersUserCompositeFilterFilterUnionMember12",
    "FiltersUserCompositeFilterFilterUnionMember13",
    "FiltersUserCompositeFilterFilterUnionMember14",
    "FiltersUserCompositeFilterFilterUnionMember15",
    "FiltersUserCompositeFilterFilterUnionMember16",
    "FiltersUserCompositeFilterFilterUnionMember17",
    "FiltersUserCompositeFilterFilterUnionMember18",
    "FiltersUserCompositeFilterFilterUnionMember19",
    "FiltersUserCompositeFilterFilterUnionMember20",
    "FiltersUserCompositeFilterFilterUnionMember21",
    "FiltersUserCompositeFilterFilterUnionMember22",
    "FiltersUserCompositeFilterFilterUnionMember23",
    "FiltersUserCompositeFilterFilterUnionMember24",
    "FiltersUserCompositeFilterFilterUnionMember25",
    "FiltersUserCompositeFilterFilterUnionMember26",
    "FiltersUserCompositeFilterFilterUnionMember27",
    "FiltersUserCompositeFilterFilterUnionMember28",
    "FiltersUserCompositeFilterFilterUnionMember29",
    "FiltersUserCompositeFilterFilterUnionMember30",
    "FiltersUserCompositeFilterFilterUnionMember31",
    "FiltersUserCompositeFilterFilterUnionMember32",
    "FiltersUserCompositeFilterFilterUnionMember33",
    "FiltersUserCompositeFilterFilterUnionMember34",
    "FiltersUserCompositeFilterFilterUnionMember35",
    "FiltersUserCompositeFilterFilterUnionMember36",
    "FiltersUserCompositeFilterFilterUnionMember37",
    "FiltersUserCompositeFilterFilterUnionMember38",
    "FiltersUserCompositeFilterFilterUnionMember39",
    "FiltersUserCompositeFilterFilterUnionMember40",
    "FiltersUserCompositeFilterFilterUnionMember41",
    "FiltersUserCompositeFilterFilterUnionMember42",
    "FiltersUserCompositeFilterFilterUnionMember43",
    "FiltersUserCompositeFilterFilterUnionMember44",
    "FiltersUserCompositeFilterFilterUnionMember45",
    "FiltersUserCompositeFilterFilterUnionMember46",
    "FiltersUserCompositeFilterFilterUnionMember47",
    "FiltersUserCompositeFilterFilterUnionMember48",
    "FiltersUserCompositeFilterFilterUnionMember49",
    "FiltersUserCompositeFilterFilterUnionMember50",
    "FiltersUserCompositeFilterFilterUnionMember51",
    "FiltersUserCompositeFilterFilterUnionMember52",
    "FiltersUserCompositeFilterFilterUnionMember53",
    "FiltersUserCompositeFilterFilterUnionMember54",
    "FiltersUserCompositeFilterFilterUnionMember55",
    "FiltersUserCompositeFilterFilterUnionMember56",
    "FiltersUserCompositeFilterFilterUnionMember57",
    "FiltersUserCompositeFilterFilterUnionMember58",
    "FiltersUserCompositeFilterFilterUnionMember59",
    "FiltersUserCompositeFilterFilterUnionMember60",
    "FiltersUserCompositeFilterFilterUnionMember61",
    "FiltersUserCompositeFilterFilterUnionMember62",
    "FiltersUserCompositeFilterFilterUnionMember63",
    "FiltersUserCompositeFilterFilterUnionMember64",
    "FiltersUserCompositeFilterFilterUnionMember65",
    "FiltersUserCompositeFilterFilterUnionMember66",
    "FiltersUserCompositeFilterFilterUnionMember67",
    "FiltersUserCompositeFilterFilterUnionMember68",
    "FiltersUserCompositeFilterFilterUnionMember69",
    "FiltersUserCompositeFilterFilterUnionMember70",
    "FiltersUserCompositeFilterFilterUnionMember71",
    "FiltersUserCompositeFilterFilterUnionMember72",
    "FiltersUserCompositeFilterFilterUnionMember73",
    "FiltersUserCompositeFilterFilterUnionMember74",
    "FiltersUserCompositeFilterFilterUnionMember75",
    "FiltersUserCompositeFilterFilterUnionMember76",
    "FiltersUserCompositeFilterFilterUnionMember77",
    "FiltersUserCompositeFilterFilterUnionMember78",
    "FiltersUserCompositeFilterFilterUnionMember79",
    "FiltersUserCompositeFilterFilterUnionMember80",
    "FiltersUserCompositeFilterFilterUnionMember81",
    "FiltersUserCompositeFilterFilterUnionMember82",
    "FiltersUserCompositeFilterFilterUnionMember83",
    "FiltersUserCompositeFilterFilterUnionMember84",
    "FiltersUserCompositeFilterFilterUnionMember85",
    "FiltersUserCompositeFilterFilterUnionMember86",
    "FiltersUserCompositeFilterFilterUnionMember87",
    "FiltersUserCompositeFilterFilterUnionMember88",
    "FiltersUserCompositeFilterFilterUnionMember89",
    "FiltersUserCompositeFilterFilterUnionMember90",
    "FiltersUserCompositeFilterFilterUnionMember91",
    "FiltersUserCompositeFilterFilterUnionMember92",
    "FiltersUserCompositeFilterFilterUnionMember93",
    "FiltersUserCompositeFilterFilterUnionMember94",
    "FiltersUserCompositeFilterFilterUnionMember95",
    "FiltersUserCompositeFilterFilterUnionMember96",
    "FiltersUserCompositeFilterFilterUnionMember97",
    "FiltersUserCompositeFilterFilterUnionMember98",
    "FiltersUserCompositeFilterFilterUnionMember99",
    "FiltersUserCompositeFilterFilterUnionMember100",
    "FiltersUserCompositeFilterFilterUnionMember101",
    "FiltersUserCompositeFilterFilterUnionMember102",
    "FiltersUserCompositeFilterFilterUnionMember103",
    "FiltersUserCompositeFilterFilterUnionMember104",
    "FiltersUserCompositeFilterFilterUnionMember105",
    "FiltersUserCompositeFilterFilterUnionMember106",
    "FiltersUserCompositeFilterFilterUnionMember107",
    "FiltersUserCompositeFilterFilterUnionMember108",
    "FiltersUserCompositeFilterFilterUnionMember109",
    "FiltersUserCompositeFilterFilterUnionMember110",
]


class SearchUserSearchParams(TypedDict, total=False):
    query: Required[str]
    """Full-text search query across user fields.

    Searches: login, displayName, bio, company, location, emails, resolvedCountry,
    resolvedState, resolvedCity (with login weighted 2x)
    """

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: githubId, login, company, location, emails,
    resolvedCountry, resolvedState, resolvedCity.

    Full-text searchable fields (automatically searched): login, displayName, bio,
    company, location, emails, resolvedCountry, resolvedState, resolvedCity.

    Filter structure:

    - Field filters: { field: "fieldName", op: "Eq"|"In", value: string|string[] }
    - Composite filters: { op: "And"|"Or", filters: [...] }

    Supported operators:

    - String fields: Eq (exact match), In (one of array)
    - Use And/Or to combine multiple filters
    """

    max_results: Annotated[int, PropertyInfo(alias="maxResults")]
    """Maximum number of results to return (default: 100, max: 1000)"""


class FiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember1(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember2(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember3(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember4(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember5(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember6(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember7(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember8(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember9(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember10(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember11(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember12(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember13(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember14(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember15(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember16(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember17(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember18(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember19(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember20(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember21(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember22(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember23(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember24(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember25(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember26(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUnionMember27(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember28(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember29(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember30(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember31(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember32(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember33(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember34(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember35(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember36(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember37(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember38(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember39(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember40(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUnionMember41(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember42(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember43(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember44(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember45(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember46(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember47(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember48(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember49(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember50(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember51(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember52(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember53(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember54(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUnionMember55(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember56(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember57(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember58(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember59(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember60(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember61(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember62(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember63(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember64(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember65(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember66(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember67(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember68(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUnionMember69(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember70(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember71(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember72(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember73(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember74(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember75(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember76(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember77(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember78(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember79(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember80(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember81(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember82(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUnionMember83(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember84(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember85(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember86(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember87(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember88(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember89(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember90(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember91(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember92(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember93(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember94(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember95(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember96(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUnionMember97(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember98(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember99(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember100(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember101(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember102(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember103(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember104(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember105(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember106(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember107(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember108(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember109(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember110(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember1(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember2(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember3(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember4(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember5(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember6(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember7(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember8(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember9(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember10(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember11(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember12(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember13(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember14(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember15(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember16(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember17(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember18(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember19(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember20(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember21(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember22(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember23(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember24(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember25(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember26(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember27(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember28(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember29(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember30(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember31(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember32(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember33(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember34(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember35(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember36(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember37(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember38(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember39(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember40(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember41(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember42(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember43(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember44(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember45(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember46(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember47(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember48(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember49(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember50(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember51(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember52(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember53(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember54(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember55(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember56(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember57(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember58(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember59(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember60(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember61(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember62(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember63(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember64(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember65(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember66(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember67(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember68(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember69(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember70(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember71(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember72(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember73(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember74(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember75(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember76(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember77(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember78(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember79(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember80(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember81(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember82(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember83(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember84(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember85(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember86(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember87(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember88(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember89(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember90(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember91(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember92(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember93(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember94(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember95(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember96(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember97(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember98(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember99(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember100(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember101(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember102(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember103(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember104(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember105(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember106(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember107(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember108(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember109(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember110(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


FiltersUserCompositeFilterFilter: TypeAlias = Union[
    FiltersUserCompositeFilterFilterUnionMember0,
    FiltersUserCompositeFilterFilterUnionMember1,
    FiltersUserCompositeFilterFilterUnionMember2,
    FiltersUserCompositeFilterFilterUnionMember3,
    FiltersUserCompositeFilterFilterUnionMember4,
    FiltersUserCompositeFilterFilterUnionMember5,
    FiltersUserCompositeFilterFilterUnionMember6,
    FiltersUserCompositeFilterFilterUnionMember7,
    FiltersUserCompositeFilterFilterUnionMember8,
    FiltersUserCompositeFilterFilterUnionMember9,
    FiltersUserCompositeFilterFilterUnionMember10,
    FiltersUserCompositeFilterFilterUnionMember11,
    FiltersUserCompositeFilterFilterUnionMember12,
    FiltersUserCompositeFilterFilterUnionMember13,
    FiltersUserCompositeFilterFilterUnionMember14,
    FiltersUserCompositeFilterFilterUnionMember15,
    FiltersUserCompositeFilterFilterUnionMember16,
    FiltersUserCompositeFilterFilterUnionMember17,
    FiltersUserCompositeFilterFilterUnionMember18,
    FiltersUserCompositeFilterFilterUnionMember19,
    FiltersUserCompositeFilterFilterUnionMember20,
    FiltersUserCompositeFilterFilterUnionMember21,
    FiltersUserCompositeFilterFilterUnionMember22,
    FiltersUserCompositeFilterFilterUnionMember23,
    FiltersUserCompositeFilterFilterUnionMember24,
    FiltersUserCompositeFilterFilterUnionMember25,
    FiltersUserCompositeFilterFilterUnionMember26,
    FiltersUserCompositeFilterFilterUnionMember27,
    FiltersUserCompositeFilterFilterUnionMember28,
    FiltersUserCompositeFilterFilterUnionMember29,
    FiltersUserCompositeFilterFilterUnionMember30,
    FiltersUserCompositeFilterFilterUnionMember31,
    FiltersUserCompositeFilterFilterUnionMember32,
    FiltersUserCompositeFilterFilterUnionMember33,
    FiltersUserCompositeFilterFilterUnionMember34,
    FiltersUserCompositeFilterFilterUnionMember35,
    FiltersUserCompositeFilterFilterUnionMember36,
    FiltersUserCompositeFilterFilterUnionMember37,
    FiltersUserCompositeFilterFilterUnionMember38,
    FiltersUserCompositeFilterFilterUnionMember39,
    FiltersUserCompositeFilterFilterUnionMember40,
    FiltersUserCompositeFilterFilterUnionMember41,
    FiltersUserCompositeFilterFilterUnionMember42,
    FiltersUserCompositeFilterFilterUnionMember43,
    FiltersUserCompositeFilterFilterUnionMember44,
    FiltersUserCompositeFilterFilterUnionMember45,
    FiltersUserCompositeFilterFilterUnionMember46,
    FiltersUserCompositeFilterFilterUnionMember47,
    FiltersUserCompositeFilterFilterUnionMember48,
    FiltersUserCompositeFilterFilterUnionMember49,
    FiltersUserCompositeFilterFilterUnionMember50,
    FiltersUserCompositeFilterFilterUnionMember51,
    FiltersUserCompositeFilterFilterUnionMember52,
    FiltersUserCompositeFilterFilterUnionMember53,
    FiltersUserCompositeFilterFilterUnionMember54,
    FiltersUserCompositeFilterFilterUnionMember55,
    FiltersUserCompositeFilterFilterUnionMember56,
    FiltersUserCompositeFilterFilterUnionMember57,
    FiltersUserCompositeFilterFilterUnionMember58,
    FiltersUserCompositeFilterFilterUnionMember59,
    FiltersUserCompositeFilterFilterUnionMember60,
    FiltersUserCompositeFilterFilterUnionMember61,
    FiltersUserCompositeFilterFilterUnionMember62,
    FiltersUserCompositeFilterFilterUnionMember63,
    FiltersUserCompositeFilterFilterUnionMember64,
    FiltersUserCompositeFilterFilterUnionMember65,
    FiltersUserCompositeFilterFilterUnionMember66,
    FiltersUserCompositeFilterFilterUnionMember67,
    FiltersUserCompositeFilterFilterUnionMember68,
    FiltersUserCompositeFilterFilterUnionMember69,
    FiltersUserCompositeFilterFilterUnionMember70,
    FiltersUserCompositeFilterFilterUnionMember71,
    FiltersUserCompositeFilterFilterUnionMember72,
    FiltersUserCompositeFilterFilterUnionMember73,
    FiltersUserCompositeFilterFilterUnionMember74,
    FiltersUserCompositeFilterFilterUnionMember75,
    FiltersUserCompositeFilterFilterUnionMember76,
    FiltersUserCompositeFilterFilterUnionMember77,
    FiltersUserCompositeFilterFilterUnionMember78,
    FiltersUserCompositeFilterFilterUnionMember79,
    FiltersUserCompositeFilterFilterUnionMember80,
    FiltersUserCompositeFilterFilterUnionMember81,
    FiltersUserCompositeFilterFilterUnionMember82,
    FiltersUserCompositeFilterFilterUnionMember83,
    FiltersUserCompositeFilterFilterUnionMember84,
    FiltersUserCompositeFilterFilterUnionMember85,
    FiltersUserCompositeFilterFilterUnionMember86,
    FiltersUserCompositeFilterFilterUnionMember87,
    FiltersUserCompositeFilterFilterUnionMember88,
    FiltersUserCompositeFilterFilterUnionMember89,
    FiltersUserCompositeFilterFilterUnionMember90,
    FiltersUserCompositeFilterFilterUnionMember91,
    FiltersUserCompositeFilterFilterUnionMember92,
    FiltersUserCompositeFilterFilterUnionMember93,
    FiltersUserCompositeFilterFilterUnionMember94,
    FiltersUserCompositeFilterFilterUnionMember95,
    FiltersUserCompositeFilterFilterUnionMember96,
    FiltersUserCompositeFilterFilterUnionMember97,
    FiltersUserCompositeFilterFilterUnionMember98,
    FiltersUserCompositeFilterFilterUnionMember99,
    FiltersUserCompositeFilterFilterUnionMember100,
    FiltersUserCompositeFilterFilterUnionMember101,
    FiltersUserCompositeFilterFilterUnionMember102,
    FiltersUserCompositeFilterFilterUnionMember103,
    FiltersUserCompositeFilterFilterUnionMember104,
    FiltersUserCompositeFilterFilterUnionMember105,
    FiltersUserCompositeFilterFilterUnionMember106,
    FiltersUserCompositeFilterFilterUnionMember107,
    FiltersUserCompositeFilterFilterUnionMember108,
    FiltersUserCompositeFilterFilterUnionMember109,
    FiltersUserCompositeFilterFilterUnionMember110,
]


class FiltersUserCompositeFilter(TypedDict, total=False):
    filters: Required[Iterable[FiltersUserCompositeFilterFilter]]
    """Array of field filters to combine with the logical operator"""

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine multiple filters"""


Filters: TypeAlias = Union[
    FiltersUnionMember0,
    FiltersUnionMember1,
    FiltersUnionMember2,
    FiltersUnionMember3,
    FiltersUnionMember4,
    FiltersUnionMember5,
    FiltersUnionMember6,
    FiltersUnionMember7,
    FiltersUnionMember8,
    FiltersUnionMember9,
    FiltersUnionMember10,
    FiltersUnionMember11,
    FiltersUnionMember12,
    FiltersUnionMember13,
    FiltersUnionMember14,
    FiltersUnionMember15,
    FiltersUnionMember16,
    FiltersUnionMember17,
    FiltersUnionMember18,
    FiltersUnionMember19,
    FiltersUnionMember20,
    FiltersUnionMember21,
    FiltersUnionMember22,
    FiltersUnionMember23,
    FiltersUnionMember24,
    FiltersUnionMember25,
    FiltersUnionMember26,
    FiltersUnionMember27,
    FiltersUnionMember28,
    FiltersUnionMember29,
    FiltersUnionMember30,
    FiltersUnionMember31,
    FiltersUnionMember32,
    FiltersUnionMember33,
    FiltersUnionMember34,
    FiltersUnionMember35,
    FiltersUnionMember36,
    FiltersUnionMember37,
    FiltersUnionMember38,
    FiltersUnionMember39,
    FiltersUnionMember40,
    FiltersUnionMember41,
    FiltersUnionMember42,
    FiltersUnionMember43,
    FiltersUnionMember44,
    FiltersUnionMember45,
    FiltersUnionMember46,
    FiltersUnionMember47,
    FiltersUnionMember48,
    FiltersUnionMember49,
    FiltersUnionMember50,
    FiltersUnionMember51,
    FiltersUnionMember52,
    FiltersUnionMember53,
    FiltersUnionMember54,
    FiltersUnionMember55,
    FiltersUnionMember56,
    FiltersUnionMember57,
    FiltersUnionMember58,
    FiltersUnionMember59,
    FiltersUnionMember60,
    FiltersUnionMember61,
    FiltersUnionMember62,
    FiltersUnionMember63,
    FiltersUnionMember64,
    FiltersUnionMember65,
    FiltersUnionMember66,
    FiltersUnionMember67,
    FiltersUnionMember68,
    FiltersUnionMember69,
    FiltersUnionMember70,
    FiltersUnionMember71,
    FiltersUnionMember72,
    FiltersUnionMember73,
    FiltersUnionMember74,
    FiltersUnionMember75,
    FiltersUnionMember76,
    FiltersUnionMember77,
    FiltersUnionMember78,
    FiltersUnionMember79,
    FiltersUnionMember80,
    FiltersUnionMember81,
    FiltersUnionMember82,
    FiltersUnionMember83,
    FiltersUnionMember84,
    FiltersUnionMember85,
    FiltersUnionMember86,
    FiltersUnionMember87,
    FiltersUnionMember88,
    FiltersUnionMember89,
    FiltersUnionMember90,
    FiltersUnionMember91,
    FiltersUnionMember92,
    FiltersUnionMember93,
    FiltersUnionMember94,
    FiltersUnionMember95,
    FiltersUnionMember96,
    FiltersUnionMember97,
    FiltersUnionMember98,
    FiltersUnionMember99,
    FiltersUnionMember100,
    FiltersUnionMember101,
    FiltersUnionMember102,
    FiltersUnionMember103,
    FiltersUnionMember104,
    FiltersUnionMember105,
    FiltersUnionMember106,
    FiltersUnionMember107,
    FiltersUnionMember108,
    FiltersUnionMember109,
    FiltersUnionMember110,
    FiltersUserCompositeFilter,
]
