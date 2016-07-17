# -*- coding: utf-8 -*-
"""
Container for all enumerated types
"""


class BaseEnum(object):
    """ base enum class """

    @classmethod
    def values(cls):
        """
        get all allowable values

        Returns:
            list: all member values
        """

        return [x for x in dir(cls) if not x.startswith('__') and not x == 'values']


class ModelType(BaseEnum):
    """ all supported model types """

    vw = 'vw'
    sklearn = 'sklearn'


class ModelStatus(BaseEnum):
    """ all supported model statuses """

    active = 'active'
    paused = 'paused'
