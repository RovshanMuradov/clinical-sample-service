import asyncio
import logging
import uuid

import pytest

from app.core import logging as log_mod


@pytest.fixture(autouse=True)
def clean_root_logger():
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    yield
    for h in root.handlers[:]:
        root.removeHandler(h)
    for h in old_handlers:
        root.addHandler(h)


def _basic_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "secret")


def test_setup_logging_structured(tmp_path, monkeypatch):
    _basic_env(monkeypatch)
    log_file = tmp_path / "service.log"
    log_mod.setup_logging(
        log_level="DEBUG",
        log_file=str(log_file),
        enable_rotation=False,
        structured_logging=True,
    )
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)
    assert any(isinstance(h, logging.FileHandler) for h in root.handlers)
    assert any(isinstance(h.formatter, log_mod.StructuredFormatter) for h in root.handlers)
    root.info("hello")
    assert log_file.exists()


def test_correlation_id_utilities():
    log_mod.set_correlation_id("abc")
    assert log_mod.get_correlation_id() == "abc"
    new_id = log_mod.generate_correlation_id()
    uuid.UUID(new_id)
    # existing correlation id should remain unchanged
    assert log_mod.get_correlation_id() == "abc"
    log_mod.set_correlation_id("")
    assert log_mod.get_correlation_id() == ""


@pytest.mark.asyncio
async def test_correlation_id_async_propagation():
    log_mod.set_correlation_id("cid")

    async def nested():
        await asyncio.sleep(0)
        return log_mod.get_correlation_id()

    assert await nested() == "cid"


def test_log_error(caplog):
    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("boom")
        except ValueError as exc:
            log_mod.log_error(exc, {"foo": "bar"})
    record = caplog.records[0]
    assert record.error_type == "ValueError"
    assert record.context == {"foo": "bar"}
    assert record.exc_info


def test_log_request_and_response(caplog):
    headers = {"Authorization": "secret", "User-Agent": "tester", "x-forwarded-for": "1.1.1.1"}
    with caplog.at_level(logging.INFO):
        log_mod.log_request("POST", "/unit", headers, body={"password": "x", "a": 1})
        log_mod.log_response(200, 0.123, 10)
    req = caplog.records[0]
    resp = caplog.records[1]
    assert req.event == "request_received"
    assert req.method == "POST"
    assert "password" not in req.body
    assert resp.status_code == 200
    assert resp.response_size_bytes == 10
