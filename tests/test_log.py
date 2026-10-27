"""Tests for the shared logging helper (formatted output, not just the filter)."""

from __future__ import annotations

import asyncio
import importlib
import io
import logging
import re
import time
from collections.abc import Iterator

import pytest

import routesmart
from routesmart.log import (
    LOG_LEVEL_ENV_VAR,
    ROOT_LOGGER_NAME,
    configure_logging,
    ensure_redacting_handler,
    get_logger,
    redact,
    sanitize_url,
)

LINE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z (\w+) (\S+): (.*)$")
SENTINEL = "S3CR3T-VALUE-123"


def _strip_routesmart_handlers() -> None:
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    logger.setLevel(logging.NOTSET)
    logger.propagate = True


@pytest.fixture(autouse=True)
def _reset_routesmart_logger() -> Iterator[None]:
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    saved = (list(logger.handlers), logger.level, logger.propagate)
    yield
    logger.handlers[:] = saved[0]
    logger.setLevel(saved[1])
    logger.propagate = saved[2]


def _configured(level: int | str = "INFO") -> tuple[io.StringIO, logging.Logger]:
    stream = io.StringIO()
    configure_logging(level, stream=stream)
    return stream, get_logger("probe")


# --- format and configuration ---------------------------------------------------


def test_format_has_utc_timestamp_level_and_service() -> None:
    stream = io.StringIO()
    configure_logging("INFO", stream=stream)
    get_logger("flight").info("fetched %d options", 3)
    (line,) = stream.getvalue().splitlines()
    match = LINE.match(line)
    assert match is not None
    assert match.groups() == ("INFO", "routesmart.flight", "fetched 3 options")


def test_level_filters_lower_records() -> None:
    stream, log = _configured("WARNING")
    log.info("hidden")
    log.warning("shown")
    assert len(stream.getvalue().splitlines()) == 1


def test_repeated_configuration_does_not_duplicate_output() -> None:
    stream = io.StringIO()
    configure_logging(stream=stream)
    configure_logging(stream=stream)
    for _ in range(3):
        get_logger("road")
    get_logger("road").info("once")
    assert len(stream.getvalue().splitlines()) == 1
    assert len(logging.getLogger(ROOT_LOGGER_NAME).handlers) == 1


def test_records_do_not_propagate_and_root_is_untouched() -> None:
    root = logging.getLogger()
    before = (list(root.handlers), root.level)
    configure_logging(stream=io.StringIO())
    get_logger("rail")
    assert logging.getLogger(ROOT_LOGGER_NAME).propagate is False
    assert (list(root.handlers), root.level) == before


def test_level_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(LOG_LEVEL_ENV_VAR, "error")
    configure_logging(stream=io.StringIO())
    assert logging.getLogger(ROOT_LOGGER_NAME).level == logging.ERROR


def test_explicit_level_overrides_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(LOG_LEVEL_ENV_VAR, "ERROR")
    configure_logging(logging.DEBUG, stream=io.StringIO())
    assert logging.getLogger(ROOT_LOGGER_NAME).level == logging.DEBUG


def test_default_level_is_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(LOG_LEVEL_ENV_VAR, raising=False)
    configure_logging(stream=io.StringIO())
    assert logging.getLogger(ROOT_LOGGER_NAME).level == logging.INFO


@pytest.mark.parametrize("level", ["VERBOSE", "", "  "])
def test_unknown_level_is_rejected(level: str) -> None:
    with pytest.raises(ValueError, match="unknown log level"):
        configure_logging(level, stream=io.StringIO())


@pytest.mark.parametrize("service", ["flight", "rail.irctc_free", "a1"])
def test_valid_service_names(service: str) -> None:
    assert get_logger(service).name == f"routesmart.{service}"


@pytest.mark.parametrize("service", ["", "Flight", "1rail", "road..x", "road.", "a b", "../x"])
def test_invalid_service_names(service: str) -> None:
    with pytest.raises(ValueError, match="invalid service name"):
        get_logger(service)


