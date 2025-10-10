from ..config.app_config import AppConfig as AppConfig
from ..schemas.response import (
    DataResponse as DataResponse,
    ErrorResponse as ErrorResponse,
)
from fastapi.responses import Response as Response
from typing import Any

class ResponseUtil:
    """
    响应工具类
    """
    @classmethod
    def success(
        cls,
        *,
        message: str = "操作成功",
        data: Any | None = None,
        name: str | None = None,
    ) -> Response:
        """
        成功响应方法
        :param message: 可选，成功响应结果中属性为 message 的值
        :param data: 可选，成功响应结果中属性为 data 的值
        :param name: 可选，成功响应结果中属性为 name 的值
        :return: 成功响应结果
        """
    @classmethod
    def failure(
        cls,
        *,
        message: str = "操作失败",
        code: int = 500,
        data: Any | None = None,
        name: str | None = None,
    ) -> Response:
        """
        失败响应方法
        :param message: 可选，失败响应结果中属性为 message 的值
        :param code: 可选，失败响应结果中属性为 code 的值
        :param data: 可选，失败响应结果中属性为 data 的值
        :param name: 可选，失败响应结果中属性为 name 的值
        :return: 失败响应结果
        """
    @classmethod
    def error(
        cls,
        *,
        error: Any | None,
        message: str = "服务器异常",
        code: int = 500,
        name: str | None = None,
    ) -> Response:
        """
        错误响应方法
        :param message: 可选，错误响应结果中属性为 message 的值
        :param code: 可选，错误响应结果中属性为 code 的值
        :param error: 可选，错误响应结果中属性为 data 的值
        :param name: 可选，错误响应结果中属性为 name 的值
        :return: 错误响应结果
        """
