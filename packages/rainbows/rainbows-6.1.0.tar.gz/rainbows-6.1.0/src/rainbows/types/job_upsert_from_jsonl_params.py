# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["JobUpsertFromJSONLParams"]


class JobUpsertFromJSONLParams(TypedDict, total=False):
    file: Required[FileTypes]

    batch_size: int

    chunk_size: int
