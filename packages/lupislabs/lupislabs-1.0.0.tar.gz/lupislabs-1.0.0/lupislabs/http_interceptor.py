import time
import json
import requests
from typing import Any, Dict, List, Optional, Protocol
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from .types import ProviderName, NormalizedStreamingResult, SensitiveDataFilter, LupisBlockOptions
from .sensitive_data_filter import SensitiveDataFilterUtil


class ProviderHandler(Protocol):
    provider: ProviderName
    
    def detect(self, url: str) -> bool:
        ...
    
    def is_streaming_chunk(self, text_chunk: str) -> bool:
        ...
    
    def accumulate_chunk(self, state: Any, text_chunk: str) -> Dict[str, Any]:
        ...
    
    def normalize_final(self, raw_body_text: str) -> Any:
        ...


class OpenAIHandler:
    provider: ProviderName = "openai"
    
    def detect(self, url: str) -> bool:
        return "api.openai.com" in url
    
    def is_streaming_chunk(self, text_chunk: str) -> bool:
        return "\ndata: " in text_chunk
    
    def accumulate_chunk(self, state: Any, text_chunk: str) -> Dict[str, Any]:
        if state is None:
            state = {
                "__raw_chunks": [],
                "__aggregated_text": "",
                "__tool_calls": [],
                "__usage": None
            }
        
        state["__raw_chunks"].append(text_chunk)
        lines = text_chunk.split("\n")
        
        for line in lines:
            if not line.startswith("data: "):
                continue
            payload = line[6:].strip()
            if payload == "[DONE]":
                continue
            
            try:
                json_data = json.loads(payload)
                if isinstance(json_data.get("choices"), list):
                    for choice in json_data["choices"]:
                        if choice.get("delta", {}).get("content"):
                            state["__aggregated_text"] += choice["delta"]["content"]
                        if isinstance(choice.get("delta", {}).get("tool_calls"), list):
                            state["__tool_calls"].extend(choice["delta"]["tool_calls"])
                
                if json_data.get("usage"):
                    state["__usage"] = json_data["usage"]
            except (json.JSONDecodeError, KeyError):
                pass
        
        return {"state": state}
    
    def normalize_final(self, raw_body_text: str) -> Any:
        try:
            parsed = json.loads(raw_body_text)
            aggregated_text = parsed.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {**parsed, "aggregatedText": aggregated_text}
        except (json.JSONDecodeError, KeyError, IndexError):
            return raw_body_text


class AnthropicHandler:
    provider: ProviderName = "claude"
    
    def detect(self, url: str) -> bool:
        return "api.anthropic.com" in url
    
    def is_streaming_chunk(self, text_chunk: str) -> bool:
        return "\nevent: " in text_chunk or "\ndata: " in text_chunk
    
    def accumulate_chunk(self, state: Any, text_chunk: str) -> Dict[str, Any]:
        if state is None:
            state = {
                "__raw_chunks": [],
                "__aggregated_text": "",
                "__tool_calls": [],
                "__usage": None
            }
        
        state["__raw_chunks"].append(text_chunk)
        lines = text_chunk.split("\n")
        
        for line in lines:
            if not line.startswith("data: "):
                continue
            
            try:
                json_data = json.loads(line[6:])
                if json_data.get("delta", {}).get("text"):
                    state["__aggregated_text"] += json_data["delta"]["text"]
                
                if json_data.get("type") == "tool_use":
                    state["__tool_calls"].append({
                        "id": json_data["id"],
                        "name": json_data["name"],
                        "type": "function",
                        "function": {
                            "name": json_data["name"],
                            "arguments": json.jsonify(json_data.get("input", {}))
                        }
                    })
                
                if json_data.get("usage"):
                    state["__usage"] = json_data["usage"]
                
                if json_data.get("type") == "message_delta" and json_data.get("usage"):
                    state["__usage"] = json_data["usage"]
            except (json.JSONDecodeError, KeyError):
                pass
        
        return {"state": state}
    
    def normalize_final(self, raw_body_text: str) -> Any:
        try:
            parsed = json.loads(raw_body_text)
            aggregated_text = parsed.get("content", [{}])[0].get("text", "")
            return {**parsed, "aggregatedText": aggregated_text}
        except (json.JSONDecodeError, KeyError, IndexError):
            return raw_body_text


