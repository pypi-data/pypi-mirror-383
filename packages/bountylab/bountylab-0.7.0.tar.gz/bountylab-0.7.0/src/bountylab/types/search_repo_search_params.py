# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SearchRepoSearchParams",
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
    "FiltersRepoCompositeFilter",
    "FiltersRepoCompositeFilterFilter",
    "FiltersRepoCompositeFilterFilterUnionMember0",
    "FiltersRepoCompositeFilterFilterUnionMember1",
    "FiltersRepoCompositeFilterFilterUnionMember2",
    "FiltersRepoCompositeFilterFilterUnionMember3",
    "FiltersRepoCompositeFilterFilterUnionMember4",
    "FiltersRepoCompositeFilterFilterUnionMember5",
    "FiltersRepoCompositeFilterFilterUnionMember6",
    "FiltersRepoCompositeFilterFilterUnionMember7",
    "FiltersRepoCompositeFilterFilterUnionMember8",
    "FiltersRepoCompositeFilterFilterUnionMember9",
    "FiltersRepoCompositeFilterFilterUnionMember10",
    "FiltersRepoCompositeFilterFilterUnionMember11",
    "FiltersRepoCompositeFilterFilterUnionMember12",
    "FiltersRepoCompositeFilterFilterUnionMember13",
    "FiltersRepoCompositeFilterFilterUnionMember14",
    "FiltersRepoCompositeFilterFilterUnionMember15",
    "FiltersRepoCompositeFilterFilterUnionMember16",
    "FiltersRepoCompositeFilterFilterUnionMember17",
    "FiltersRepoCompositeFilterFilterUnionMember18",
    "FiltersRepoCompositeFilterFilterUnionMember19",
    "FiltersRepoCompositeFilterFilterUnionMember20",
    "FiltersRepoCompositeFilterFilterUnionMember21",
    "FiltersRepoCompositeFilterFilterUnionMember22",
    "FiltersRepoCompositeFilterFilterUnionMember23",
    "FiltersRepoCompositeFilterFilterUnionMember24",
    "FiltersRepoCompositeFilterFilterUnionMember25",
    "FiltersRepoCompositeFilterFilterUnionMember26",
    "FiltersRepoCompositeFilterFilterUnionMember27",
    "FiltersRepoCompositeFilterFilterUnionMember28",
    "FiltersRepoCompositeFilterFilterUnionMember29",
    "FiltersRepoCompositeFilterFilterUnionMember30",
    "FiltersRepoCompositeFilterFilterUnionMember31",
    "FiltersRepoCompositeFilterFilterUnionMember32",
    "FiltersRepoCompositeFilterFilterUnionMember33",
    "FiltersRepoCompositeFilterFilterUnionMember34",
    "FiltersRepoCompositeFilterFilterUnionMember35",
    "FiltersRepoCompositeFilterFilterUnionMember36",
    "FiltersRepoCompositeFilterFilterUnionMember37",
    "FiltersRepoCompositeFilterFilterUnionMember38",
    "FiltersRepoCompositeFilterFilterUnionMember39",
    "FiltersRepoCompositeFilterFilterUnionMember40",
    "FiltersRepoCompositeFilterFilterUnionMember41",
    "FiltersRepoCompositeFilterFilterUnionMember42",
    "FiltersRepoCompositeFilterFilterUnionMember43",
    "FiltersRepoCompositeFilterFilterUnionMember44",
    "FiltersRepoCompositeFilterFilterUnionMember45",
    "FiltersRepoCompositeFilterFilterUnionMember46",
    "FiltersRepoCompositeFilterFilterUnionMember47",
    "FiltersRepoCompositeFilterFilterUnionMember48",
    "FiltersRepoCompositeFilterFilterUnionMember49",
    "FiltersRepoCompositeFilterFilterUnionMember50",
    "FiltersRepoCompositeFilterFilterUnionMember51",
    "FiltersRepoCompositeFilterFilterUnionMember52",
    "FiltersRepoCompositeFilterFilterUnionMember53",
    "FiltersRepoCompositeFilterFilterUnionMember54",
    "FiltersRepoCompositeFilterFilterUnionMember55",
    "FiltersRepoCompositeFilterFilterUnionMember56",
    "FiltersRepoCompositeFilterFilterUnionMember57",
    "FiltersRepoCompositeFilterFilterUnionMember58",
    "FiltersRepoCompositeFilterFilterUnionMember59",
    "FiltersRepoCompositeFilterFilterUnionMember60",
    "FiltersRepoCompositeFilterFilterUnionMember61",
    "FiltersRepoCompositeFilterFilterUnionMember62",
    "FiltersRepoCompositeFilterFilterUnionMember63",
    "FiltersRepoCompositeFilterFilterUnionMember64",
    "FiltersRepoCompositeFilterFilterUnionMember65",
    "FiltersRepoCompositeFilterFilterUnionMember66",
    "FiltersRepoCompositeFilterFilterUnionMember67",
    "FiltersRepoCompositeFilterFilterUnionMember68",
    "FiltersRepoCompositeFilterFilterUnionMember69",
    "FiltersRepoCompositeFilterFilterUnionMember70",
    "FiltersRepoCompositeFilterFilterUnionMember71",
    "FiltersRepoCompositeFilterFilterUnionMember72",
    "FiltersRepoCompositeFilterFilterUnionMember73",
    "FiltersRepoCompositeFilterFilterUnionMember74",
    "FiltersRepoCompositeFilterFilterUnionMember75",
    "FiltersRepoCompositeFilterFilterUnionMember76",
    "FiltersRepoCompositeFilterFilterUnionMember77",
    "FiltersRepoCompositeFilterFilterUnionMember78",
    "FiltersRepoCompositeFilterFilterUnionMember79",
    "FiltersRepoCompositeFilterFilterUnionMember80",
    "FiltersRepoCompositeFilterFilterUnionMember81",
    "FiltersRepoCompositeFilterFilterUnionMember82",
    "FiltersRepoCompositeFilterFilterUnionMember83",
    "FiltersRepoCompositeFilterFilterUnionMember84",
    "FiltersRepoCompositeFilterFilterUnionMember85",
    "FiltersRepoCompositeFilterFilterUnionMember86",
    "FiltersRepoCompositeFilterFilterUnionMember87",
    "FiltersRepoCompositeFilterFilterUnionMember88",
    "FiltersRepoCompositeFilterFilterUnionMember89",
    "FiltersRepoCompositeFilterFilterUnionMember90",
    "FiltersRepoCompositeFilterFilterUnionMember91",
    "FiltersRepoCompositeFilterFilterUnionMember92",
]


