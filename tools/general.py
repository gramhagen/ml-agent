# -*- coding: utf-8 -*-
# pylint: disable=no-name-in-module

"""
Capture miscellaneous utilities
"""

from subprocess import Popen, PIPE
import inspect
from numpy import isclose


def run_process(command, logger=None):
    """
    run_process executes a shell command and returns any output

    WARNING:
        there is no protection against executing malicious code here so be careful

    Args:
        command (str or arraylike(str)): shell command to execute
        logger (object): logger object

    Returns:
        (object): stdout from shell command is returned
    """

    caller = inspect.stack()[1][3]
    if logger is not None:
        logger.debug("(%s) command: %s", caller, command)
    p = Popen(args=command, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if logger is not None:
        if err:
            logger.debug("(%s) stderr: %s", caller, err)
        if out:
            logger.debug("(%s) stdout: %s", caller, out)

    returncode = p.returncode
    if returncode != 0:
        msg = "encountered error (return code {returncode} while running command {command}\n {err}"
        raise Exception(msg.format(returncode=returncode, command=command, err=err))

    return out


def precision_compare(x, y):
    """
    compare two values, but limit precision based on the first input

    Args:
        x (float): value used to determine precision for comparison
        y (float): value which will be limited to x's precision

    Returns:
        bool: True if x and y match to precision of x
    """

    digits = str(x).split('.')
    tol = 10 ** -len(digits[1]) if len(digits) > 1 else 1
    return isclose(x, y, atol=tol)
