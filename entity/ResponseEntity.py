from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ResponseEntity:
    """
    统一的前后端数据传输格式

    用于封装API响应，包含状态码、消息和具体数据
    """
    code: int
    message: str
    data: Optional[Any] = None

    def __post_init__(self):
        # 验证状态码格式
        if not isinstance(self.code, int):
            raise TypeError("状态码必须是整数")

    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> 'ResponseEntity':
        """
        创建成功响应

        Args:
            data: 返回的数据
            message: 响应消息，默认"操作成功"

        Returns:
            ResponseEntity: 成功响应的ResponseEntity实例
        """
        return ResponseEntity(code=200, message=message, data=data)

    @staticmethod
    def error(code: int = 500, message: str = "操作失败") -> 'ResponseEntity':
        """
        创建错误响应

        Args:
            code: 错误状态码，默认500
            message: 错误消息，默认"操作失败"

        Returns:
            ResponseEntity: 错误响应的ResponseEntity实例
        """
        return ResponseEntity(code=code, message=message, data=None)

    @staticmethod
    def unauthorized(message: str = "未授权访问") -> 'ResponseEntity':
        """
        创建未授权响应

        Args:
            message: 错误消息，默认"未授权访问"

        Returns:
            ResponseEntity: 未授权响应的ResponseEntity实例
        """
        return ResponseEntity(code=401, message=message, data=None)

    @staticmethod
    def forbidden(message: str = "禁止访问") -> 'ResponseEntity':
        """
        创建禁止访问响应

        Args:
            message: 错误消息，默认"禁止访问"

        Returns:
            ResponseEntity: 禁止访问响应的ResponseEntity实例
        """
        return ResponseEntity(code=403, message=message, data=None)

    @staticmethod
    def not_found(message: str = "资源未找到") -> 'ResponseEntity':
        """
        创建资源未找到响应

        Args:
            message: 错误消息，默认"资源未找到"

        Returns:
            ResponseEntity: 资源未找到响应的ResponseEntity实例
        """
        return ResponseEntity(code=404, message=message, data=None)

    def is_success(self) -> bool:
        """
        判断响应是否成功

        Returns:
            bool: 如果状态码为200则返回True，否则返回False
        """
        return self.code == 200

    def __repr__(self) -> str:
        return f"ResponseEntity(code={self.code}, message='{self.message}', data={self.data})"