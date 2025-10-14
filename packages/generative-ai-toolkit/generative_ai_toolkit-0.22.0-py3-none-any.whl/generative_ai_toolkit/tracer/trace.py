# Copyright 2025 Amazon.com, Inc. and its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import json
import secrets
import threading
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import (
    Any,
    Literal,
    NamedTuple,
    TypedDict,
)

from generative_ai_toolkit.utils.json import DefaultJsonEncoder

LOCK = threading.Lock()
IMMUTABLE_TYPES = (int, float, bool, str, type(None), tuple, frozenset)
BLUE = "\033[94m"  # noqa: N806
GREEN = "\033[92m"  # noqa: N806
YELLOW = "\033[93m"  # noqa: N806
RED = "\033[91m"  # noqa: N806
GRAY = "\033[90m"  # noqa: N806
RESET = "\033[0m"  # noqa: N806
MAGENTA = "\033[95m"  # noqa: N806
CYAN = "\033[96m"  # noqa: N806
DIM_GRAY = "\033[2;90m"  # noqa: N806
WHITE = "\033[37m"  # noqa: N806


def thread_safe_deepcopy(obj, lock=LOCK):
    if isinstance(obj, IMMUTABLE_TYPES):
        return obj
    with lock:
        return copy.deepcopy(obj)


class TraceScopeDict(TypedDict):
    name: str
    version: str


class TraceDict(TypedDict):
    span_name: str
    trace_id: str
    span_id: str
    span_kind: Literal["INTERNAL", "SERVER", "CLIENT"]
    parent_span_id: str | None
    started_at: datetime
    ended_at: datetime | None
    duration_ms: int | None
    attributes: Mapping[str, Any]
    span_status: Literal["UNSET", "OK", "ERROR"]
    resource_attributes: Mapping[str, Any]
    scope: TraceScopeDict


