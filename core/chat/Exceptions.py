"""
Custom exceptions for chat engine
"""


class ServerSideError(Exception):
    """
    服务器端错误异常类
    用于处理LLM提供商或网络错误等服务器端问题
    """
    
    def __init__(self, message: str, server_response: str = None):
        """
        初始化服务器端错误
        
        Args:
            message: 错误描述信息
            server_response: 服务端返回的原始内容（如果有）
        """
        super().__init__(message)
        self.server_response = server_response
        self.message = message
    
    def __str__(self):
        if self.server_response:
            return f"{self.message}\n服务端返回内容: {self.server_response}"
        return self.message
    
    def __repr__(self):
        return f"ServerSideError(message='{self.message}', server_response='{self.server_response}')"