"""Shared logging helper built on the standard library ``logging`` module.

Every module gets its logger with ``get_logger("<service>")``. The entry point
calls ``configure_logging()`` once. Records carry a UTC timestamp, the level and
the service logger name, for example::

    2026-10-27T11:40:00.123Z INFO routesmart.flight: fetched 3 options

Confidentiality model (see ``docs/LOGGING.md``):

* Callers must keep secrets and personal travel data out of log calls. Use
  ``sanitize_url()`` before logging a URL, and log exception *types* rather
  than full provider responses.
* As defence in depth, every RouteSmart handler redacts its **fully formatted
  output**, including exception tracebacks and stack info, using
  ``redact()``. Redaction is pattern-based and cannot recognise arbitrary
  secrets.
* Importing the ``routesmart`` package installs the redacting handler on the
  ``routesmart`` logger (``ensure_redacting_handler()``). Every
  ``routesmart.*`` record, including ones from plain
  ``logging.getLogger(__name__)`` inside the package, is therefore redacted
  even before ``configure_logging()`` (WARNING and above, to stderr), and never
  reaches Python's unredacted last-resort handler. Loggers outside the
  ``routesmart`` hierarchy are not covered.
* A malformed log call never raises into application code, and never echoes
  its arguments.
"""

from __future__ import annotations

import contextlib
import logging
import os
import re
import sys
import time
from typing import Final, TextIO, override
from urllib.parse import urlsplit, urlunsplit

ROOT_LOGGER_NAME: Final = "routesmart"
LOG_LEVEL_ENV_VAR: Final = "ROUTESMART_LOG_LEVEL"
LOG_FORMAT: Final = "%(asctime)s.%(msecs)03dZ %(levelname)s %(name)s: %(message)s"
DATE_FORMAT: Final = "%Y-%m-%dT%H:%M:%S"
REDACTED: Final = "***"

_SERVICE_NAME = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")

