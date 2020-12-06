# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:27
# @Author : 司云中
# @File : __init__.py.py
# @Software: Pycharm

from flask import current_app
from werkzeug.utils import import_string

from application.utils.exception import ImproperlyConfigured

def get_model(import_name):
    """获取具体app_label下的model_name"""
    model_name = import_string(import_name)
    return model_name

def get_user_model():
    """
    Return the User model that is active in this project.
    """
    try:
        return get_model(current_app.config.get('AUTH_USER_MODEL'))
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL refers to model '%s' that has not been installed" % current_app.config.get('AUTH_USER_MODEL')
        )