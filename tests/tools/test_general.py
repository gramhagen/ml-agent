# -*- coding: utf-8 -*-

"""
Test general utils
"""

from tools.general import precision_compare


def test_precision_compare():
    """
    test comparing floats to desired precision works
    """

    assert precision_compare(12, 12.9)

    assert precision_compare(1.123, 1.12345)

    assert not precision_compare(1.12345, 1.123)

    assert not precision_compare(1.123, 2.123)