class HttpInterceptor:
    def __init__(
        self,
        tracer: trace.Tracer,
        project_id: str,
        sensitive_data_filter: Optional[SensitiveDataFilter] = None
    ):
        self.tracer = tracer
        self.project_id = project_id
        self.is_intercepting = False
        self.original_request = requests.Session.request
        self.sensitive_data_filter = SensitiveDataFilterUtil(
            sensitive_data_filter or SensitiveDataFilter()
        )

        # Provider handlers
        self.handlers = {
            "openai": OpenAIHandler(),
            "claude": AnthropicHandler(),
        }

    def start_intercepting(self):
        """Start intercepting HTTP requests."""
        if self.is_intercepting:
            return

        self.is_intercepting = True
        self._patch_requests()

    def stop_intercepting(self):
        """Stop intercepting HTTP requests."""
        if not self.is_intercepting:
            return

        self.is_intercepting = False
        requests.Session.request = self.original_request

    def _patch_requests(self):
        """Patch the requests library to intercept HTTP calls."""
        original_request = requests.Session.request

        def patched_request(self, method, url, **kwargs):
            start_time = time.time()
            provider = self._detect_provider(url)
            handler = self._resolve_handler(provider)

            # Skip OTLP traces to avoid recursion
            if "/v1/traces" in url:
                return original_request(self, method, url, **kwargs)

            with self.tracer.start_as_current_span(f"HTTP {method.upper()}") as span:
                span.set_attribute("http.method", method.upper())
                span.set_attribute("http.url", url)
                span.set_attribute("url.full", url)
                span.set_attribute("http.provider", provider)
                span.set_attribute("lupis.project.id", self.project_id)
                span.set_attribute("lupis.complete", "true")

                # Skip request body to reduce span size - focus on pricing/time/message type data

                # Capture request headers
                if kwargs.get("headers"):
                    filtered_headers = self.sensitive_data_filter.filter_headers(kwargs["headers"])
                    span.set_attribute("http.request.headers", json.dumps(filtered_headers))

                try:
                    response = original_request(self, method, url, **kwargs)
                    duration = int((time.time() - start_time) * 1000)

                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("http.response.status_code", response.status_code)
                    span.set_attribute("http.response.status", response.status_code)

                    # Capture response headers
                    filtered_response_headers = self.sensitive_data_filter.filter_headers(dict(response.headers))
                    span.set_attribute("http.response.headers", json.dumps(filtered_response_headers))

                    # Skip response body to reduce span size - focus on pricing/time/message type data
                    # Only capture usage/pricing data if available
                    try:
                        response_text = response.text
                        if handler:
                            normalized_body = handler.normalize_final(response_text)
                            if isinstance(normalized_body, dict) and "usage" in normalized_body:
                                span.set_attribute(
                                    "http.response.usage", json.dumps(normalized_body["usage"])
                                )
                    except Exception as e:
                        # Skip error body capture to reduce span size
                        pass

                    span.set_status(Status(StatusCode.OK if response.ok else StatusCode.ERROR))
                    return response

                except Exception as error:
                    span.record_exception(error)
                    span.set_status(Status(StatusCode.ERROR, str(error)))
                    raise

        # Patch the requests.Session.request method
        requests.Session.request = patched_request

    def _detect_provider(self, url: str) -> str:
        """Detect the AI provider from URL."""
        if "api.openai.com" in url:
            return "openai"
        elif "api.anthropic.com" in url:
            return "claude"
        elif "api.cohere.ai" in url:
            return "cohere"
        elif "api.huggingface.co" in url:
            return "huggingface"
        elif "api.google.com" in url:
            return "google"
        return "unknown"

    def _resolve_handler(self, provider: str) -> Optional[ProviderHandler]:
        """Resolve provider handler."""
        return self.handlers.get(provider)
