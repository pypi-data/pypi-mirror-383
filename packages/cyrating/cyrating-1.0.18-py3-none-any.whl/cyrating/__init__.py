# -*- coding: utf-8 -*-

from cyrating.api import Cyrating

__all__ = ["api"]


def init(**kwargs):
    return Cyrating(**kwargs)
