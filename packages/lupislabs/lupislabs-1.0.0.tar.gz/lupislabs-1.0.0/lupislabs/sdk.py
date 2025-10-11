import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from opentelemetry import trace
from .types import (
    LupisConfig, LupisBlockOptions, LupisEvent, EventProperties, 
    LupisMetadata, SensitiveDataFilter
)
from .tracer import LupisTracer


class LupisSDK:
    """Main Lupis SDK class for Python applications."""

    def __init__(self, config: LupisConfig):
        self.config = config
        self.tracer = LupisTracer(config)
        self.event_queue: List[LupisEvent] = []
        self.flush_timer: Optional[asyncio.Task] = None
        self.max_batch_size = 50
        self.flush_interval_ms = 5000
        self.global_metadata: LupisMetadata = LupisMetadata()
        self._shutdown_event = asyncio.Event()

    def set_metadata(self, metadata: LupisMetadata):
        """Set global metadata for all traces and events."""
        self.global_metadata = metadata
        self.tracer.set_metadata(metadata)

    def get_metadata(self) -> LupisMetadata:
        """Get current global metadata."""
        return self.global_metadata

    def clear_metadata(self):
        """Clear global metadata."""
        self.global_metadata = LupisMetadata()
        self.tracer.clear_metadata()

    def set_chat_id(self, chat_id: str):
        """Set the current chat ID for grouping traces."""
        self.tracer.set_chat_id(chat_id)

    def clear_chat_id(self):
        """Clear the current chat ID."""
        self.tracer.clear_chat_id()

    async def run(self, fn: Callable[[], Union[Any, Awaitable[Any]]], options: LupisBlockOptions = None) -> Any:
        """Run a function with optional chat ID grouping."""
        if options is None:
            options = LupisBlockOptions()

        if options.chat_id:
            self.set_chat_id(options.chat_id)

        try:
            if asyncio.iscoroutinefunction(fn):
                result = await fn()
            else:
                result = fn()
            return result
        finally:
            if options.chat_id:
                self.clear_chat_id()

    def get_tracer(self) -> trace.Tracer:
        """Get the OpenTelemetry tracer."""
        return self.tracer.get_tracer()

    def create_span(self, name: str, attributes: Optional[Dict[str, Any]] = None, span_kind: Optional[trace.SpanKind] = None) -> trace.Span:
        """Create a new span."""
        return self.tracer.create_span(name, attributes, span_kind)

    def track_event(self, name: str, properties: Optional[EventProperties] = None, metadata: Optional[LupisMetadata] = None):
        """Track a custom event."""
        event = LupisEvent(
            name=name,
            timestamp=int(time.time() * 1000),
            properties=properties,
            metadata=self._merge_metadata(self.global_metadata, metadata)
        )

        self.event_queue.append(event)

        if len(self.event_queue) >= self.max_batch_size:
            asyncio.create_task(self._flush_events())
        elif self.flush_timer is None:
            self.flush_timer = asyncio.create_task(self._schedule_flush())

    def _merge_metadata(self, global_meta: LupisMetadata, local_meta: Optional[LupisMetadata]) -> LupisMetadata:
        """Merge global and local metadata."""
        if local_meta is None:
            return global_meta

        merged = LupisMetadata()
        merged.user_id = local_meta.user_id or global_meta.user_id
        merged.organization_id = local_meta.organization_id or global_meta.organization_id
        merged.session_id = local_meta.session_id or global_meta.session_id
        merged.chat_id = local_meta.chat_id or global_meta.chat_id

        # Merge extra fields
        merged.extra = {}
        if global_meta.extra:
            merged.extra.update(global_meta.extra)
        if local_meta.extra:
            merged.extra.update(local_meta.extra)

        return merged

    async def _schedule_flush(self):
        """Schedule a flush after the interval."""
        try:
            await asyncio.sleep(self.flush_interval_ms / 1000)
            await self._flush_events()
        except asyncio.CancelledError:
            pass
        finally:
            self.flush_timer = None

    async def _flush_events(self):
        """Flush events to the server."""
        if self.flush_timer:
            self.flush_timer.cancel()
            self.flush_timer = None

        if not self.event_queue:
            return

        events_to_send = self.event_queue.copy()
        self.event_queue.clear()

        if not self.config.enabled:
            logging.info(f"[Lupis SDK] Events (not sent, disabled): {len(events_to_send)}")
            return

        events_endpoint = (self.config.otlp_endpoint or "http://localhost:3010/api/traces").replace("/api/traces", "/api/events")

        try:
            import aiohttp
            headers = {
                "Content-Type": "application/json",
                "x-project-id": self.config.project_id,
            }
            if self.config.api_key:
                headers["x-api-key"] = self.config.api_key

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    events_endpoint,
                    headers=headers,
                    json=[event.to_dict() for event in events_to_send],
                ) as response:
                    if response.status == 200:
                        logging.info(f"[Lupis SDK] Successfully sent {len(events_to_send)} events")
                    else:
                        error_text = await response.text()
                        logging.error(f"[Lupis SDK] Failed to send events: {error_text}")
        except ImportError:
            # Fallback to requests if aiohttp is not available
            try:
                import requests
                headers = {
                    "Content-Type": "application/json",
                    "x-project-id": self.config.project_id,
                }
                if self.config.api_key:
                    headers["x-api-key"] = self.config.api_key

                response = requests.post(
                    events_endpoint,
                    headers=headers,
                    json=[event.to_dict() for event in events_to_send],
                    timeout=30,
                )
                if response.status_code == 200:
                    logging.info(f"[Lupis SDK] Successfully sent {len(events_to_send)} events")
                else:
                    logging.error(f"[Lupis SDK] Failed to send events: {response.text}")
            except Exception as e:
                logging.error(f"[Lupis SDK] Error sending events: {e}")
        except Exception as e:
            logging.error(f"[Lupis SDK] Error sending events: {e}")

    async def shutdown(self):
        """Shutdown the SDK and flush pending events."""
        logging.info("[Lupis SDK] Shutting down...")

        # Cancel any pending flush timer
        if self.flush_timer:
            self.flush_timer.cancel()
            self.flush_timer = None

        # Flush remaining events
        await self._flush_events()

        # Shutdown tracer
        await self.tracer.shutdown()

        logging.info("[Lupis SDK] Shutdown complete")
