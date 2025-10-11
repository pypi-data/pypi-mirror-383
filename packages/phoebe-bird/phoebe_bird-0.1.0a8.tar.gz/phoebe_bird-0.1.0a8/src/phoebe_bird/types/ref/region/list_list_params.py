# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ListListParams"]


class ListListParams(TypedDict, total=False):
    region_type: Required[Annotated[str, PropertyInfo(alias="regionType")]]

    fmt: Literal["csv", "json"]
    """Fetch the records in CSV or JSON format."""
