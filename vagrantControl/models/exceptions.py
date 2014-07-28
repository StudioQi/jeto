# -=- encoding: utf-8 -=-
class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvalidPath(BaseException):
    pass


class InstanceNotFound(BaseException):
    pass
