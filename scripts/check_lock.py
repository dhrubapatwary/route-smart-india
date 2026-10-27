"""Check that requirements/dev.lock.txt is exactly what requirements/dev.txt needs.

It resolves ``requirements/dev.txt`` with pip, constrained to the locked
versions, and compares the resolved set with the lock:

* **missing:** needed by ``dev.txt`` but not pinned in the lock;
* **obsolete:** pinned in the lock but no longer needed by ``dev.txt``;
* **mismatched:** resolved to a different version than locked. This should be
  impossible under the constraints, but is reported if it happens.

Resolution reads package metadata from the index, so it needs network access.
It installs nothing (``--dry-run``) and writes only to a temporary directory.

Usage: ``python scripts/check_lock.py`` (exit 0 = consistent, 1 = drift, 2 = error).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "requirements" / "dev.lock.txt"
INPUT = ROOT / "requirements" / "dev.txt"
_PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s\\;]+)", re.MULTILINE)


def normalize(name: str) -> str:
    """Return the PEP 503 normalised form of a distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_lock(text: str) -> dict[str, str]:
    """Return ``{normalised name: version}`` for every ``name==version`` pin in ``text``."""
    return {normalize(name): version for name, version in _PIN.findall(text)}


@dataclass(frozen=True)
class Drift:
    """Differences between the lock and the resolved requirement set."""

    missing: dict[str, str] = field(default_factory=dict)
    obsolete: dict[str, str] = field(default_factory=dict)
    mismatched: dict[str, tuple[str, str]] = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        """Whether the lock and the resolved set agree exactly."""
        return not (self.missing or self.obsolete or self.mismatched)


def compare(locked: dict[str, str], resolved: dict[str, str]) -> Drift:
    """Compare locked pins with the resolved set (both keyed by normalised name)."""
    return Drift(
        missing={n: v for n, v in resolved.items() if n not in locked},
        obsolete={n: v for n, v in locked.items() if n not in resolved},
        mismatched={
            n: (locked[n], v) for n, v in resolved.items() if n in locked and locked[n] != v
        },
    )


def resolve(constraints: dict[str, str]) -> dict[str, str]:
    """Resolve ``dev.txt`` with pip under exact-version constraints; install nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        constraints_file = Path(tmp) / "constraints.txt"
        constraints_file.write_text(
            "".join(f"{n}=={v}\n" for n, v in sorted(constraints.items())), encoding="utf-8"
        )
        report_file = Path(tmp) / "report.json"
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--dry-run",
            "--ignore-installed",
            "--quiet",
            "--report",
            str(report_file),
            "-r",
            str(INPUT),
            "-c",
            str(constraints_file),
        ]
        subprocess.run(command, check=True, cwd=ROOT)  # noqa: S603 (fixed argv, no shell)
        report = json.loads(report_file.read_text(encoding="utf-8"))
    return {
        normalize(item["metadata"]["name"]): item["metadata"]["version"]
        for item in report["install"]
    }


def main() -> int:
    """Run the check and print a human-readable result."""
    locked = parse_lock(LOCK.read_text(encoding="utf-8"))
    if not locked:
        print(f"check-lock: no pins found in {LOCK}", file=sys.stderr)
        return 2
    try:
        resolved = resolve(locked)
    except (subprocess.CalledProcessError, OSError, KeyError, ValueError) as exc:
        print(f"check-lock: resolution failed: {exc!r}", file=sys.stderr)
        return 2
    drift = compare(locked, resolved)
    if drift.clean:
        print(f"check-lock: ok ({len(locked)} pins; lock matches dev.txt exactly)")
        return 0
    for label, items in (("missing", drift.missing), ("obsolete", drift.obsolete)):
        for name, version in sorted(items.items()):
            print(f"check-lock: {label}: {name}=={version}", file=sys.stderr)
    for name, (locked_version, resolved_version) in sorted(drift.mismatched.items()):
        print(
            f"check-lock: mismatched: {name} locked {locked_version}, resolved {resolved_version}",
            file=sys.stderr,
        )
    print("check-lock: regenerate the lock (see requirements/README.md)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
