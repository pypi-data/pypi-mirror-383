from __future__ import annotations

import builtins

from typing import Any, Callable, Dict

import pytest

from lib_log_rich.adapters.structured import journald as journald_module
from lib_log_rich.adapters.structured.journald import JournaldAdapter, Sender
from lib_log_rich.domain.events import LogEvent
from lib_log_rich.domain.levels import LogLevel
from tests.os_markers import LINUX_ONLY, OS_AGNOSTIC

pytestmark = [OS_AGNOSTIC]


@pytest.fixture
def sample_event(event_factory: Callable[[dict[str, object] | None], LogEvent]) -> LogEvent:
    return event_factory({"extra": {"error_code": "E100"}})


RecordedFields = Dict[str, object]


def make_sender(recorded: RecordedFields) -> Sender:
    def _sender(**fields: Any) -> None:
        recorded.update({key: value for key, value in fields.items()})

    return _sender


def test_journald_adapter_emits_uppercase_fields(sample_event: LogEvent) -> None:
    recorded: RecordedFields = {}
    adapter = JournaldAdapter(sender=make_sender(recorded))
    adapter.emit(sample_event)

    assert recorded["MESSAGE"] == sample_event.message
    assert recorded["PRIORITY"] == 6
    assert recorded["JOB_ID"] == sample_event.context.job_id
    assert recorded["LOGGER_NAME"] == sample_event.logger_name
    assert recorded["ERROR_CODE"] == "E100"


def test_journald_adapter_allows_custom_field_prefix(sample_event: LogEvent) -> None:
    recorded: RecordedFields = {}
    adapter = JournaldAdapter(sender=make_sender(recorded), service_field="UNIT")
    adapter.emit(sample_event)

    assert recorded["UNIT"] == sample_event.context.service
    assert "PROCESS_ID_CHAIN" in recorded


def test_journald_adapter_extra_does_not_override_core(sample_event: LogEvent) -> None:
    recorded: RecordedFields = {}
    adapter = JournaldAdapter(sender=make_sender(recorded))
    noisy_event = sample_event.replace(extra={"message": "spoof", "priority": 0})
    adapter.emit(noisy_event)

    assert recorded["MESSAGE"] == sample_event.message
    assert recorded["PRIORITY"] == 6
    assert recorded["EXTRA_MESSAGE"] == "spoof"
    assert recorded["EXTRA_PRIORITY"] == 0


def test_journald_adapter_translates_levels(sample_event: LogEvent) -> None:
    recorded: RecordedFields = {}
    adapter = JournaldAdapter(sender=make_sender(recorded))
    adapter.emit(sample_event.replace(level=LogLevel.ERROR))

    assert recorded["PRIORITY"] == 3


@OS_AGNOSTIC
def test_journald_adapter_requires_systemd(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(journald_module, "_systemd_send", None)
    original_import = builtins.__import__

    def fake_import(
        name: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name.startswith("systemd"):
            raise ModuleNotFoundError("systemd missing")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError, match="systemd.journal is not available"):
        JournaldAdapter()


@LINUX_ONLY
def test_journald_adapter_with_systemd(monkeypatch: pytest.MonkeyPatch, sample_event: LogEvent) -> None:
    journal = pytest.importorskip("systemd.journal")
    captured: RecordedFields = {}

    def fake_send(**fields: Any) -> None:
        captured.update({key: value for key, value in fields.items()})

    monkeypatch.setattr(journal, "send", fake_send)

    adapter = JournaldAdapter()
    adapter.emit(sample_event)

    assert captured["MESSAGE"] == sample_event.message
    assert captured["PRIORITY"] == 6


def test_journald_adapter_custom_service_field(sample_event: LogEvent) -> None:
    captured: dict[str, Any] = {}

    def capture_sender(**fields: Any) -> None:
        captured.update(fields)

    adapter = JournaldAdapter(sender=capture_sender, service_field="unit")
    adapter.emit(sample_event)
    assert captured["UNIT"] == sample_event.context.service


def test_journald_adapter_extra_field_collision(sample_event: LogEvent) -> None:
    event = sample_event.replace(extra={"message": "shadow"})
    captured: dict[str, Any] = {}

    def capture_sender(**fields: Any) -> None:
        captured.update(fields)

    adapter = JournaldAdapter(sender=capture_sender)
    adapter.emit(event)
    assert captured["EXTRA_MESSAGE"] == "shadow"
    assert captured["MESSAGE"] == event.message


def test_journald_adapter_process_id_chain_string(sample_event: LogEvent) -> None:
    class DictContext:
        def to_dict(self, *, include_none: bool = False) -> dict[str, Any]:
            return {
                "service": "svc",
                "environment": "env",
                "job_id": "job",
                "process_id_chain": "1>2",
            }

    captured: dict[str, Any] = {}

    def capture_sender(**fields: Any) -> None:
        captured.update(fields)

    adapter = JournaldAdapter(sender=capture_sender)
    mutated = sample_event.replace()
    object.__setattr__(mutated, "context", DictContext())
    adapter.emit(mutated)
    assert captured["PROCESS_ID_CHAIN"] == "1>2"
