"""Pruebas del comparador de protocolos MTQ vs TCP/UDP."""
from holonet.simulation.benchmarking import (
    BenchmarkConfig,
    ProtocolComparator,
    export_results_csv,
    export_results_html,
)


def test_protocol_comparator_generates_metrics():
    config = BenchmarkConfig(steps=6, step_seconds=0.5, payload_bytes=256, random_seed=123)
    comparator = ProtocolComparator(config)

    results = comparator.run()

    assert len(results) == 3
    protocols = {metric.protocol for metric in results}
    assert protocols == {"Holonet-MTQ", "TCP/IP", "UDP/IP"}
    mtq_metric = next(metric for metric in results if metric.protocol == "Holonet-MTQ")
    assert mtq_metric.latency_ms > 0
    assert 0 <= mtq_metric.failure_rate < 1
    assert mtq_metric.security_index <= 1


def test_export_helpers_generate_files(tmp_path):
    comparator = ProtocolComparator(BenchmarkConfig(steps=4, step_seconds=0.75, payload_bytes=128))
    results = comparator.run()

    csv_path = tmp_path / "benchmark.csv"
    html_path = tmp_path / "benchmark.html"

    export_results_csv(csv_path.as_posix(), results)
    export_results_html(html_path.as_posix(), results)

    csv_content = csv_path.read_text(encoding="utf-8")
    html_content = html_path.read_text(encoding="utf-8")

    assert "Holonet-MTQ" in csv_content
    assert "TCP/IP" in csv_content
    assert "<!DOCTYPE html>" in html_content
    assert "Benchmark Holonet-MTQ vs TCP/UDP" in html_content
