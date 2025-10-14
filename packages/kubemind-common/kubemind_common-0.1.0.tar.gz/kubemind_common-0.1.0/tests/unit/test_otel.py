from kubemind_common.otel.setup import setup_otel


def test_setup_otel_noop_without_deps():
    # Should not raise even if otel packages are not installed
    setup_otel(service_name="kubemind-test", exporter_endpoint="http://localhost:4318")