class SearchRepoSearchParams(TypedDict, total=False):
    query: Required[str]
    """
    Natural language search query for semantic search across repository README and
    description using vector embeddings
    """

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: githubId, ownerLogin, name, stargazerCount, language,
    totalIssuesCount, totalIssuesOpen, totalIssuesClosed, lastContributorLocations.

    Filter structure:

    - Field filters: { field: "fieldName", op: "Eq"|"In"|"Gte"|"Lte", value:
      string|number|array }
    - Composite filters: { op: "And"|"Or", filters: [...] }

    Supported operators:

    - String fields: Eq (exact match), In (one of array)
    - Number fields: Eq (exact), In (one of array), Gte (>=), Lte (<=)
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
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember14(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember15(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember16(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember17(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember18(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember19(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember20(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember21(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember22(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember23(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember24(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember25(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember26(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember27(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember28(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember29(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember30(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember31(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember32(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember33(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember34(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember35(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember36(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember37(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember38(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember39(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember40(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersUnionMember41(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember42(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersUnionMember43(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersUnionMember44(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember45(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersUnionMember46(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember47(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember48(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersUnionMember49(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember50(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember51(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersUnionMember52(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersUnionMember53(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersUnionMember54(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersUnionMember55(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersUnionMember56(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersUnionMember57(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersUnionMember58(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersUnionMember59(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersUnionMember60(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember61(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersUnionMember62(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember63(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersUnionMember64(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersUnionMember65(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember66(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersUnionMember67(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember68(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember69(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersUnionMember70(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember71(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersUnionMember72(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersUnionMember73(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember74(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersUnionMember75(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember76(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember77(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersUnionMember78(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember79(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersUnionMember80(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersUnionMember81(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember82(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersUnionMember83(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember84(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["Contains"]]

    value: Required[str]


class FiltersUnionMember85(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["NotContains"]]

    value: Required[str]


class FiltersUnionMember86(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["ContainsAny"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember87(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["NotContainsAny"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember88(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyLt"]]

    value: Required[str]


class FiltersUnionMember89(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyLte"]]

    value: Required[str]


class FiltersUnionMember90(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyGt"]]

    value: Required[str]


class FiltersUnionMember91(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyGte"]]

    value: Required[str]


class FiltersUnionMember92(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember1(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember2(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember3(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember4(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember5(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember6(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember7(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember8(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember9(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember10(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember11(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember12(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember13(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember14(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember15(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember16(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember17(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember18(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember19(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember20(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember21(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember22(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember23(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember24(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember25(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember26(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember27(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember28(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember29(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember30(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember31(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember32(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember33(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember34(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember35(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember36(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember37(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember38(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember39(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember40(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember41(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember42(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember43(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember44(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember45(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember46(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember47(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember48(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotEq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember49(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember50(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotIn"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember51(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Lt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember52(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Lte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember53(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Gt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember54(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Gte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember55(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Glob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember56(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember57(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["IGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember58(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["NotIGlob"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember59(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Regex"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember60(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember61(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember62(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember63(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember64(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember65(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember66(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember67(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember68(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember69(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember70(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember71(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember72(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember73(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember74(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember75(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember76(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember77(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["NotEq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember78(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember79(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["NotIn"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember80(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Lt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember81(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember82(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Gt"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember83(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember84(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["Contains"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember85(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["NotContains"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember86(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["ContainsAny"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember87(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["NotContainsAny"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember88(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyLt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember89(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyLte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember90(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyGt"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember91(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["AnyGte"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember92(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["ContainsAllTokens"]]

    value: Required[str]


FiltersRepoCompositeFilterFilter: TypeAlias = Union[
    FiltersRepoCompositeFilterFilterUnionMember0,
    FiltersRepoCompositeFilterFilterUnionMember1,
    FiltersRepoCompositeFilterFilterUnionMember2,
    FiltersRepoCompositeFilterFilterUnionMember3,
    FiltersRepoCompositeFilterFilterUnionMember4,
    FiltersRepoCompositeFilterFilterUnionMember5,
    FiltersRepoCompositeFilterFilterUnionMember6,
    FiltersRepoCompositeFilterFilterUnionMember7,
    FiltersRepoCompositeFilterFilterUnionMember8,
    FiltersRepoCompositeFilterFilterUnionMember9,
    FiltersRepoCompositeFilterFilterUnionMember10,
    FiltersRepoCompositeFilterFilterUnionMember11,
    FiltersRepoCompositeFilterFilterUnionMember12,
    FiltersRepoCompositeFilterFilterUnionMember13,
    FiltersRepoCompositeFilterFilterUnionMember14,
    FiltersRepoCompositeFilterFilterUnionMember15,
    FiltersRepoCompositeFilterFilterUnionMember16,
    FiltersRepoCompositeFilterFilterUnionMember17,
    FiltersRepoCompositeFilterFilterUnionMember18,
    FiltersRepoCompositeFilterFilterUnionMember19,
    FiltersRepoCompositeFilterFilterUnionMember20,
    FiltersRepoCompositeFilterFilterUnionMember21,
    FiltersRepoCompositeFilterFilterUnionMember22,
    FiltersRepoCompositeFilterFilterUnionMember23,
    FiltersRepoCompositeFilterFilterUnionMember24,
    FiltersRepoCompositeFilterFilterUnionMember25,
    FiltersRepoCompositeFilterFilterUnionMember26,
    FiltersRepoCompositeFilterFilterUnionMember27,
    FiltersRepoCompositeFilterFilterUnionMember28,
    FiltersRepoCompositeFilterFilterUnionMember29,
    FiltersRepoCompositeFilterFilterUnionMember30,
    FiltersRepoCompositeFilterFilterUnionMember31,
    FiltersRepoCompositeFilterFilterUnionMember32,
    FiltersRepoCompositeFilterFilterUnionMember33,
    FiltersRepoCompositeFilterFilterUnionMember34,
    FiltersRepoCompositeFilterFilterUnionMember35,
    FiltersRepoCompositeFilterFilterUnionMember36,
    FiltersRepoCompositeFilterFilterUnionMember37,
    FiltersRepoCompositeFilterFilterUnionMember38,
    FiltersRepoCompositeFilterFilterUnionMember39,
    FiltersRepoCompositeFilterFilterUnionMember40,
    FiltersRepoCompositeFilterFilterUnionMember41,
    FiltersRepoCompositeFilterFilterUnionMember42,
    FiltersRepoCompositeFilterFilterUnionMember43,
    FiltersRepoCompositeFilterFilterUnionMember44,
    FiltersRepoCompositeFilterFilterUnionMember45,
    FiltersRepoCompositeFilterFilterUnionMember46,
    FiltersRepoCompositeFilterFilterUnionMember47,
    FiltersRepoCompositeFilterFilterUnionMember48,
    FiltersRepoCompositeFilterFilterUnionMember49,
    FiltersRepoCompositeFilterFilterUnionMember50,
    FiltersRepoCompositeFilterFilterUnionMember51,
    FiltersRepoCompositeFilterFilterUnionMember52,
    FiltersRepoCompositeFilterFilterUnionMember53,
    FiltersRepoCompositeFilterFilterUnionMember54,
    FiltersRepoCompositeFilterFilterUnionMember55,
    FiltersRepoCompositeFilterFilterUnionMember56,
    FiltersRepoCompositeFilterFilterUnionMember57,
    FiltersRepoCompositeFilterFilterUnionMember58,
    FiltersRepoCompositeFilterFilterUnionMember59,
    FiltersRepoCompositeFilterFilterUnionMember60,
    FiltersRepoCompositeFilterFilterUnionMember61,
    FiltersRepoCompositeFilterFilterUnionMember62,
    FiltersRepoCompositeFilterFilterUnionMember63,
    FiltersRepoCompositeFilterFilterUnionMember64,
    FiltersRepoCompositeFilterFilterUnionMember65,
    FiltersRepoCompositeFilterFilterUnionMember66,
    FiltersRepoCompositeFilterFilterUnionMember67,
    FiltersRepoCompositeFilterFilterUnionMember68,
    FiltersRepoCompositeFilterFilterUnionMember69,
    FiltersRepoCompositeFilterFilterUnionMember70,
    FiltersRepoCompositeFilterFilterUnionMember71,
    FiltersRepoCompositeFilterFilterUnionMember72,
    FiltersRepoCompositeFilterFilterUnionMember73,
    FiltersRepoCompositeFilterFilterUnionMember74,
    FiltersRepoCompositeFilterFilterUnionMember75,
    FiltersRepoCompositeFilterFilterUnionMember76,
    FiltersRepoCompositeFilterFilterUnionMember77,
    FiltersRepoCompositeFilterFilterUnionMember78,
    FiltersRepoCompositeFilterFilterUnionMember79,
    FiltersRepoCompositeFilterFilterUnionMember80,
    FiltersRepoCompositeFilterFilterUnionMember81,
    FiltersRepoCompositeFilterFilterUnionMember82,
    FiltersRepoCompositeFilterFilterUnionMember83,
    FiltersRepoCompositeFilterFilterUnionMember84,
    FiltersRepoCompositeFilterFilterUnionMember85,
    FiltersRepoCompositeFilterFilterUnionMember86,
    FiltersRepoCompositeFilterFilterUnionMember87,
    FiltersRepoCompositeFilterFilterUnionMember88,
    FiltersRepoCompositeFilterFilterUnionMember89,
    FiltersRepoCompositeFilterFilterUnionMember90,
    FiltersRepoCompositeFilterFilterUnionMember91,
    FiltersRepoCompositeFilterFilterUnionMember92,
]


class FiltersRepoCompositeFilter(TypedDict, total=False):
    filters: Required[Iterable[FiltersRepoCompositeFilterFilter]]
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
    FiltersRepoCompositeFilter,
]
