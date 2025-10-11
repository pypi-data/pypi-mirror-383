import logging
from typing import Any, Dict, Optional
from opentelemetry import trace
from opentelemetry.trace import Span, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from .types import LupisConfig, LupisMetadata, SensitiveDataFilter
from .http_interceptor import HttpInterceptor


class MetadataSpanProcessor:
    """Custom span processor to add metadata to spans."""
    
    def __init__(self):
        self.current_chat_id: Optional[str] = None
        self.current_metadata: LupisMetadata = LupisMetadata()

    def set_chat_id(self, chat_id: str):
        """Set the current chat ID."""
        self.current_chat_id = chat_id

    def clear_chat_id(self):
        """Clear the current chat ID."""
        self.current_chat_id = None

    def set_metadata(self, metadata: LupisMetadata):
        """Set the current metadata."""
        self.current_metadata = metadata

    def clear_metadata(self):
        """Clear the current metadata."""
        self.current_metadata = LupisMetadata()

    def on_start(self, span: Span, parent_context=None):
        """Called when a span starts."""
        if self.current_chat_id:
            span.set_attribute("lupis.chat.id", self.current_chat_id)

        # Add all metadata as span attributes
        metadata_dict = self._metadata_to_dict(self.current_metadata)
        for key, value in metadata_dict.items():
            if value is not None:
                span.set_attribute(f"lupis.metadata.{key}", str(value))

    def on_end(self, span: Span):
        """Called when a span ends."""
        pass

    def shutdown(self):
        """Shutdown the processor."""
        pass

    def force_flush(self, timeout_millis: int = 30000):
        """Force flush any pending spans."""
        pass

    def _metadata_to_dict(self, metadata: LupisMetadata) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        result = {}
        if metadata.user_id:
            result["user_id"] = metadata.user_id
        if metadata.organization_id:
            result["organization_id"] = metadata.organization_id
        if metadata.session_id:
            result["session_id"] = metadata.session_id
        if metadata.chat_id:
            result["chat_id"] = metadata.chat_id
        if metadata.extra:
            result.update(metadata.extra)
        return result


class LupisTracer:
    """Lupis OpenTelemetry tracer with metadata support."""

    def __init__(self, config: LupisConfig):
        self.config = config
        self.metadata_processor = MetadataSpanProcessor()
        self.http_interceptor: Optional[HttpInterceptor] = None

        # Create resource
        resource = Resource.create({
            "service.name": config.service_name,
            "service.version": config.service_version,
            "lupis.project.id": config.project_id,
        })

        # Create tracer provider
        self.provider = TracerProvider(resource=resource)

        # Add metadata processor
        self.provider.add_span_processor(self.metadata_processor)

        # Add span processors based on configuration
        if config.enabled:
            otlp_url = config.otlp_endpoint or "http://localhost:3010/api/traces"
            logging.info(f"[Lupis SDK] Initializing OTLP Exporter with URL: {otlp_url}")

            headers = {"x-project-id": config.project_id}
            if hasattr(config, "api_key") and config.api_key:
                headers["x-api-key"] = config.api_key

            otlp_exporter = OTLPSpanExporter(endpoint=otlp_url, headers=headers)

            span_processor = BatchSpanProcessor(
                otlp_exporter,
                schedule_delay_millis=5000,
                max_queue_size=2048,
                max_export_batch_size=512,
                export_timeout_millis=30000,
            )
            self.provider.add_span_processor(span_processor)
        else:
            console_exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(console_exporter)
            self.provider.add_span_processor(span_processor)

        # Set the global tracer provider
        trace.set_tracer_provider(self.provider)

        # Get tracer
        self.tracer = trace.get_tracer(config.service_name, config.service_version)

        # Initialize HTTP interception
        sensitive_data_filter = SensitiveDataFilter(
            filter_sensitive_data=config.filter_sensitive_data,
            sensitive_data_patterns=config.sensitive_data_patterns,
            redaction_mode=config.redaction_mode
        )

        self.http_interceptor = HttpInterceptor(
            self.tracer,
            config.project_id,
            sensitive_data_filter
        )
        self.http_interceptor.start_intercepting()

    def get_tracer(self) -> trace.Tracer:
        """Get the OpenTelemetry tracer."""
        return self.tracer

    def set_chat_id(self, chat_id: str):
        """Set the current chat ID for all spans."""
        self.metadata_processor.set_chat_id(chat_id)

    def clear_chat_id(self):
        """Clear the current chat ID."""
        self.metadata_processor.clear_chat_id()

    def set_metadata(self, metadata: LupisMetadata):
        """Set metadata for all spans."""
        self.metadata_processor.set_metadata(metadata)

    def clear_metadata(self):
        """Clear metadata for all spans."""
        self.metadata_processor.clear_metadata()

    def create_span(self, name: str, attributes: Optional[Dict[str, Any]] = None, span_kind: Optional[StatusCode] = None) -> Span:
        """Create a new span."""
        return self.tracer.start_span(name, attributes=attributes)

    async def shutdown(self):
        """Shutdown the tracer and flush pending spans."""
        logging.info("[Lupis SDK] Stopping HTTP interception...")
        if self.http_interceptor:
            self.http_interceptor.stop_intercepting()

        logging.info("[Lupis SDK] Flushing spans...")
        self.provider.force_flush()

        logging.info("[Lupis SDK] Shutting down...")
        self.provider.shutdown()

        logging.info("[Lupis SDK] Shutdown complete")
