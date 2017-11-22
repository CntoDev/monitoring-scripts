"""This file contains all the common functions, variables, etc. used by the test files"""

import pytest


def run_and_assert(unit_invocation, expected_code, capfd, expected_message=None,
                   **execution_args):
    """Ensure a function follows Nagios standards

    This calls the function passed as `unit_invocation` providing as arguments
    `**execution_args`.
    It then captures its return status and checks if its return code matches
    with the provided `expected_code` (which must be an instance of
    `monitoring_scripts.nagios_common.Codes`).
    After that it checks the function prints a correct output and if `expected_message` is
    provided, it also checks that such string is contained in the function's output.

    `capfd` is used to retrieve the function under test's output and it's a fixture provided by
    pytest.
    """

    with pytest.raises(SystemExit) as execution_result:
        unit_invocation(**execution_args)

    assert execution_result.value.code == expected_code.value

    out = capfd.readouterr()[0]
    if out:
        assert out.startswith(expected_code.name + ':')
        if expected_message:
            assert expected_message in out
