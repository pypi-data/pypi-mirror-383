"""
OpenTelemetry setup per ASPERA Runtime (traces + metrics OTLP).
"""

from __future__ import annotations

import os
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


def init_otel(service_name: str = "aspera-runtime", endpoint: Optional[str] = None) -> None:
    endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    resource = Resource.create({"service.name": service_name})

    # Traces
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    span_exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

    # Metrics
    metric_exporter = OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics")
    reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)



