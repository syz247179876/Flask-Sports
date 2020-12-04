# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 上午2:07
# @Author : 司云中
# @File : signal.py
# @Software: Pycharm

from blinker import Namespace

user_signals = Namespace()

send_code_signal = user_signals.signal('send-code')


