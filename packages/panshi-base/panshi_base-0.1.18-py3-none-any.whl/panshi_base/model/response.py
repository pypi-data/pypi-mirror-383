from typing import Optional, Any

from pydantic import BaseModel


class CommonResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Any]

    @staticmethod
    def success(data: Any) -> 'CommonResponse':
        return CommonResponse(code=200, msg="成功", data=data)

    @staticmethod
    def fail(msg: str, code: int = 500) -> 'CommonResponse':
        return CommonResponse(code=code, msg=msg, data=None)