# --- H1: malformed calls never raise into application code -----------------------


@pytest.mark.parametrize(
    ("template", "args"),
    [
        ("count %d", (SENTINEL,)),
        ("%s and %s", (SENTINEL,)),
        ("%(missing)s", ({"other": SENTINEL},)),
        ("no placeholders", ("extra", SENTINEL)),
    ],
)
def test_malformed_format_does_not_raise_and_drops_arguments(
    template: str, args: tuple[object, ...]
) -> None:
    stream, log = _configured()
    log.warning(template, *args)  # must not raise
    output = stream.getvalue()
    assert "<unformattable log message:" in output
    assert repr(template) in output
    assert SENTINEL not in output


def test_malformed_template_with_secret_is_redacted() -> None:
    stream, log = _configured()
    log.warning("api_key=" + SENTINEL + " count %d", "x")
    assert SENTINEL not in stream.getvalue()
    assert "<unformattable log message: TypeError" in stream.getvalue()


class _Exploding:
    def __str__(self) -> str:
        raise RuntimeError(SENTINEL)


def test_message_object_whose_str_raises_is_reported_without_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    stream, log = _configured()
    log.warning(_Exploding())  # must not raise
    captured = capsys.readouterr()
    assert "routesmart logging error: RuntimeError" in captured.err
    assert SENTINEL not in captured.err + captured.out + stream.getvalue()


# --- H2/H3: confidentiality of formatted output ------------------------------------


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (f'{{"api_key": "{SENTINEL}"}}', '{"api_key": "***"}'),
        (f"{{'password': '{SENTINEL}'}}", "{'password': '***'}"),
        (f"access_token={SENTINEL}", "access_token=***"),
        (f"refresh_token={SENTINEL}", "refresh_token=***"),
        (f"client_secret={SENTINEL}", "client_secret=***"),
        (f"key={SENTINEL}", "key=***"),
        (f"password='{SENTINEL}'", "password='***'"),
        (f"password = {SENTINEL}, user=x", "password = ***, user=x"),
        (f"Authorization: Bearer {SENTINEL}", "Authorization: Bearer ***"),
        (f"header Bearer {SENTINEL}", "header Bearer ***"),
        (f"X-Api-Key: {SENTINEL}", "X-Api-Key: ***"),
        (f"https://user:{SENTINEL}@db.example.com/x", "https://***@db.example.com/x"),
        (f"GET /v1?apikey={SENTINEL}&q=BLR", "GET /v1?apikey=***&q=BLR"),
        ("jwt eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYWRtaW4ifQ.c2lnbmF0dXJl", "jwt ***"),
        ("no secrets here", "no secrets here"),
        ("", ""),
    ],
)
def test_known_secret_forms_are_redacted_in_formatted_output(message: str, expected: str) -> None:
    stream, log = _configured()
    log.info("%s", message)
    (line,) = stream.getvalue().splitlines() or [""]
    match = LINE.match(line)
    assert match is not None
    assert match.group(3) == expected
    assert redact(message) == expected


def test_traceback_and_exception_message_are_redacted() -> None:
    stream, log = _configured()
    try:
        raise RuntimeError(f"upstream failed for https://api.example.com/v1?api_key={SENTINEL}")
    except RuntimeError:
        log.exception("call failed")
    output = stream.getvalue()
    assert "Traceback (most recent call last)" in output
    assert "RuntimeError: upstream failed" in output
    assert SENTINEL not in output


def test_stack_info_is_redacted() -> None:
    stream, log = _configured()
    token = f"token={SENTINEL}"
    log.warning("context %s", token, stack_info=True)
    assert "Stack (most recent call last)" in stream.getvalue()
    assert SENTINEL not in stream.getvalue()


