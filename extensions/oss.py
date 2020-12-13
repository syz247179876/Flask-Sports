# -*- coding: utf-8 -*-
# @Time  : 2020/12/13 下午6:02
# @Author : 司云中
# @File : oss.py
# @Software: Pycharm

import oss2

class OSS(object):
    """操作OSS对象存储,上传文件"""

    def __init__(self, app=None, config=None):
        self.config = config

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the app with ALiYun-OSS service"""
        self.app = app

        # 从配置中导入
        self.set_auth()
        self.set_bucket()
        self.set_base_url()

        oss = {
            'auth': self.auth,
            'bucket': self.bucket,
            'base_url': self.base_url
        }
        setattr(app, 'OSS', oss)

    def set_auth(self):
        """设置认证信息"""
        access_key_id = self.app.config.get('ACCESS_KEY_ID')
        access_key_secret = self.app.config.get('ACCESS_KEY_SECRET')
        self.auth = oss2.Auth(access_key_id, access_key_secret)

    def set_bucket(self):
        """设置oss图床"""

        oss_bucket_name = self.app.config.get('OSS_BUCKET_NAME')
        endpoint = self.app.config.get('OSS_ENDPOINT')
        self.bucket = oss2.Bucket(self.auth, endpoint, oss_bucket_name)

    def set_base_url(self):
        """
        获取返回的基本路由,用于提供用户访问数据地址
        或者是存数数据库的字段值
        """
        self.base_url = self.app.config.get('OSS_BASE_URL')


oss = OSS()