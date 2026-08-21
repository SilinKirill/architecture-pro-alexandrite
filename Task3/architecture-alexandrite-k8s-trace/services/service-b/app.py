import os

from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing() -> None:
    provider = TracerProvider(
        resource=Resource.create({"service.name": "service-b"})
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


@app.get("/")
def index():
    return {
        "service": "service-b",
        "result": "ok",
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)