# Key names whose values are treated as secrets: any key that *ends* with one of these
# suffixes (so access_token, client_secret, x-api-key, primary_key, ... all count).
_SENSITIVE_KEY_SUFFIXES: Final = (
    "password",
    "passwd",
    "passphrase",
    "pwd",
    "secret",
    "token",
    "key",
    "authorization",
    "auth",
    "credential",
    "credentials",
    "cookie",
    "sessionid",
    "session_id",
    "session-id",
    "signature",
)
_ENDS_WITH_SENSITIVE_SUFFIX = "|".join(f"(?<={re.escape(s)})" for s in _SENSITIVE_KEY_SUFFIXES)
# key=value, key: value, "key": "value", key='value', key = Bearer value, ...
# Linear-time by construction: a key may start only at the beginning of a [\w.-] run
# (negative lookbehind), the run is taken possessively (at most 64 characters), the
# suffix is checked with fixed-width lookbehinds, and every later quantifier is
# possessive, so nothing backtracks.
_SECRET_ASSIGNMENT = re.compile(
    rf"""(?P<kq>["']?)(?<![\w.-])(?P<key>[\w.-]{{1,64}}+)(?:{_ENDS_WITH_SENSITIVE_SUFFIX})(?P=kq)
    (?P<sep>\s*+[:=]\s*+)
    (?:"(?P<dq>[^"]*+)"|'(?P<sq>[^']*+)'|(?P<scheme>(?:bearer|basic|token)\s++)?(?P<bare>[^\s"',;&}}\]]++))""",
    re.IGNORECASE | re.VERBOSE,
)
_BARE_AUTH_SCHEME = re.compile(
    r"\b(?P<scheme>bearer|basic)\s+[A-Za-z0-9._~+/=-]{8,}", re.IGNORECASE
)
_URL_USERINFO = re.compile(r"\b(?P<scheme>[a-z][a-z0-9+.-]{0,20}://)[^/\s@]+@", re.IGNORECASE)
# The negative lookbehind allows a match to start only at the beginning of a
# base64url run, and the possessive quantifiers forbid backtracking. Together they
# keep the scan linear: without them, "eyJ-" * n restarts at every "eyJ" (O(n^2)).
_JWT = re.compile(r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{5,}+\.[A-Za-z0-9_-]{5,}+\.[A-Za-z0-9_-]*+")
# A URL path segment is treated as a credential if it is long and mixes letters and
# digits (API tokens, bot tokens, signed IDs). Short or letters-only secrets are not detected.
_TOKEN_LIKE_SEGMENT = re.compile(r"[A-Za-z0-9._~:+=-]{20,}+")

_HANDLER_MARKER: Final = "_routesmart_handler"
_MALFORMED_CALL_ERRORS: Final = (TypeError, ValueError, KeyError, IndexError)


def _utc_time(seconds: float | None) -> time.struct_time:
    return time.gmtime(seconds)


def _mask_assignment(match: re.Match[str]) -> str:
    quote = match["kq"]
    prefix = f"{quote}{match['key']}{quote}{match['sep']}"
    if match["dq"] is not None:
        return f'{prefix}"{REDACTED}"'
    if match["sq"] is not None:
        return f"{prefix}'{REDACTED}'"
    return f"{prefix}{match['scheme'] or ''}{REDACTED}"


def redact(text: str) -> str:
    """Mask common secret patterns in ``text``.

    Covers: values of secret-like keys in ``key=value``, ``key: value`` and
    JSON/quoted forms; ``Bearer``/``Basic`` credentials; URL userinfo
    (``scheme://user:pass@host``); and JWT-shaped tokens. Arbitrary secrets
    that match none of these patterns are **not** detected.

    Args:
        text: Text that may contain secrets.

    Returns:
        The text with matched secret values replaced by ``***``.
    """
    text = _URL_USERINFO.sub(lambda m: f"{m['scheme']}{REDACTED}@", text)
    text = _SECRET_ASSIGNMENT.sub(_mask_assignment, text)
    text = _BARE_AUTH_SCHEME.sub(lambda m: f"{m['scheme']} {REDACTED}", text)
    return _JWT.sub(REDACTED, text)


def _looks_like_token(segment: str) -> bool:
    return (
        _TOKEN_LIKE_SEGMENT.fullmatch(segment) is not None
        and any(c.isdigit() for c in segment)
        and any(c.isalpha() for c in segment)
    )


def _sanitize_path(path: str) -> str:
    segments = path.split("/")
    return "/".join(
        REDACTED if _looks_like_token(segment) else redact(segment) for segment in segments
    )


def sanitize_url(url: str) -> str:
    """Return a reduced-risk version of ``url`` for logging.

    Exactly what it does:

    * Drops userinfo (``user:pass@``) and the fragment.
    * Keeps the scheme, host and port.
    * Keeps query parameter names and replaces every query value with ``***``.
    * Replaces token-like path segments with ``***``: segments of 20 or more
      characters from ``[A-Za-z0-9._~:+=-]`` that contain both a letter and a
      digit (e.g. API or bot tokens, UUIDs, signed IDs).
    * Applies ``redact()`` to every other path segment (JWTs, ``key=value``).

    It does **not** detect short or letters-only secrets in the path, secrets in
    the host name, or percent-encoded secrets. Avoid putting such URLs in logs
    at all.

    Args:
        url: Any URL string.

    Returns:
        The sanitised URL, or ``"<unparseable url>"`` if it cannot be parsed.
    """
    try:
        parts = urlsplit(url)
        host = parts.hostname or ""
        port = parts.port
    except ValueError:
        return "<unparseable url>"
    netloc = f"[{host}]" if ":" in host else host
    if port is not None:
        netloc = f"{netloc}:{port}"
    names = [pair.split("=", 1)[0] for pair in parts.query.split("&") if pair]
    query = "&".join(f"{name}={REDACTED}" for name in names)
    return urlunsplit((parts.scheme, netloc, _sanitize_path(parts.path), query, ""))


class RedactingFormatter(logging.Formatter):
    """UTC formatter that redacts the complete formatted record.

    Redaction is applied after the message, exception traceback and stack info
    have been rendered, so secrets inside exception text are masked too.
    """

    def __init__(self) -> None:
        """Create the formatter with the shared RouteSmart format."""
        super().__init__(LOG_FORMAT, datefmt=DATE_FORMAT)
        self.converter = _utc_time

    @override
    def format(self, record: logging.LogRecord) -> str:
        """Format and redact ``record``; degrade gracefully on malformed calls.

        Args:
            record: The record being emitted.

        Returns:
            The redacted, formatted line(s).
        """
        try:
            record.getMessage()
        except _MALFORMED_CALL_ERRORS as exc:
            # Keep the template for diagnosis, but never the arguments.
            record.msg = (
                f"<unformattable log message: {type(exc).__name__}; template={record.msg!r}>"
            )
            record.args = None
        return redact(super().format(record))


class _RedactingStreamHandler(logging.StreamHandler[TextIO]):
    """Stream handler with redaction and argument-free error reporting.

    With no explicit stream it writes to the *current* ``sys.stderr`` on every
    emit, so it keeps working when stderr is replaced (e.g. by test capture).
    """

    def __init__(self, stream: TextIO | None = None) -> None:
        super().__init__(stream if stream is not None else sys.stderr)
        self._follow_stderr = stream is None
        self.setFormatter(RedactingFormatter())
        setattr(self, _HANDLER_MARKER, True)

    @override
    def emit(self, record: logging.LogRecord) -> None:
        if self._follow_stderr:
            self.stream = sys.stderr
        super().emit(record)

    @override
    def handleError(self, record: logging.LogRecord) -> None:
        # The stdlib default prints the raw message and arguments; never do that.
        exc = sys.exception()
        notice = (
            f"routesmart logging error: {type(exc).__name__} while emitting a record "
            f"from {record.name}:{record.lineno}\n"
        )
        with contextlib.suppress(OSError, ValueError):
            sys.stderr.write(notice)


def _install_handler(logger: logging.Logger, stream: TextIO | None) -> None:
    for existing in [h for h in logger.handlers if getattr(h, _HANDLER_MARKER, False)]:
        logger.removeHandler(existing)
        existing.close()
    logger.addHandler(_RedactingStreamHandler(stream))
    logger.propagate = False


def _resolve_level(level: int | str | None) -> int:
    raw = level if level is not None else os.getenv(LOG_LEVEL_ENV_VAR, "INFO")
    if isinstance(raw, int):
        return raw
    resolved = logging.getLevelNamesMapping().get(raw.strip().upper())
    if resolved is None:
        raise ValueError(f"unknown log level: {raw!r}")
    return resolved


def configure_logging(level: int | str | None = None, *, stream: TextIO | None = None) -> None:
    """Configure the ``routesmart`` logger hierarchy. Safe to call repeatedly.

    Repeated calls replace the previous RouteSmart handler instead of stacking
    duplicates. Records do not propagate to the root logger, and the root logger
    is never modified.

    Args:
        level: Level name or number. Defaults to ``$ROUTESMART_LOG_LEVEL``, else ``INFO``.
        stream: Output stream. Defaults to the current ``sys.stderr``.

    Raises:
        ValueError: If ``level`` is not a known logging level.
    """
    resolved = _resolve_level(level)
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    _install_handler(logger, stream)
    logger.setLevel(resolved)


def ensure_redacting_handler() -> None:
    """Install the redacting stderr handler on ``routesmart`` if none is present.

    Called when the ``routesmart`` package is imported and by ``get_logger()``.
    It is idempotent and never touches the root logger. Until
    ``configure_logging()`` sets a level, the effective level follows the root
    logger (WARNING by default).
    """
    root = logging.getLogger(ROOT_LOGGER_NAME)
    if not any(getattr(h, _HANDLER_MARKER, False) for h in root.handlers):
        _install_handler(root, None)


def get_logger(service: str) -> logging.Logger:
    """Return the logger for a RouteSmart service, e.g. ``get_logger("flight")``.

    Ensures the redacting handler is installed (see ``ensure_redacting_handler``).

    Args:
        service: Lower-case dotted service name, such as ``"flight"`` or ``"contracts.io"``.

    Returns:
        The ``routesmart.<service>`` logger.

    Raises:
        ValueError: If ``service`` is not a valid lower-case dotted name.
    """
    if not _SERVICE_NAME.fullmatch(service):
        raise ValueError(f"invalid service name: {service!r}")
    ensure_redacting_handler()
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{service}")
