# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["DatasetCreateParams"]


class DatasetCreateParams(TypedDict, total=False):
    data: Required[Iterable[Dict[str, object]]]
    """Items to be included in the dataset"""

    name: Required[str]

    description: str

    tags: SequenceNotStr[str]
    """The tags associated with the entity"""
