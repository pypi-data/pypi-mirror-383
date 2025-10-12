"""Pruebas para los adaptadores de overlay MTQ."""
from __future__ import annotations

from holonet.network import (
    LocalMTQHop,
    MTQOverlaySession,
    OverlayAdapter,
    WireGuardAdapter,
    ZeroTierAdapter,
)
from holonet.transmission import OpticalFrame


def _make_frame() -> OpticalFrame:
    frame = OpticalFrame(payload=b"demo", wavelength_nm=1550.0)
    frame.encapsulate_tcp_ip("192.168.1.10", "192.168.1.20", 5000, 5001)
    return frame


def test_overlay_adapter_routes_frames() -> None:
    adapter = ZeroTierAdapter(name="zerotier", network_id="8056c2e21c000001")
    adapter.connect_peer("peer-1", "10.0.0.1")

    frame = _make_frame()
    adapter.send_frame("peer-1", frame)

    assert adapter.routed_frames == [("peer-1", frame)]
    assert adapter.connected_peers["peer-1"].startswith("zt://8056c2e21c000001/")


def test_overlay_session_transmit_to_all_hops() -> None:
    adapter = WireGuardAdapter(name="wireguard", tunnel_name="wg-mtq")
    session = MTQOverlaySession(adapter)
    session.register_hop("hop-a", "fd00::1")
    session.register_hop("hop-b", "fd00::2")

    frame = _make_frame()
    delivered = session.transmit(frame)

    assert delivered == ["hop-a", "hop-b"]
    assert len(adapter.routed_frames) == 2


def test_local_mtq_hops_chain_processing() -> None:
    adapter = OverlayAdapter(name="local-overlay")
    session = MTQOverlaySession(adapter)
    hop_a = LocalMTQHop("raspi-1", adapter)
    hop_b = LocalMTQHop("server-1", adapter)

    hop_a.attach("10.0.0.10")
    hop_b.attach("10.0.0.20")
    session.register_hop(hop_a.hop_id, hop_a.address or "")
    session.register_hop(hop_b.hop_id, hop_b.address or "")

    frame = _make_frame()
    delivered = session.transmit(frame)

    for peer_id, routed_frame in adapter.routed_frames:
        if peer_id == hop_a.hop_id:
            summary = hop_a.process(routed_frame)
            assert summary["overlay"] == adapter.name
            hop_a.forward(hop_b.hop_id, routed_frame)
        if peer_id == hop_b.hop_id:
            hop_b.process(routed_frame)

    assert delivered == [hop_a.hop_id, hop_b.hop_id]
    assert len(hop_a.processed_frames) == 1
    assert len(hop_b.processed_frames) >= 1
