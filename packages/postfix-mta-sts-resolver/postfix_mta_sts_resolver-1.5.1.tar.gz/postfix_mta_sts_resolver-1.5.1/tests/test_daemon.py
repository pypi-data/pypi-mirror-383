import sys
import asyncio
import argparse

import pytest

import postfix_mta_sts_resolver.daemon as daemon
import postfix_mta_sts_resolver.utils as utils

class MockCmdline:
    def __init__(self, *args):
        self._cmdline = args

    def __enter__(self):
        self._old_cmdline = sys.argv
        sys.argv = list(self._cmdline)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.argv = self._old_cmdline

@pytest.mark.asyncio
async def test_heartbeat():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(daemon.heartbeat(), 1.5)

def test_parse_args():
    with MockCmdline("mta-sts-daemon", "-c", "/dev/null", "-v", "info"):
        args = daemon.parse_args()
    assert args.config == '/dev/null'
    assert not args.disable_uvloop
    assert args.verbosity == utils.LogLevel.info
    assert args.logfile is None

def test_bad_args():
    with MockCmdline("mta-sts-daemon", "-c", "/dev/null", "-v", "xxx"):
        with pytest.raises(SystemExit):
            args = daemon.parse_args()
