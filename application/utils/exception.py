# -*- coding: utf-8 -*-
# @Time  : 2020/12/1 下午11:48
# @Author : 司云中
# @File : exception.py
# @Software: Pycharm

import json

import werkzeug as werkzeug

HTTP_100_CONTINUE = 100
HTTP_101_SWITCHING_PROTOCOLS = 101
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
HTTP_204_NO_CONTENT = 204
HTTP_205_RESET_CONTENT = 205
HTTP_206_PARTIAL_CONTENT = 206
HTTP_207_MULTI_STATUS = 207
HTTP_208_ALREADY_REPORTED = 208
HTTP_226_IM_USED = 226
HTTP_300_MULTIPLE_CHOICES = 300
HTTP_301_MOVED_PERMANENTLY = 301
HTTP_302_FOUND = 302
HTTP_303_SEE_OTHER = 303
HTTP_304_NOT_MODIFIED = 304
HTTP_305_USE_PROXY = 305
HTTP_306_RESERVED = 306
HTTP_307_TEMPORARY_REDIRECT = 307
HTTP_308_PERMANENT_REDIRECT = 308
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_402_PAYMENT_REQUIRED = 402
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
HTTP_408_REQUEST_TIMEOUT = 408
HTTP_409_CONFLICT = 409
HTTP_410_GONE = 410
HTTP_411_LENGTH_REQUIRED = 411
HTTP_412_PRECONDITION_FAILED = 412
HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_414_REQUEST_URI_TOO_LONG = 414
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
HTTP_417_EXPECTATION_FAILED = 417
HTTP_418_IM_A_TEAPOT = 418
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_423_LOCKED = 423
HTTP_424_FAILED_DEPENDENCY = 424
HTTP_426_UPGRADE_REQUIRED = 426
HTTP_428_PRECONDITION_REQUIRED = 428
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_504_GATEWAY_TIMEOUT = 504
HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
HTTP_506_VARIANT_ALSO_NEGOTIATES = 506
HTTP_507_INSUFFICIENT_STORAGE = 507
HTTP_508_LOOP_DETECTED = 508
HTTP_509_BANDWIDTH_LIMIT_EXCEEDED = 509
HTTP_510_NOT_EXTENDED = 510
HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511
# 通用自定义异常码
UNIVERSAL_ERROR = 9999
# QQ认证异常码
QQ_AUTHENTICATION_ERROR = 1001
# 微博认证异常码
WeiBo_AUTHENTICATION_ERROR = 1002
# 手机注册异常
PHONE_REGISTER_ERROR = 1003
# 手机号不存在
PHONE_NOT_EXIST = 1004
# 手机号存在
PHONE_HAS_EXISTED = 1005
# 验证码错误
CODE_VALIDATE_FAIL = 1006


class ApiException(werkzeug.exceptions.HTTPException):
    """
    1.重写__init__()方法,设定传入值
      code: HTTP常规状态码
      error_code:自定义错误异常码,范围1000-9999
      msg:提示消息,没有则为''
      data:响应数据,没有则为''
    2.重写get_body()方法,重设响应体
    3.重写get_headers()方法,重设响应头部
    """

    def __init__(self, code=None, error_code=None, msg=None, data=None):
        self.code = code or HTTP_500_INTERNAL_SERVER_ERROR
        self.error_code = error_code or UNIVERSAL_ERROR
        self.msg = msg or self.description
        self.data = data
        super().__init__(self.msg, None)  # response is None

    def get_body(self, environ=None):
        """生成body"""
        body = dict(
            code=self.code,
            error_code=self.error_code,
            msg=self.msg,
            data=self.data
        )
        return json.dumps(body, sort_keys=False, ensure_ascii=False)  # json格式化,以中文显示

    def get_headers(self, environ=None):
        """返回application/json的响应格式"""
        return [("Content-Type", "application/json")]


class ServerError(ApiException):
    """通用服务错误"""
    code = HTTP_500_INTERNAL_SERVER_ERROR
    error_code = UNIVERSAL_ERROR
    description = 'Server Error'

    def __init__(self):
        super().__init__(self.code, self.error_code, self.description)


class QQServiceUnavailable(ApiException):
    """QQ认证异常"""
    code = HTTP_400_BAD_REQUEST
    error_code = QQ_AUTHENTICATION_ERROR
    description = 'QQ Authentication error'

    def __init__(self):
        super().__init__(self.code, self.error_code, self.description)


class WbServiceUnavailable(ApiException):
    """微博认证异常"""
    code = HTTP_400_BAD_REQUEST
    error_code = WeiBo_AUTHENTICATION_ERROR
    description = 'WeiBo Authentication error'

    def __init__(self):
        super().__init__(self.code, self.error_code, self.description)


class RegisterExistedException(ApiException):
    """手机注册已存在"""
    code = HTTP_400_BAD_REQUEST
    error_code = PHONE_HAS_EXISTED
    description = 'Mobile phone number exist'

    def __init__(self):
        super().__init__(self.code, self.error_code, self.description)


class LoginNotExistException(ApiException):
    """手机号登录不存在"""
    code = HTTP_400_BAD_REQUEST
    error_code = PHONE_NOT_EXIST
    description = 'Mobile phone number does not exist'

    def __init__(self):
        super().__init__(self.code, self.error_code, self.description)


class VerificationCodeException(ApiException):
    """验证码错误"""

    code = HTTP_400_BAD_REQUEST
    error_code = CODE_VALIDATE_FAIL
    description = 'Verification code is validated error'

    def __init__(self):
        super().__init__(self.code, self.error_code, self.description)
