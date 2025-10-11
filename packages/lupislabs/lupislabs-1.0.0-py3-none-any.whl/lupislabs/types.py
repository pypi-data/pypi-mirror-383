from typing import Dict, Any, Optional, Union, List, Literal
from dataclasses import dataclass


@dataclass
class LupisConfig:
    project_id: str
    api_key: Optional[str] = None
    enabled: bool = True
    otlp_endpoint: Optional[str] = None
    service_name: str = "lupis-sdk"
    service_version: str = "1.0.0"
    filter_sensitive_data: bool = True
    sensitive_data_patterns: Optional[List[str]] = None
    redaction_mode: Literal["mask", "remove", "hash"] = "mask"


@dataclass
class TraceData:
    id: str
    project_id: str
    timestamp: int
    input: Dict[str, Any]
    type: str = "http_request"
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    chat_id: Optional[str] = None


ProviderName = Literal["openai", "claude", "cohere", "huggingface", "google", "unknown"]


@dataclass
class NormalizedStreamingResult:
    type: str = "streaming_response"
    provider: ProviderName = "unknown"
    model: Optional[str] = None
    aggregated_text: Optional[str] = None
    data: Optional[List[str]] = None
    tool_calls: Optional[List[Any]] = None
    usage: Optional[Any] = None
    content_type: Optional[str] = None
    total_chunks: Optional[int] = None
    total_length: Optional[int] = None
    is_complete: Optional[bool] = None


@dataclass
class LupisBlockOptions:
    chat_id: Optional[str] = None
    name: Optional[str] = None
    metadata: Optional["LupisMetadata"] = None
    capture_http: bool = True
    capture_console: bool = False


EventProperties = Dict[str, Union[str, int, float, bool, None]]


@dataclass
class LupisMetadata:
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    session_id: Optional[str] = None
    chat_id: Optional[str] = None
    extra: Optional[Dict[str, Union[str, int, float, bool, None]]] = None


@dataclass
class SensitiveDataFilter:
    filter_sensitive_data: bool = True
    sensitive_data_patterns: List[str] = None
    redaction_mode: Literal["mask", "remove", "hash"] = "mask"


@dataclass
class LupisEvent:
    name: str
    timestamp: int
    properties: Optional[EventProperties] = None
    metadata: Optional[LupisMetadata] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert LupisEvent to dictionary for JSON serialization."""
        result = {"name": self.name, "timestamp": self.timestamp}

        if self.properties:
            result["properties"] = self.properties

        if self.metadata:
            metadata_dict = {}
            if self.metadata.user_id:
                metadata_dict["user_id"] = self.metadata.user_id
            if self.metadata.organization_id:
                metadata_dict["organization_id"] = self.metadata.organization_id
            if self.metadata.session_id:
                metadata_dict["session_id"] = self.metadata.session_id
            if self.metadata.chat_id:
                metadata_dict["chat_id"] = self.metadata.chat_id
            if self.metadata.extra:
                metadata_dict.update(self.metadata.extra)
            result["metadata"] = metadata_dict

        return result
