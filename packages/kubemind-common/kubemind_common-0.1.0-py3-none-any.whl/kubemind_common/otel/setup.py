from __future__ import annotations

import os
from typing import Optional


def setup_otel(service_name: str, exporter_endpoint: Optional[str] = None) -> None:
    """Set up basic OpenTelemetry tracing/export.

    This function is safe to call even if otel deps are not installed; it no-ops.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        endpoint = exporter_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
    except Exception:
        # Otel not installed or exporter unavailable; ignore
        return

