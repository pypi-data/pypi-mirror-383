# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["SettingUpdateParams"]


class SettingUpdateParams(TypedDict, total=False):
    ai_mode: Optional[str]

    pinned_workspaces: Optional[SequenceNotStr[str]]

    show_document_navigator: Optional[bool]

    show_help_page: Optional[bool]

    show_invite_tab: Optional[bool]

    show_security_settings: Optional[bool]

    show_smart_search: Optional[bool]

    show_templates: Optional[bool]

    show_thread_visualization: Optional[bool]
