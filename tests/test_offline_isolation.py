"""Assertions that only apply when the suite runs under scripts/test-offline.sh.

The script's probe verifies the namespace, exports its id in
``ROUTESMART_OFFLINE_NETNS`` and then ``exec``s pytest in the same process. This
test checks, from inside pytest, that it is still in that namespace, with no
network interfaces besides ``lo``, and not running as root. Under plain pytest it
is skipped.
"""

from __future__ import annotations

import os
import socket

import pytest

OFFLINE_NETNS = os.environ.get("ROUTESMART_OFFLINE_NETNS")


@pytest.mark.skipif(OFFLINE_NETNS is None, reason="only under scripts/test-offline.sh")
def test_suite_runs_in_the_verified_namespace_as_non_root() -> None:
    assert os.readlink("/proc/self/ns/net") == OFFLINE_NETNS
    assert {name for _, name in socket.if_nameindex()} == {"lo"}
    assert os.geteuid() != 0
    assert os.getuid() != 0
