class IPAlreadyOnlineError(BaseException):
    pass


class IPNotOnlineError(BaseException):
    pass


class OtherException(BaseException):
    def __init__(self, err_response):
        self.err_response = err_response
        pass