def test_records_before_configuration_are_redacted_and_not_lost(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _strip_routesmart_handlers()
    root = logging.getLogger()
    root_before = (list(root.handlers), root.level)
    get_logger("early").warning("api_key=%s", SENTINEL)
    captured = capsys.readouterr()
    assert "routesmart.early: api_key=***" in captured.err
    assert SENTINEL not in captured.err + captured.out
    assert (list(root.handlers), root.level) == root_before


def test_configure_replaces_the_early_handler() -> None:
    _strip_routesmart_handlers()
    get_logger("early")
    stream, log = _configured()
    log.info("after")
    assert len(logging.getLogger(ROOT_LOGGER_NAME).handlers) == 1
    assert "after" in stream.getvalue()


# Adversarial inputs, including the Round 2 reviewer's quadratic JWT trigger ("eyJ-" * n).
# Each payload is ~400 KB. Before the N1 fix, "eyJ-" * 100_000 alone would take on the
# order of a minute (11 s at 160 KB, quadratic growth). The fixed patterns take tens of
# milliseconds, so the generous per-payload budget is not a fragile timing threshold.
_ADVERSARIAL_PAYLOADS = {
    "jwt-restarts": "eyJ-" * 100_000,
    "jwt-like-segments": "eyJaaaaa." * 45_000,
    "dotted-words": "a." * 200_000,
    "key-then-spaces": "key" + " " * 400_000 + "x",
    "repeated-key-space": "key " * 100_000,
    "unclosed-quotes": 'key="' * 80_000,
    "scheme-fragments": "a://" * 100_000,
    "bearer-words": "Bearer " * 60_000,
    "long-key-runs": ("a" * 63 + "key =") * 6_000,
    "single-token": "x" * 400_000,
}


@pytest.mark.parametrize("name", sorted(_ADVERSARIAL_PAYLOADS))
def test_redaction_completes_quickly_on_adversarial_input(name: str) -> None:
    payload = _ADVERSARIAL_PAYLOADS[name]
    start = time.perf_counter()
    redact(payload)
    assert time.perf_counter() - start < 5.0, name


def test_jwt_match_starts_only_at_a_token_boundary() -> None:
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYWRtaW4ifQ.c2lnbmF0dXJl"
    assert redact(f"id {jwt}") == "id ***"
    assert redact(f"id:{jwt}") == "id:***"
    # Documented limit: a JWT glued to a preceding base64url character is not matched by the
    # JWT rule (this is what keeps the scan linear). A key or scheme still catches common uses.
    assert redact(f"x-{jwt}") == f"x-{jwt}"
    assert redact(f"token={jwt}") == "token=***"
    assert redact(f"Bearer {jwt}") == "Bearer ***"


@pytest.mark.parametrize(
    "key",
    [
        "password",
        "PASSWD",
        "client_secret",
        "x-api-key",
        "access.token",
        "sessionid",
        "my_signature",
    ],
)
def test_sensitive_key_suffixes_are_redacted(key: str) -> None:
    assert redact(f"{key}={SENTINEL}") == f"{key}=***"


@pytest.mark.parametrize("text", ["monkeys=3", "keyboard=us", "tokens=5", "keynote=x"])
def test_keys_not_ending_in_a_sensitive_suffix_are_kept(text: str) -> None:
    assert redact(text) == text


def test_key_longer_than_64_characters_is_not_treated_as_a_key() -> None:
    text = "a" * 70 + "key=value"
    assert redact(text) == text


# --- N2: direct stdlib loggers in the routesmart hierarchy --------------------------


def test_direct_stdlib_logger_is_redacted_after_package_import(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _strip_routesmart_handlers()
    importlib.reload(routesmart)  # re-runs the package import side effect
    logging.getLogger("routesmart.adapters.flight").warning("api_key=%s", SENTINEL)
    captured = capsys.readouterr()
    assert "routesmart.adapters.flight: api_key=***" in captured.err
    assert SENTINEL not in captured.err + captured.out


def test_direct_stdlib_logger_is_redacted_after_configuration() -> None:
    stream, _ = _configured()
    logging.getLogger("routesmart.adapters.rail").info("token=%s", SENTINEL)
    assert "routesmart.adapters.rail: token=***" in stream.getvalue()
    assert SENTINEL not in stream.getvalue()


def test_package_import_never_modifies_the_root_logger() -> None:
    root = logging.getLogger()
    before = (list(root.handlers), root.level)
    _strip_routesmart_handlers()
    importlib.reload(routesmart)
    assert (list(root.handlers), root.level) == before
    assert logging.getLogger(ROOT_LOGGER_NAME).propagate is False


def test_importing_routesmart_configures_the_routesmart_logger() -> None:
    # Documented side effect (D-IMPL-04 approval condition): the package import installs
    # exactly one RouteSmart redacting handler and stops propagation to the root logger.
    _strip_routesmart_handlers()
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    assert (logger.handlers, logger.propagate) == ([], True)
    importlib.reload(routesmart)
    assert len(logger.handlers) == 1
    assert type(logger.handlers[0]).__name__ == "_RedactingStreamHandler"
    assert logger.propagate is False
    assert logger.level == logging.NOTSET  # level is left to configure_logging()


def test_ensure_redacting_handler_is_idempotent() -> None:
    _strip_routesmart_handlers()
    for _ in range(3):
        ensure_redacting_handler()
    assert len(logging.getLogger(ROOT_LOGGER_NAME).handlers) == 1


def test_loggers_outside_the_hierarchy_are_not_touched() -> None:
    other = logging.getLogger("thirdparty.client")
    before = (list(other.handlers), other.propagate)
    ensure_redacting_handler()
    assert (list(other.handlers), other.propagate) == before


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://user:pw@API.example.com:8443/v1/x?api_key=K&q=BLR#frag",
            "https://api.example.com:8443/v1/x?api_key=***&q=***",
        ),
        ("https://example.com/path", "https://example.com/path"),
        ("https://example.com/?flag", "https://example.com/?flag=***"),
        ("http://[::1]:8080/x?token=t", "http://[::1]:8080/x?token=***"),
        ("http://[::1]:99999/", "<unparseable url>"),
        ("", ""),
        # N9: token-like path segments (>= 20 chars of [A-Za-z0-9._~:+=-] with a letter and digit)
        (
            "https://api.telegram.org/bot1234567890:AAFakeFakeFakeFakeFakeFakeFake/sendMessage",
            "https://api.telegram.org/***/sendMessage",
        ),
        (
            "https://example.com/v1/items/123e4567-e89b-12d3-a456-426614174000",
            "https://example.com/v1/items/***",
        ),
        (
            "https://example.com/t/eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYWRtaW4ifQ.c2lnbmF0dXJl",
            "https://example.com/t/***",
        ),
        ("https://example.com/files;token=abc/x", "https://example.com/files;token=***/x"),
        ("https://example.com/v1/flights/AI-123", "https://example.com/v1/flights/AI-123"),
        # Documented limits: short or letters-only path secrets are not detected.
        ("https://example.com/k/abc123", "https://example.com/k/abc123"),
        (
            "https://example.com/k/onlylettersbutverylongsegment",
            "https://example.com/k/onlylettersbutverylongsegment",
        ),
    ],
)
def test_sanitize_url(url: str, expected: str) -> None:
    assert sanitize_url(url) == expected


@pytest.mark.asyncio
async def test_concurrent_async_logging_keeps_every_record() -> None:
    stream, log = _configured()

    async def worker(index: int) -> None:
        await asyncio.sleep(0)
        log.info("worker %d done", index)

    await asyncio.gather(*(worker(i) for i in range(50)))
    lines = stream.getvalue().splitlines()
    assert len(lines) == 50
    assert {line.rsplit(" ", 2)[-2] for line in lines} == {str(i) for i in range(50)}
