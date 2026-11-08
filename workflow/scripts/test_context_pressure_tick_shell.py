"""
Runs test_context_pressure_tick.sh under pytest so a red shell case turns the suite red.

The shell test never DMs or notifies anyone: it sets CONTEXT_TICK_DELIVER=0, a throwaway state
file and a dead API base itself (see its ISOLATION block). Takes ~20s because one case asserts
the sensor retry really runs.
"""
import os
import subprocess

HERE  = os.path.dirname( os.path.abspath( __file__ ) )
SHELL = os.path.join( HERE, "test_context_pressure_tick.sh" )


def test_context_pressure_tick_shell_cases_all_pass():
    """
    Requires:
        - bash and python3 on PATH
    Ensures:
        - fails, with the shell test's own output attached, if any shell case fails
    """
    result = subprocess.run( [ "bash", SHELL ], capture_output=True, text=True, timeout=300 )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 failed" in result.stdout, result.stdout
