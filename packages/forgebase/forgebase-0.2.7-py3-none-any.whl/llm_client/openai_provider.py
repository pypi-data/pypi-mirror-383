from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Callable, Dict, Iterable, List, Optional
import os

from forge_utils import logger

from .interfaces import ILLMClient
from .llm_exceptions import ConfigurationError
from .models import InputItem, InputToolResult, ResponseResult, Tool
from .openai_client import LLMOpenAIClient
from .response import OpenAIResponse


def _extract_text(resp: Any) -> str:
    """Extrai texto de ResponseResult suportando itens de mensagem ou partes diretas."""
    try:
        items = getattr(resp, "output", None) or []
        for item in items:
            parts = getattr(item, "content", None)
            if parts is None:
                # item pode ser um ContentPart direto
                if (
                    getattr(item, "type", "") in ("output_text", "text")
                    and getattr(item, "text", None)
                ):
                    return item.text.strip()
                continue
            for p in parts:
                if (
                    getattr(p, "type", "") in ("output_text", "text")
                    and getattr(p, "text", None)
                ):
                    return p.text.strip()
        return ""
    except Exception:
        return ""


class OpenAIProvider(ILLMClient):
    """Provider OpenAI que implementa ILLMClient sobre LLMOpenAIClient."""

    def __init__(
        self,
        client: Optional[LLMOpenAIClient] = None,
        timeout: int = 120
    ) -> None:
        self._client = client
        self._model = "gpt-4o"
        self._timeout = timeout
        self._tools_defs: List[Tool] = []
        self._tool_choice: str | dict | None = "auto"
        self._tool_fns: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._hooks: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)
        self._pending_client_hooks: list[tuple[str, Callable[[dict[str, Any]], None]]] = []
        if self._client is not None:
            self._ensure_client_hooks()
        # Pending outputs buffer for streaming follow-ups
        self._pending_outputs: list[dict] = []

    PROVIDER_EVENTS = {
        "before_send",
        "after_send",
        "on_error",
        "before_tool_call",
        "after_tool_call",
        "tool_error",
        "cache_hit",
    }

    def register_hook(self, event: str, callback: Callable[[dict[str, Any]], None]) -> None:
        if event in LLMOpenAIClient.HOOK_EVENTS:
            self._pending_client_hooks.append((event, callback))
            self._ensure_client_hooks()
            return
        if event not in self.PROVIDER_EVENTS:
            raise ValueError(f"Evento de hook desconhecido: {event}")
        self._hooks[event].append(callback)

    def clear_hooks(self, event: str | None = None) -> None:
        if event is None:
            self._hooks.clear()
            self._pending_client_hooks.clear()
            if self._client is not None:
                self._client.clear_hooks()
        else:
            if event in LLMOpenAIClient.HOOK_EVENTS:
                self._pending_client_hooks = [
                    (evt, cb)
                    for evt, cb in self._pending_client_hooks
                    if evt != event
                ]
                if self._client is not None:
                    self._client.clear_hooks(event)
            else:
                self._hooks.pop(event, None)

    def _ensure_client_hooks(self) -> None:
        if self._client is None:
            return
        for event, callback in self._pending_client_hooks:
            self._client.register_hook(event, callback)
        self._pending_client_hooks.clear()
        # Bridge client's tool hook events to provider-level hooks
        try:
            def _forward_tool(event: str, payload: dict[str, Any]) -> None:
                if event == "before_tool":
                    self._emit_provider_hook("before_tool_call", payload)
                elif event == "after_tool":
                    self._emit_provider_hook("after_tool_call", payload)
                elif event == "tool_error":
                    self._emit_provider_hook("tool_error", payload)
            self._client.set_tool_hook(_forward_tool)  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - defensivo
            pass

    def _emit_provider_hook(self, event: str, payload: dict[str, Any]) -> None:
        for callback in list(self._hooks.get(event, [])):
            try:
                callback(payload)
            except Exception as hook_exc:  # pragma: no cover - hooks não devem interromper o fluxo
                logger.error(
                    "Erro ao executar hook do provider '%s'",
                    event,
                    exc_info=hook_exc,
                )

    def notify_cache_hit(self, payload: dict[str, Any]) -> None:
        """Emite manualmente o hook de cache quando houver reutilização local."""
        self._emit_provider_hook("cache_hit", payload)

    @property
    def name(self) -> str:
        return "openai"

    def set_api_key(self, key: str) -> bool:
        if self._client is None:
            self._client = LLMOpenAIClient(
                api_key=key,
                model=self._model,
                temperature=0.7,
                timeout=self._timeout
            )
            self._ensure_client_hooks()
            return True
        # atualiza a response interna
        self._client.response.api_key = key
        return True

    # Tools configuration / registry
    def configure_tools(self, tools: List[Tool], tool_choice: str | dict | None = "auto") -> None:
        self._tools_defs = tools
        self._tool_choice = tool_choice
        if self._client:
            self._client.configure_tools(tools=tools, tool_choice=tool_choice)

    def register_tool(self, name: str, func: Callable[[Dict[str, Any]], Any]) -> None:
        self._tool_fns[name] = func

    def send_message(
        self,
        prompt: str,
        context: Optional[List[dict]] = None,
        *,
        images: list[str] | None = None,
        audio: str | dict[str, str] | None = None,
    ) -> str:
        if not isinstance(prompt, str) or not prompt:
            raise ConfigurationError("prompt inválido")
        if self._client is None:
            raise ConfigurationError("cliente não configurado (chame set_api_key)")
        self._ensure_client_hooks()
        payload: dict[str, Any] = {
            "prompt": prompt,
            "context": context,
            "streamed": False,
            "images": images,
            "audio": audio,
        }
        self._emit_provider_hook("before_send", payload)
        # Use tool orchestration do LLMOpenAIClient se tools configuradas
        try:
            if self._tools_defs or self._tool_fns:
                for name, handler in self._tool_fns.items():
                    self._client.register_tool(name, handler)
                result = self._client.send_with_tool_orchestration(
                    prompt,
                    tools=self._tools_defs,
                    tool_choice=self._tool_choice,
                    images=images,
                    audio=audio,
                )
            else:
                resp = self._client.send_prompt(
                    prompt,
                    streamed=False,
                    images=images,
                    audio=audio,
                )
                result = _extract_text(resp) or ""
        except Exception as exc:
            payload_err = dict(payload)
            payload_err["error"] = exc
            self._emit_provider_hook("on_error", payload_err)
            raise
        payload_after = dict(payload)
        payload_after["result"] = result
        self._emit_provider_hook("after_send", payload_after)
        return result

    def send_stream(
        self,
        prompt: str,
        context: Optional[List[dict]] = None,
        *,
        images: list[str] | None = None,
        audio: str | dict[str, str] | None = None,
    ) -> Iterable[str]:
        if not isinstance(prompt, str) or not prompt:
            raise ConfigurationError("prompt inválido")
        if self._client is None:
            raise ConfigurationError("cliente não configurado (chame set_api_key)")
        self._ensure_client_hooks()
        payload: dict[str, Any] = {
            "prompt": prompt,
            "context": context,
            "streamed": True,
            "images": images,
            "audio": audio,
        }
        self._emit_provider_hook("before_send", payload)

        from typing import cast

        try:
            if self._tools_defs or self._tool_fns:
                stream_iter = self._stream_with_tools(prompt, images=images, audio=audio)
            else:
                stream_iter = cast(
                    Iterable[str],
                    self._client.send_prompt(
                        prompt,
                        streamed=True,
                        images=images,
                        audio=audio,
                    ),
                )
        except Exception as exc:
            payload_err = dict(payload)
            payload_err["error"] = exc
            self._emit_provider_hook("on_error", payload_err)
            raise

        def wrapper() -> Iterable[str]:
            try:
                for chunk in stream_iter:
                    yield chunk
            except Exception as exc:
                payload_err = dict(payload)
                payload_err["error"] = exc
                self._emit_provider_hook("on_error", payload_err)
                raise
            else:
                payload_after = dict(payload)
                payload_after["result"] = None
                self._emit_provider_hook("after_send", payload_after)

        return wrapper()

    def list_models(self) -> dict[str, Any]:
        if self._client is None:
            raise ConfigurationError("cliente não configurado (chame set_api_key)")
        self._ensure_client_hooks()
        payload: dict[str, Any] = {"operation": "list_models"}
        self._emit_provider_hook("before_send", payload)
        try:
            result = self._client.list_models()
        except Exception as exc:
            payload_err = dict(payload)
            payload_err["error"] = exc
            self._emit_provider_hook("on_error", payload_err)
            raise
        payload_after = dict(payload)
        payload_after["result"] = result
        self._emit_provider_hook("after_send", payload_after)
        return result

    # Internal: one-step tool orchestration (sync)
    def _collect_tool_uses(self, resp: ResponseResult) -> List[dict]:
        uses: List[dict] = []
        for item in getattr(resp, "output", []) or []:
            # 1) function_call item (top-level)
            if getattr(item, "type", "") == "function_call":
                name = getattr(item, "name", "")
                call_id = getattr(item, "call_id", None) or getattr(item, "id", "")
                raw_args = getattr(item, "arguments", {})
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                else:
                    args = raw_args
                # raw item to include back into input on follow-up (as docs recommend)
                try:
                    raw_item = {
                        "type": "function_call",
                        "name": name,
                        "call_id": call_id,
                        "arguments": raw_args if isinstance(raw_args, str) else json.dumps(args),
                    }
                except Exception:
                    raw_item = {
                        "type": "function_call",
                        "name": name,
                        "call_id": call_id,
                        "arguments": "{}",
                    }
                if call_id:
                    uses.append(
                        {
                            "kind": "function",
                            "name": name,
                            "id": call_id,
                            "args": args,
                            "raw": raw_item,
                        }
                    )
                continue

            # 2) tool_use em mensagem ou top-level
            parts = getattr(item, "content", None)
            candidate_parts = parts if parts is not None else [item]
            for part in candidate_parts:
                ptype = getattr(part, "type", "")
                if ptype == "tool_use":
                    name = (getattr(part, "name", None) or "")
                    tool_id = (getattr(part, "id", None) or getattr(part, "tool_use_id", None) or "")
                    raw_args = getattr(part, "input", None) or getattr(part, "arguments", None) or {}
                    if isinstance(raw_args, str):
                        try:
                            args = json.loads(raw_args)
                        except Exception:  # pragma: no cover - malformed JSON
                            args = {}
                    else:
                        args = raw_args
                    if tool_id:
                        # raw tool_use item for follow-up context
                        raw_item = {
                            "type": "tool_use",
                            "id": tool_id,
                            "name": name,
                            "input": (
                                raw_args
                                if isinstance(raw_args, str)
                                else json.dumps(args)
                            ),
                        }
                        uses.append(
                            {
                                "kind": "tool",
                                "name": name,
                                "id": tool_id,
                                "args": args,
                                "raw": raw_item,
                            }
                        )
                elif ptype == "function_call":
                    name = (getattr(part, "name", None) or "")
                    call_id = (getattr(part, "call_id", None) or getattr(part, "id", None) or "")
                    raw_args = getattr(part, "arguments", None) or {}
                    if isinstance(raw_args, str):
                        try:
                            args = json.loads(raw_args)
                        except Exception:  # pragma: no cover - malformed JSON
                            args = {}
                    else:
                        args = raw_args
                    if call_id:
                        # raw function_call item for follow-up context
                        try:
                            raw_item = {
                                "type": "function_call",
                                "name": name,
                                "call_id": call_id,
                                "arguments": (
                                    raw_args
                                    if isinstance(raw_args, str)
                                    else json.dumps(args)
                                ),
                            }
                        except Exception:
                            raw_item = {
                                "type": "function_call",
                                "name": name,
                                "call_id": call_id,
                                "arguments": "{}",
                            }
                        uses.append(
                            {
                                "kind": "function",
                                "name": name,
                                "id": call_id,
                                "args": args,
                                "raw": raw_item,
                            }
                        )
        return uses

    def _eval_tools(self, uses: List[dict]) -> List[dict]:
        results: List[dict] = []
        is_real = isinstance(getattr(self._client, "response", None), OpenAIResponse)
        for u in uses:
            fn = self._tool_fns.get(u["name"]) if u.get("name") else None
            metadata = {
                "tool": u.get("name"),
                "args": u.get("args"),
                "id": u.get("id"),
            }
            self._emit_provider_hook("before_tool_call", metadata)
            error: Exception | None = None
            try:
                result = fn(u["args"]) if fn else "(tool not registered)"
            except Exception as exc:  # pragma: no cover - tool error
                error = exc
                metadata_err = dict(metadata)
                metadata_err["error"] = exc
                self._emit_provider_hook("tool_error", metadata_err)
                result = f"tool_error: {exc}"
            metadata_after = dict(metadata)
            metadata_after["result"] = result
            if error is not None:
                metadata_after["error"] = error
            self._emit_provider_hook("after_tool_call", metadata_after)

            if u.get("kind") == "function":
                # Build output payload
                if isinstance(result, (dict, list)):
                    output = json.dumps(result)
                else:
                    output = json.dumps({"result": str(result)})
                call_identifier = u.get("id")
                if not call_identifier:
                    continue
                if is_real:
                    results.append(
                        {
                            "type": "function_call_output",
                            "call_id": str(call_identifier),
                            "output": output,
                        }
                    )
                else:
                    # For tests/local, keep function_call_output and include raw call
                    raw = u.get("raw")
                    if isinstance(raw, dict):
                        results.append(raw)
                    results.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_identifier,
                            "output": output,
                        }
                    )
            else:
                call_identifier = u.get("id")
                if not call_identifier:
                    continue
                if isinstance(result, (dict, list)):
                    output = json.dumps(result)
                else:
                    output = str(result)
                if is_real:
                    results.append(
                        {
                            "type": "custom_tool_call_output",
                            "call_id": str(call_identifier),
                            "output": output,
                        }
                    )
                else:
                    results.append(
                        {
                            "type": "custom_tool_call_output",
                            "call_id": call_identifier,
                            "output": output,
                        }
                    )
        return results

    def _stream_with_tools(
        self,
        prompt: str,
        *,
        images: list[str] | None = None,
        audio: str | dict[str, str] | None = None,
    ) -> Iterable[str]:
        assert self._client is not None
        client = self._client
        previous_response_id: Optional[str] = None
        context_items: Optional[List[InputItem | InputToolResult | dict[str, Any]]] = None
        current_tool_choice: str | dict | None = self._tool_choice

        def run_loop() -> Iterable[str]:
            nonlocal previous_response_id, context_items, current_tool_choice
            # Compatibility flags (env-driven) for follow-up behavior
            # Defaults (v0.2.5): outputs-only ON, tool_choice override to 'none', include_output_name ON
            _oo = os.getenv("FORGEBASE_FOLLOWUP_OUTPUTS_ONLY", None)
            outputs_only = not (_oo or "").strip().lower() in {"0", "false", "no"}
            tool_choice_override = os.getenv("FORGEBASE_FOLLOWUP_TOOL_CHOICE", None)
            if tool_choice_override is None or not tool_choice_override.strip():
                tool_choice_override = "none"
            include_output_name = not (os.getenv("FORGEBASE_OUTPUT_NAME", "").strip().lower() in {"0", "false", "no"})
            try:
                # Propagate to client: used in building output payloads (optional name)
                setattr(self._client, "_forgebase_include_output_name", include_output_name)  # type: ignore[attr-defined]
            except Exception:
                pass
            for _ in range(3):
                any_delta = False
                sent_pending_this_call = False
                events = client.stream_events(
                    prompt,
                    tools=self._tools_defs or None,
                    tool_choice=current_tool_choice,
                    previous_response_id=previous_response_id,
                    input_override=context_items,
                    images=images,
                    audio=audio,
                )
                response_obj: Optional[ResponseResult] = None
                for event in events:
                    event_type = event.get("type")
                    if event_type == "response.output_text.delta":
                        delta = event.get("delta", "")
                        if delta:
                            any_delta = True
                            yield delta
                    elif event_type == "response.completed" and event.get("response"):
                        try:
                            response_obj = ResponseResult(**event["response"])
                        except Exception:  # pragma: no cover - defensive
                            response_obj = None
                    elif event_type == "response.failed":
                        message = event.get("error", {}).get("message") if isinstance(event.get("error"), dict) else None
                        raise ConfigurationError(message or "Falha no streaming da API.")

                if response_obj is None:
                    break

                previous_response_id = response_obj.id
                # If we successfully completed a call, clear pending outputs that were sent
                if self._pending_outputs and sent_pending_this_call:
                    self._pending_outputs.clear()
                uses = self._collect_tool_uses(response_obj)
                if not uses:
                    if not any_delta:
                        fallback = _extract_text(response_obj)
                        if fallback:
                            yield fallback
                    break

                tool_results = self._eval_tools(uses)
                if not tool_results:
                    break

                next_context: List[InputItem | InputToolResult | dict[str, Any]] = []
                is_real = isinstance(getattr(client, "response", None), OpenAIResponse)
                for u in uses:
                    raw = u.get("raw")
                    if isinstance(raw, dict):
                        # For real API calls, include raw call descriptors (function_call/tool_use)
                        # unless outputs_only is requested.
                        if not outputs_only:
                            if is_real and raw.get("type") in {"function_call", "tool_use"}:
                                next_context.append(raw)
                            elif not is_real:
                                next_context.append(raw)
                # Merge pending outputs with new outputs to ensure none is lost
                merged_outputs: list[dict] = []
                if self._pending_outputs:
                    merged_outputs.extend(self._pending_outputs)
                merged_outputs.extend(tool_results)
                next_context.extend(merged_outputs)
                # Mark that we will send pending outputs on next call
                if merged_outputs:
                    self._pending_outputs = merged_outputs
                    sent_pending_this_call = True
                else:
                    sent_pending_this_call = False
                context_items = next_context

                # Debug logging of follow-up payload (ids/types only)
                if os.getenv("FORGEBASE_DEBUG_FOLLOWUP", "").strip().lower() in {"1", "true", "yes"}:
                    try:
                        from forge_utils import logger as _log
                        outs = [it for it in context_items if isinstance(it, dict) and it.get("type") in {
                            "function_call_output", "custom_tool_call_output", "function_result", "tool_result"
                        }]
                        types = [it.get("type") for it in (context_items or []) if isinstance(it, dict)]
                        cids = [it.get('call_id') for it in outs]
                        msg = f"[follow-up] prev={previous_response_id} outputs={len(outs)} types={types} call_ids={cids}"
                        # Log também em INFO para garantir visibilidade em produção
                        _log.info(msg)
                    except Exception:
                        pass

                follow_tool_choice = None if self._tool_choice == "required" else self._tool_choice
                current_tool_choice = tool_choice_override or (follow_tool_choice or "auto")

        return run_loop()

    def _send_with_tools(
        self,
        prompt: str,
        *,
        images: list[str] | None = None,
        audio: str | dict[str, str] | None = None,
    ) -> str:
        assert self._client is not None
        client = self._client
        # First turn
        from typing import cast
        resp: ResponseResult = cast(
            ResponseResult,
            client.send_prompt(
                prompt,
                streamed=False,
                tools=self._tools_defs or None,
                tool_choice=self._tool_choice,
                images=images,
                audio=audio,
            ),
        )

        # Iterate tool resolution up to N rounds
        for _ in range(3):
            uses = self._collect_tool_uses(resp)
            if not uses:
                text = _extract_text(resp)
                if text:
                    return text
                break
            tool_results = self._eval_tools(uses)
            if not tool_results:
                break
            # Build context: original user message + raw function/tool calls + their outputs
            # Build follow-up context: only call descriptors and their outputs
            context_items: List[InputItem | InputToolResult | dict[str, Any]] = []
            is_real = isinstance(getattr(client, "response", None), OpenAIResponse)
            for u in uses:
                raw = u.get("raw")
                if isinstance(raw, dict):
                    # For real API calls, include the original function_call descriptor too
                    # (as per some Responses API examples) before its corresponding output.
                    if is_real and raw.get("type") == "function_call":
                        context_items.append(raw)
                    elif not is_real:
                        context_items.append(raw)
            context_items.extend(tool_results)

            # Importante: após executar ferramentas, permita o modelo responder.
            # Evite manter 'required' no follow-up para não forçar novos tool calls.
            follow_tool_choice = (
                None if self._tool_choice == "required" else self._tool_choice
            )
            resp = cast(
                ResponseResult,
                client.send_prompt(
                    prompt,
                    streamed=False,
                    tools=self._tools_defs or None,
                    tool_choice=follow_tool_choice or "auto",
                    previous_response_id=resp.id,
                    input_override=context_items,
                    images=images,
                    audio=audio,
                ),
            )

        return _extract_text(resp) or ""


__all__ = ["OpenAIProvider"]
