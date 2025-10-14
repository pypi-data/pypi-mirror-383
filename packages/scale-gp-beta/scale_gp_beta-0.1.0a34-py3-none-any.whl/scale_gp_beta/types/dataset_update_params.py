# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .._types import SequenceNotStr

__all__ = ["DatasetUpdateParams"]


class DatasetUpdateParams(TypedDict, total=False):
    description: str

    name: str

    tags: SequenceNotStr[str]
    """The tags associated with the entity"""
