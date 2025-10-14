class PanshiError(Exception):
    """Base exception class for the panshi api."""

    pass


class NotImplmentError(PanshiError):
    """Exception that's raised when code not implemented."""

    pass


class APIError(PanshiError):
    """Base exception clas for the panshi api error"""

    def __init__(self, error_code: int, error_msg: str) -> None:
        """
        init with error code and error message from api response
        """
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(
            f"api return error, code: {self.error_code}, msg: {self.error_msg}"
        )

if __name__ == '__main__':
    e = APIError("111","奥术大师大多")
    print(str(e))

class RequestError(PanshiError):
    """Exception when api request is failed"""


class InvalidArgumentError(PanshiError):
    """Exception when the argument is invalid"""

    pass


class ArgumentNotFoundError(PanshiError):
    """Exception when the argument is not found"""


class RequestTimeoutError(PanshiError):
    """Exception when api request is timeout"""

    pass


class AccessTokenExpiredError(PanshiError):
    """Exception when access token is expired"""

    pass


class InternalError(PanshiError):
    """Exception when internal error occurs"""

    pass


class ValidationError(Exception):
    """Exception when validating failed"""

    ...


class FileSizeOverflow(Exception):
    """Exception when zip file is too big"""

    ...
