from typing import ClassVar, Any


def get_exception_str(e: Exception):
    if len(str(e)) == 0:
        error_msg = type(e).__name__
        return error_msg
    else:
        return str(e)


class Singleton(type):
    """
    Singleton metaclass
    """

    _instances: ClassVar[dict] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        change operator () to return the only instance
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
