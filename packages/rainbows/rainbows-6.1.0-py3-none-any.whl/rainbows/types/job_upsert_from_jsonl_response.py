# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["JobUpsertFromJSONLResponse"]


class JobUpsertFromJSONLResponse(BaseModel):
    inserted: int
    """Number of jobs inserted"""

    total_processed: int
    """Total number of jobs processed"""

    updated: int
    """Number of jobs updated"""

    errors: Optional[List[str]] = None
    """Any errors encountered during processing"""
