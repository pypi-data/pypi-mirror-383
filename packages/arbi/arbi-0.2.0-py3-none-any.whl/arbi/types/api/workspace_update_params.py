# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["WorkspaceUpdateParams"]


class WorkspaceUpdateParams(TypedDict, total=False):
    description: Optional[str]

    is_public: Optional[bool]

    name: Optional[str]
