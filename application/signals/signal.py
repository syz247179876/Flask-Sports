# -*- coding: utf-8 -*-
# @Time  : 2020/12/4 上午2:07
# @Author : 司云中
# @File : signal.py
# @Software: Pycharm

from blinker import Namespace

user_signals = Namespace()  # 声明信号映射

send_code_signal = user_signals.signal('send-code') # 创建信号对象


