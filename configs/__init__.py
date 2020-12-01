# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:24
# @Author : 司云中
# @File : __init__.py.py
# @Software: Pycharm

import os

def load_config(mode=os.environ.get('MODE')):
    """
    load config which would be required in
    different environment decided by param 'mode'
    """
    try:
        if mode == 'TESTING':
            from .testing import TestingConfig
            return TestingConfig
        elif mode == 'PRODUCTION':
            from .production import ProductionConfig
            return ProductionConfig
        elif mode == 'DEVELOPMENT':
            from .development import DevelopmentConfig
            return DevelopmentConfig
    except ImportError:
        from .default import Default
        return Default

__all__ = ['load_config']