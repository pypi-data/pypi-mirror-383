"""Span processor for ABV OpenTelemetry integration.

This module defines the ABVSpanProcessor class, which extends OpenTelemetry's
BatchSpanProcessor with ABV-specific functionality. It handles exporting
spans to the ABV API with proper authentication and filtering.

Key features:
- HTTP-based span export to ABV API
- Bearer token authentication with ABV API key
- Configurable batch processing behavior
- Project-scoped span filtering to prevent cross-project data leakage
"""

import os
from typing import Dict, List, Optional

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from abvdev._client.constants import ABV_TRACER_NAME
from abvdev._client.environment_variables import (
    ABV_FLUSH_AT,
    ABV_FLUSH_INTERVAL,
)
from abvdev._client.utils import span_formatter
from abvdev.logger import abv_logger
from abvdev.version import __version__ as abv_version


class ABVSpanProcessor(BatchSpanProcessor):
    """OpenTelemetry span processor that exports spans to the ABV API.

    This processor extends OpenTelemetry's BatchSpanProcessor with ABV-specific functionality:
    1. Project-scoped span filtering to prevent cross-project data leakage
    2. Instrumentation scope filtering to block spans from specific libraries/frameworks
    3. Configurable batch processing parameters for optimal performance
    4. HTTP-based span export to the ABV OTLP endpoint
    5. Debug logging for span processing operations
    6. Authentication with ABV API using Bearer token

    The processor is designed to efficiently handle large volumes of spans with
    minimal overhead, while ensuring spans are only sent to the correct project.
    It integrates with OpenTelemetry's standard span lifecycle, adding ABV-specific
    filtering and export capabilities.
    """

    def __init__(
        self,
        *,
        api_key: str,
        host: str,
        timeout: Optional[int] = None,
        flush_at: Optional[int] = None,
        flush_interval: Optional[float] = None,
        blocked_instrumentation_scopes: Optional[List[str]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ):
        self.api_key = api_key
        self.blocked_instrumentation_scopes = (
            blocked_instrumentation_scopes
            if blocked_instrumentation_scopes is not None
            else []
        )

        env_flush_at = os.environ.get(ABV_FLUSH_AT, None)
        flush_at = flush_at or int(env_flush_at) if env_flush_at is not None else None

        env_flush_interval = os.environ.get(ABV_FLUSH_INTERVAL, None)
        flush_interval = (
            flush_interval or float(env_flush_interval)
            if env_flush_interval is not None
            else None
        )

        bearer_auth_header = f"Bearer {api_key}"

        # Prepare default headers
        default_headers = {
            "Authorization": bearer_auth_header,
            "x_abv_sdk_name": "python",
            "x_abv_sdk_version": abv_version,
        }

        # Merge additional headers if provided
        headers = {**default_headers, **(additional_headers or {})}

        abv_span_exporter = OTLPSpanExporter(
            endpoint=f"{host}/api/public/otel/v1/traces",
            headers=headers,
            timeout=timeout,
        )

        super().__init__(
            span_exporter=abv_span_exporter,
            export_timeout_millis=timeout * 1_000 if timeout else None,
            max_export_batch_size=flush_at,
            schedule_delay_millis=flush_interval * 1_000
            if flush_interval is not None
            else None,
        )

    def on_end(self, span: ReadableSpan) -> None:
        # Only export spans that belong to the scoped project
        # This is important to not send spans to wrong project in multi-project setups
        if self._is_abv_span(span) and not self._is_abv_project_span(span):
            abv_logger.debug(
                f"Security: Span rejected - belongs to project '{span.instrumentation_scope.attributes.get('api_key') if span.instrumentation_scope and span.instrumentation_scope.attributes else None}' but processor is for '{self.api_key}'. "
                f"This prevents cross-project data leakage in multi-project environments."
            )
            return

        # Do not export spans from blocked instrumentation scopes
        if self._is_blocked_instrumentation_scope(span):
            return

        abv_logger.debug(
            f"Trace: Processing span name='{span._name}' | Full details:\n{span_formatter(span)}"
        )

        super().on_end(span)

    @staticmethod
    def _is_abv_span(span: ReadableSpan) -> bool:
        return (
            span.instrumentation_scope is not None
            and span.instrumentation_scope.name == ABV_TRACER_NAME
        )

    def _is_blocked_instrumentation_scope(self, span: ReadableSpan) -> bool:
        return (
            span.instrumentation_scope is not None
            and span.instrumentation_scope.name in self.blocked_instrumentation_scopes
        )

    def _is_abv_project_span(self, span: ReadableSpan) -> bool:
        if not ABVSpanProcessor._is_abv_span(span):
            return False

        if span.instrumentation_scope is not None:
            api_key_on_span = (
                span.instrumentation_scope.attributes.get("api_key", None)
                if span.instrumentation_scope.attributes
                else None
            )

            return api_key_on_span == self.api_key

        return False
