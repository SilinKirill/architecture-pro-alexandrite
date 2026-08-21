import os

import requests
from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing() -> None:
    provider = TracerProvider(
        resource=Resource.create({"service.name": "service-a"})
    )
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(
        endpoint=os.getenv(
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "http://simplest-collector:4318/v1/traces",
        )
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))


configure_tracing()

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8080/")


@app.get("/")
def index():
    response = requests.get(SERVICE_B_URL, timeout=5)
    response.raise_for_status()

    return {
        "service": "service-a",
        "service_b": response.json(),
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)