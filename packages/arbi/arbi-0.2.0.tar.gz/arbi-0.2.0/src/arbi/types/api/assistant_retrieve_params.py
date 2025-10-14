# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from ..chunk_param import ChunkParam

__all__ = [
    "AssistantRetrieveParams",
    "Tools",
    "ToolsModelCitationTool",
    "ToolsModelCitationToolToolResponses",
    "ToolsRetrievalChunkToolInput",
    "ToolsRetrievalFullContextToolInput",
]


class AssistantRetrieveParams(TypedDict, total=False):
    content: Required[str]

    workspace_ext_id: Required[str]

    config_ext_id: Optional[str]

    parent_message_ext_id: Optional[str]

    tools: Dict[str, Tools]


class ToolsModelCitationToolToolResponses(TypedDict, total=False):
    chunk_ids: Required[SequenceNotStr[str]]

    offset_end: Required[int]

    offset_start: Required[int]

    statement: Required[str]


class ToolsModelCitationTool(TypedDict, total=False):
    description: str

    name: Literal["model_citation"]

    tool_responses: Dict[str, ToolsModelCitationToolToolResponses]


class ToolsRetrievalChunkToolInput(TypedDict, total=False):
    description: str

    name: Literal["retrieval_chunk"]

    tool_args: Dict[str, SequenceNotStr[str]]

    tool_responses: Dict[str, Iterable[ChunkParam]]


class ToolsRetrievalFullContextToolInput(TypedDict, total=False):
    description: str

    name: Literal["retrieval_full_context"]

    tool_args: Dict[str, object]

    tool_responses: Dict[str, Iterable[ChunkParam]]


Tools: TypeAlias = Union[ToolsModelCitationTool, ToolsRetrievalChunkToolInput, ToolsRetrievalFullContextToolInput]
