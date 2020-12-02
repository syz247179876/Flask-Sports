# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:28
# @Author : 司云中
# @File : manage.py.py
# @Software: Pycharm

from application import create_app
from flask_script import Manager, Server

app = create_app()
manager = Manager(app)
# 使用python manage.py runserver启动服务器
manager.add_command('runserver', Server)

# @manager.shell
# def make_shell_context():
#     return dict(app=app, db=db, User=User)

if __name__ == '__main__':
    # 启动flask服务
    manager.run()
    # app.run(host='192.168.1.102', port=5000)