class Trace:
    span_name: str
    trace_id: str
    span_id: str
    span_kind: Literal["INTERNAL", "SERVER", "CLIENT"]
    parent_span: "Trace | None"
    started_at: datetime
    ended_at: datetime | None
    cloned_at: datetime | None
    _attributes: dict[str, Any]
    _inheritable_attributes: dict[str, Any]
    span_status: Literal["UNSET", "OK", "ERROR"]
    resource_attributes: Mapping[str, Any]
    scope: "TraceScope"

    def __init__(
        self,
        span_name: str,
        *,
        span_kind: Literal["INTERNAL", "SERVER", "CLIENT"] = "INTERNAL",
        trace_id: str | None = None,
        span_id: str | None = None,
        parent_span: "Trace | None" = None,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        attributes: dict[str, Any] | None = None,
        span_status: Literal["UNSET", "OK", "ERROR"] = "UNSET",
        resource_attributes: Mapping[str, Any] | None = None,
        scope: "TraceScope | None" = None,
        snapshot_handler: Callable[["Trace"], None] | None = None,
    ) -> None:
        self.span_name = span_name
        self.span_kind = span_kind
        self.span_id = span_id or secrets.token_hex(8)
        if trace_id and parent_span and parent_span.trace_id != trace_id:
            raise ValueError(
                f"You provided trace_id {trace_id} and parent_span {parent_span.span_id}, "
                f"but the parent span has a different trace_id {parent_span.trace_id} "
                "(you'll probably want to just provide parent_span, in which case the parent span's trace_id will be used)"
            )
        self.trace_id = trace_id or (
            parent_span.trace_id if parent_span else secrets.token_hex(16)
        )
        self.parent_span = parent_span
        self.started_at = started_at or datetime.now(UTC)
        self.ended_at = ended_at
        self._attributes = attributes or {}
        self._inheritable_attributes = {}
        self.resource_attributes = resource_attributes or {}
        self.scope = scope or (
            parent_span.scope
            if parent_span
            else TraceScope("generative-ai-toolkit", "current")
        )
        self.span_status = span_status
        self._snapshot_handler = snapshot_handler
        self._deepcopy_lock = threading.Lock()
        self._attributes_lock = threading.Lock()
        self.cloned_at = None

    def clone(self):
        """
        Return a stand-alone and flattened clone of the trace.

        To avoid having to clone the entire chain of parent spans:
        - The clone will only include a pointer to its direct parent
        - That parent span will only have its name, span id and trace id set
        - The clone's attributes field will include all inheritable attributes from its parents

        For all intents and purposes, the clone will "look" the same as the original.
        """
        copied = type(self)(
            span_name=self.span_name,
            span_kind=self.span_kind,
            trace_id=self.trace_id,
            span_id=self.span_id,
            parent_span=(
                type(self)(
                    span_name=self.parent_span.span_name,
                    trace_id=self.parent_span.trace_id,
                    span_id=self.parent_span.span_id,
                )
                if self.parent_span
                else None
            ),
            started_at=self.started_at,
            ended_at=self.ended_at,
            attributes=dict(
                thread_safe_deepcopy(self.attributes, lock=self._deepcopy_lock)
            ),
            span_status=self.span_status,
            resource_attributes=thread_safe_deepcopy(
                self.resource_attributes, lock=self._deepcopy_lock
            ),
            scope=self.scope,
        )
        copied.cloned_at = datetime.now(UTC)
        return copied

    def emit_snapshot(self):
        if self._snapshot_handler:
            self._snapshot_handler(self.clone())

    @property
    def attributes(self) -> Mapping[str, Any]:
        with self._attributes_lock:
            inherited: dict[str, Any] = {}
            for trace in [*reversed(self.parents), self]:
                inherited.update(trace._inheritable_attributes)
            return inherited | self._attributes

    @property
    def parents(self) -> list["Trace"]:
        """
        The parent traces, in proximity order, nearest parent first:
        [parent, grandparent, great-grandparent]
        """
        parents = []
        current_parent = self.parent_span
        while current_parent:
            parents.append(current_parent)
            current_parent = current_parent.parent_span
        return parents

    @property
    def duration_ms(self) -> int:
        if not self.ended_at:
            raise ValueError("Span has not ended yet")
        return int((self.ended_at - self.started_at).total_seconds() * 1000)

    def add_attribute(
        self,
        attribute_key: str,
        attribute_value: Any,
        *,
        inheritable=False,
    ) -> "Trace":
        if self.ended_at:
            raise RuntimeError(
                f"Cannot add attribute to span {self.span_name} that already ended"
            )
        attribute_value = thread_safe_deepcopy(
            attribute_value, lock=self._deepcopy_lock
        )
        with self._attributes_lock:
            self._attributes[attribute_key] = attribute_value
            if inheritable:
                self._inheritable_attributes[attribute_key] = attribute_value
            return self

    def __repr__(self) -> str:
        return (
            f"Trace("
            f"span_name={repr(self.span_name)}, "
            f"span_kind={repr(self.span_kind)}, "
            f"trace_id={repr(self.trace_id)}, "
            f"span_id={repr(self.span_id)}, "
            f"parent_span_id={repr(self.parent_span.span_id if self.parent_span else None)}, "
            f"started_at={repr(self.started_at)}, "
            f"ended_at={repr(self.ended_at)}, "
            f"attributes={self.attributes}, "
            f"span_status={repr(self.span_status)}, "
            f"resource_attributes={self.resource_attributes}, "
            f"scope={repr(self.scope)}"
            f")"
        )

    def as_dict(self) -> TraceDict:
        return {
            "span_name": self.span_name,
            "span_kind": self.span_kind,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span.span_id if self.parent_span else None,
            "started_at": self.started_at,
            "ended_at": self.ended_at if self.ended_at else None,
            "duration_ms": self.duration_ms if self.ended_at else None,
            "attributes": self.attributes,
            "span_status": self.span_status,
            "resource_attributes": self.resource_attributes,
            "scope": {
                "name": self.scope.name,
                "version": self.scope.version,
            },
        }

    def as_human_readable(
        self,
        *,
        max_length=160,
        max_lines=-1,
        color_white=WHITE,
        color_blue=BLUE,
        color_green=GREEN,
        color_yellow=YELLOW,
        color_red=RED,
        color_gray=GRAY,
        color_reset=RESET,
        color_magenta=MAGENTA,
        color_cyan=CYAN,
    ) -> str:

        # Snapshots are printed only in gray:
        if self.ended_at is None:
            color_white = color_gray
            color_blue = color_gray
            color_green = color_gray
            color_yellow = color_gray
            color_red = color_gray
            color_magenta = color_gray
            color_cyan = color_gray

        def truncate(
            text: str, max_length=max_length, max_lines=1, indent_subsequent_lines=0
        ) -> str:
            """Helper to truncate long strings"""
            text = str(text).strip().replace("\n", "\\n")
            lines: list[str] = []
            for i in range(max_lines if max_lines >= 0 else 999):
                fragment = text[(i * max_length) : (i + 1) * max_length].strip()
                if not fragment:
                    break
                if i == max_lines - 1 and len(fragment) > max_length - 3:
                    fragment = fragment[: max_length - 3] + "..."
                lines.append(fragment)
            return f"\n{indent_subsequent_lines * " "}".join(lines)

        max_prefix_length = 16

        def truncate_multiline(
            title: str,
            text: str,
            max_lines=max_lines,
        ):
            prefix = f"{' ' * max_prefix_length}{title}: "[-max_prefix_length:]
            return f"{prefix}{truncate(text, max_lines=max_lines, indent_subsequent_lines=len(prefix))}"

        attributes = self.attributes
        important_attrs = {
            attr_name: attributes[attr_name]
            for attr_name in [
                "ai.trace.type",
                "peer.service",
                "ai.conversation.id",
            ]
            if attr_name in attributes
        }
        if "ai.auth.context" in attributes:
            important_attrs["ai.auth.context"] = (
                attributes["ai.auth.context"].get("principal_id", "unknown-principal")
                if isinstance(attributes["ai.auth.context"], Mapping)
                else "unknown-principal"
            )
        attrs_str = " ".join(
            f"{k}={v if type(v) in (int, bool, float) or v is None else truncate(v if type(v) is str else json.dumps(v, cls=DefaultJsonEncoder), 80) }"
            for k, v in important_attrs.items()
        )

        span_kind_color = (
            color_red
            if (
                "ai.tool.error" in attributes
                or "ai.llm.response.error" in attributes
                or "exception.message" in attributes
            )
            else (
                color_magenta
                if self.span_kind == "CLIENT"
                else color_green if self.span_kind == "SERVER" else color_blue
            )
        )

        # Base output
        start_time = self.started_at.isoformat(timespec="milliseconds").replace(
            "+00:00", "Z"
        )
        end_time = (
            self.ended_at.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            if self.ended_at
            else None
        )
        duration_time = f"[{self.duration_ms / 1000:.1f}s]" if self.ended_at else ""
        cloned_at = (
            self.cloned_at.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            if self.cloned_at
            else start_time
        )

        agent_name = attributes.get("ai.agent.name") or self.resource_attributes.get(
            "service.name"
        )
        result = (
            f"{color_blue}[{self.trace_id}/{self.parent_span.span_id if self.parent_span else 'root'}/{self.span_id}]{color_reset} "
            f"{color_cyan}{agent_name or "<missing service.name>"}{color_reset} "
            f"{span_kind_color}{self.span_kind}{color_reset} "
            f"{color_white}{self.span_name} - {start_time} {f'- {end_time} {duration_time} ' if end_time else ''}{f' [SNAPSHOT - {cloned_at}]' if not self.ended_at else ''}{color_reset}"
            f"\n{f'  {color_yellow}{attrs_str}{color_reset}' if attrs_str else ''}"
        )

        trace_type = attributes.get("ai.trace.type")

        if trace_type == "llm-invocation":
            messages = attributes.get("ai.llm.request.messages", [])
            if messages:
                last_message = messages[-1].get("content", "")
                result += f"\n{color_gray}{truncate_multiline("Last message", last_message)}{color_reset}"

            llm_response = attributes.get("ai.llm.response.output", "")
            if llm_response:
                result += f"\n{color_gray}{truncate_multiline("Response", llm_response)}{color_reset}"

            stop_reason = attributes.get("ai.llm.response.stop.reason")
            if stop_reason:
                result += f"\n{color_gray}{truncate_multiline("Stop reason", stop_reason)}{color_reset}"

            if error := attributes.get("ai.llm.response.error"):
                result += (
                    f"\n{color_red}{truncate_multiline("Error", error)}{color_reset}"
                )

        elif trace_type == "tool-invocation":
            tool_input = attributes.get("ai.tool.input")
            if tool_input is not None:
                result += f"\n{color_gray}{truncate_multiline("Input", tool_input)}{color_reset}"

            tool_output = attributes.get("ai.tool.output")
            if tool_output is not None:
                result += f"\n{color_gray}{truncate_multiline("Output",tool_output)}{color_reset}"

            if error := attributes.get("ai.tool.error"):
                result += (
                    f"\n{color_red}{truncate_multiline("Error",error)}{color_reset}"
                )

        elif trace_type in {"converse", "converse-stream"}:
            user_input = attributes.get("ai.user.input")
            if user_input is not None:
                result += f"\n{color_gray}{truncate_multiline("Input",user_input)}{color_reset}"

            agent_response = attributes.get("ai.agent.response")
            if agent_response is not None:
                result += f"\n{color_gray}{truncate_multiline("Response",agent_response)}{color_reset}"

            if error := attributes.get("exception.message"):
                result += (
                    f"\n{color_gray}{truncate_multiline("Error", error)}{color_reset}"
                )

        elif trace_type == "cycle":
            cycle_response = attributes.get("ai.agent.cycle.response")
            if cycle_response is not None:
                result += f"\n{color_gray}{truncate_multiline("Response",cycle_response)}{color_reset}"

            if error := attributes.get("exception.message"):
                result += (
                    f"\n{color_red}{truncate_multiline("Error", error)}{color_reset}"
                )

        elif trace_type == "conversation-history-list":
            conversation_history = attributes.get("ai.conversation.history.messages")
            if conversation_history is not None:
                result += f"\n{color_gray}{truncate_multiline("Messages",conversation_history)}{color_reset}"

        elif trace_type == "conversation-history-add":
            conversation_history = attributes.get("ai.conversation.history.message")
            if conversation_history is not None:
                result += f"\n{color_gray}{truncate_multiline("Message",conversation_history)}{color_reset}"

        return result + "\n" + ("\n" if not self.ended_at else "")


class TraceScope(NamedTuple):
    name: str
    version: str

    def __repr__(self) -> str:
        return f"{self.name}@{self.version}"
