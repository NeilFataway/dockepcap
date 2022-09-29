# coding=utf-8
from flask import current_app
from flask import jsonify
import traceback
import StringIO


class DPcapException(Exception):
    """
    Base Exception for all docker pcap exception
    """
    code = None

    def __init__(self, message=None, code=None):
        if message:
            Exception.__init__(self, message)
        else:
            Exception.__init__(self)
        if code is not None:
            self.code = code
        elif not self.code:
            self.code = 500
        self.trace_back = ""

    @property
    def to_dict(self):
        if self.code >= 500:
            s_traceback = StringIO.StringIO()
            traceback.print_exc(file=s_traceback)
            self.trace_back = s_traceback.getvalue()
        return {
            "errmsg": self.message,
            "traceback": self.trace_back
        }

    @property
    def to_json(self):
        return jsonify(self.to_dict)

    @staticmethod
    def error_handler(err):
        current_app.logger.error(err.message)
        return err.to_json, err.code, {"Content-Type": "application/json"}


class ContainerNotFoundError(DPcapException):
    """Container Not Found"""
    code = 404
    message = "container not found"


class DumpNotFoundError(DPcapException):
    """Dump Not Found"""
    code = 404
    message = "dump not found"


class InvalidUsage(DPcapException):
    """前端传入参数异常"""
    code = 400
    message = "invalid usage"


class ResourceLocked(DPcapException):
    """resource locked"""
    code = 423
    message = "resource locked"


def unknownhandler(err):
    """handle the exception which is not defined by our code yet throw out."""
    s_traceback = StringIO.StringIO()
    traceback.print_exc(file=s_traceback)

    current_app.logger.error("Internal error occurred - {}: {}:\n{}".format(type(err).__name__, str(err),
                                                                            s_traceback.getvalue()))

    response = jsonify({
        "errmsg": "Internal error occurred - {}: {}".format(type(err).__name__, str(err)),
        "traceback": s_traceback.getvalue()
    })
    response.status_code = 500
    return response


def setup_exception(app):
    app.register_error_handler(DPcapException, DPcapException.error_handler)
    app.register_error_handler(500, unknownhandler)
