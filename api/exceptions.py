# coding=utf-8
from __future__ import unicode_literals
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler as rest_exception_handler


class ProjectBaseException(Exception):
    code = {"code": "undefined", "en": "undefined exception code"}

    def __init__(self, *args, **kwargs):
        if not isinstance(self.code, dict):
            raise Exception('parameter type must be a dict')
        code = self.code.get('code', 'undefined')
        self.message = self.code.get('message', 'undefined')
        self.obj = kwargs.get('obj', None)
        self.target = kwargs.get('target', None)
        self.params = kwargs.get('params')
        if self.params and isinstance(self.params, dict):
            self.message = self.message.format(**self.params)
        elif self.params and isinstance(self.params, (list, set, tuple)):
            self.message = self.message.format(*self.params)

        Exception.__init__(self, "{0}:{1}".format(code, self.message))

    def __new__(cls, *args, **kwargs):
        obj = super(ProjectBaseException, cls).__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj


def _custom_exception_handler(exc, context):
    # logger.exception(exc)
    if isinstance(exc, ProjectBaseException):
        msg = exc.message
        data = {"non_field_errors": [msg],
                "error_code": exc.code["code"]}
        return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)


def exception_handler(exc, context):
    response = rest_exception_handler(exc, context)

    if response is None:
        response = _custom_exception_handler(exc=exc, context=context)

    return response
