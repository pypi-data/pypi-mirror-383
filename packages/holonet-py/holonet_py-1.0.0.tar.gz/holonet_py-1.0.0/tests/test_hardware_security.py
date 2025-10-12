"""Pruebas de hardware simulado y guardia leptónica."""
from datetime import datetime, timedelta, timezone

from datetime import datetime, timedelta, timezone

from holonet.core.packets import LeptonicPattern, MuonPacket
from holonet.hardware.induction_driver import DeviceRegistry, InductionDevice
from holonet.security.leptonic_guard import LeptonicGuard
from holonet.security.token_store import TokenRecord, TokenStoreProtocol


class StubTokenStore(TokenStoreProtocol):
    """Almacén stub para inspeccionar llamadas en las pruebas."""

    def __init__(self) -> None:
        self.tokens: dict[str, TokenRecord] = {}
        self.store_calls: list[tuple[str, str]] = []
        self.retrieve_calls: list[str] = []
        self.revoked: list[str] = []

    def store(self, node_id: str, token: str, expires_at: datetime | None = None) -> None:
        self.store_calls.append((node_id, token))
        self.tokens[node_id] = TokenRecord(token=token, expires_at=expires_at)

    def retrieve(self, node_id: str) -> TokenRecord | None:
        self.retrieve_calls.append(node_id)
        return self.tokens.get(node_id)

    def revoke(self, node_id: str) -> None:
        self.revoked.append(node_id)
        self.tokens.pop(node_id, None)


def test_device_registry_and_sense():
    registry = DeviceRegistry()
    device = InductionDevice("dev1", calibration_factor=2.0)
    registry.register(device)
    pattern = LeptonicPattern("p", [1.0])
    signal = pattern.to_signal(1.0)
    assert registry.list_devices()["dev1"] == 2.0
    assert device.sense(signal) == signal.intensity() * 2.0


def test_device_calibration_history():
    registry = DeviceRegistry()
    device = InductionDevice("dev1", calibration_factor=1.0)
    registry.register(device)

    reference = datetime(2024, 1, 1, tzinfo=timezone.utc)
    device.update_calibration(reference - timedelta(hours=1), 1.5)
    device.update_calibration(reference + timedelta(hours=1), 3.0)

    pattern = LeptonicPattern("p", [1.0, 0.5])
    signal_mid = pattern.to_signal(1.0, {"timestamp": reference.isoformat()})
    signal_future = pattern.to_signal(1.0, {"timestamp": (reference + timedelta(hours=2)).isoformat()})
    signal_without_timestamp = pattern.to_signal(1.0)

    assert device.sense(signal_mid) == signal_mid.intensity() * 1.5
    assert device.sense(signal_future) == signal_future.intensity() * 3.0
    assert device.sense(signal_without_timestamp) == signal_without_timestamp.intensity() * 3.0
    assert registry.list_devices()["dev1"] == 3.0


def test_leptonic_guard_token_with_stub():
    store = StubTokenStore()
    guard = LeptonicGuard(store=store)
    guard.register_shared_secret("node", "Super-Secreta123!")
    token = guard.issue_token("node", "Super-Secreta123!")
    pattern = LeptonicPattern("p", [1.0])
    packet = pattern.to_signal(1.0)
    muon_packet = MuonPacket(b"data", packet)

    assert store.store_calls == [("node", token)]
    assert guard.verify("node", token, muon_packet)
    assert store.retrieve_calls[-1] == "node"

    packet_negative = pattern.to_signal(-1.0)
    muon_packet_negative = MuonPacket(b"data", packet_negative)
    assert not guard.verify("node", token, muon_packet_negative)
