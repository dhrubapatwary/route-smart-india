# Logging and Confidentiality

- **Code:** `src/routesmart/log.py`
- **Tests:** `tests/test_log.py`
- **Decision:** D-IMPL-04, **approved with limitations** (owner, 2026-10-27). Redaction is best-effort, not a guarantee; sensitive values must not be logged. Importing `routesmart` configures the `routesmart` logger, and a test covers this.

## Usage

```python
from routesmart.log import configure_logging, get_logger, sanitize_url

configure_logging()                 # once, at the entry point; level from ROUTESMART_LOG_LEVEL
log = get_logger("flight")          # logger "routesmart.flight"
log.info("fetched %d options from %s", count, sanitize_url(url))
```

The output format is `2026-10-27T11:40:00.123Z INFO routesmart.flight: …`. Timestamps are UTC.

## Rules for callers (primary control)

1. Never log credentials, tokens, request or response headers, request bodies, or personal travel data such as names, PNRs and phone numbers.
2. Log URLs only through `sanitize_url()`. It **reduces** risk but does not make an arbitrary URL safe. Its exact contract:
   - It drops userinfo and the fragment.
   - It masks every query value, keeping the parameter names.
   - It masks token-like path segments: 20 or more characters from `[A-Za-z0-9._~:+=-]` that contain both a letter and a digit, such as bot/API tokens, UUIDs and signed IDs.
   - It applies `redact()` to the other path segments, which catches JWTs and `;token=…`.
   - It does **not** detect short or letters-only secrets in the path, secrets in the host name, or percent-encoded secrets. Don't log such URLs at all.
3. For provider errors, log the exception type, status code and a sanitised URL. Do not log raw provider responses.

## Defence in depth (what the helper guarantees)

- **Whole-output redaction.** Every RouteSmart handler redacts its *fully formatted* output, which includes the message, the exception traceback and the stack info. The tests check the formatted output, not an intermediate message.
- **Patterns covered:**
  - values of secret-like keys in `key=value`, `key: value`, `"key": "value"` and `key='value'` forms. Key names include `password`, `secret`, `token`, `api_key`, `access_token`, `client_secret`, `authorization`, `cookie`, `signature` and `key`, among others;
  - `Bearer`/`Basic` credentials;
  - URL userinfo (`scheme://user:pass@host`);
  - JWT-shaped tokens.
- **Malformed calls never raise.** A bad `%` format, such as a wrong type, a missing argument or a missing mapping key, produces `<unformattable log message: …; template=…>`. The arguments are dropped. Any other emit error prints a one-line notice with the exception type and the logger/line, never the message or arguments. This replaces the stdlib default, which echoes both.
- **Early records and direct loggers.** Importing the `routesmart` package (which any `routesmart.*` module import does first) installs the redacting stderr handler on the `routesmart` logger via `ensure_redacting_handler()`.
  - **Effect:** every record in the `routesmart.*` hierarchy is redacted, including records from plain `logging.getLogger(__name__)` inside the package and records emitted before `configure_logging()`.
  - **Level:** WARNING and above by default, until `configure_logging()` sets a level.
  - **Never unredacted:** such records never reach Python's unredacted last-resort handler.
  - **Root logger:** it is never modified, and RouteSmart records do not propagate to it.
  - **Side effect:** importing the package configures the `routesmart` logger.
- **Performance.** All patterns are written so that nothing backtracks:
  - A match may start only at the beginning of a token run (negative lookbehind).
  - Runs are consumed with possessive quantifiers.
  - Key suffixes are checked with fixed-width lookbehinds.
  - Key names are at most 64 characters.

  **Evidence** (local, 2026-10-27; see TEST_RESULTS.md, Round 3):
  - 4× more input took ≈ 4× the time for every adversarial input tried.
  - The Round 2 reviewer's input `"eyJ-" * 80_000` dropped from 1.38 s to 0.06 s.

  `tests/test_log.py` runs ten ~400 KB adversarial payloads with a generous 5 s budget each. The old quadratic JWT pattern was confirmed to exceed 20 s on one of them, so a regression fails the test. The budget is not a precise timing claim.
- **Idempotent setup.** Calling `get_logger` or `configure_logging` repeatedly keeps exactly one RouteSmart handler.

## Known limitations

- Pattern-based redaction **cannot detect arbitrary secrets**. A bare value with no recognisable key, scheme or shape (for example `"failed for hunter2"`) is logged as-is. Rule 1 above is the real control.
- Over-redaction is accepted. Any value after a key *ending* in a sensitive suffix, such as `cache_key=…` or `primary_key=…`, is masked. Keys that merely *contain* a suffix, such as `keyboard=` or `tokens=`, are not.
- Key names longer than 64 characters are not recognised as keys.
- The JWT rule matches only a JWT that starts a token run. A JWT glued to a preceding base64url character, as in `x-eyJ…`, is not matched by that rule. This is what keeps the scan linear. A key or `Bearer` before it is still caught.
- Records sent to *other* handlers that someone attaches to RouteSmart loggers, or records from third-party libraries' own loggers, are not covered.
- **pytest:** pytest's log capture attaches its own (unredacted) handler to non-propagating loggers such as `routesmart`. The suite therefore runs with `-p no:logging` (pyproject `addopts`). Re-enabling pytest's logging plugin would print RouteSmart records unredacted in failure reports.
- A quoted value is masked only up to its closing quote. An unquoted value is masked up to the next whitespace or `,;&}]`.
