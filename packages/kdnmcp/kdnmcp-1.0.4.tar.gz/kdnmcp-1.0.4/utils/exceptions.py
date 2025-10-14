"""异常处理模块"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """错误代码枚举"""
    # 配置错误
    CONFIG_MISSING = "CONFIG_MISSING"
    CONFIG_INVALID = "CONFIG_INVALID"
    
    # API错误
    API_REQUEST_FAILED = "API_REQUEST_FAILED"
    API_RESPONSE_INVALID = "API_RESPONSE_INVALID"
    API_AUTHENTICATION_FAILED = "API_AUTHENTICATION_FAILED"
    API_RATE_LIMIT_EXCEEDED = "API_RATE_LIMIT_EXCEEDED"
    API_SERVICE_UNAVAILABLE = "API_SERVICE_UNAVAILABLE"
    
    # 参数错误
    PARAMETER_MISSING = "PARAMETER_MISSING"
    PARAMETER_INVALID = "PARAMETER_INVALID"
    PARAMETER_FORMAT_ERROR = "PARAMETER_FORMAT_ERROR"
    
    # 业务逻辑错误
    SHIPPER_NOT_SUPPORTED = "SHIPPER_NOT_SUPPORTED"
    LOGISTICS_CODE_INVALID = "LOGISTICS_CODE_INVALID"
    TRACKING_NOT_FOUND = "TRACKING_NOT_FOUND"
    RECOGNITION_FAILED = "RECOGNITION_FAILED"
    TIME_ESTIMATION_FAILED = "TIME_ESTIMATION_FAILED"
    
    # 系统错误
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"


class MCPError(Exception):
    """MCP服务基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "error": True,
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }
        
        if self.cause:
            result["cause"] = str(self.cause)
        
        return result
    
    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"


class ConfigurationError(MCPError):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, cause: Optional[Exception] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFIG_INVALID,
            details=details,
            cause=cause
        )


class APIError(MCPError):
    """API请求错误"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.API_REQUEST_FAILED,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_data:
            details["response_data"] = response_data
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            cause=cause
        )


class ValidationError(MCPError):
    """参数验证错误"""
    
    def __init__(
        self,
        message: str,
        parameter_name: Optional[str] = None,
        parameter_value: Optional[Any] = None,
        expected_format: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if parameter_name:
            details["parameter_name"] = parameter_name
        if parameter_value is not None:
            details["parameter_value"] = str(parameter_value)
        if expected_format:
            details["expected_format"] = expected_format
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PARAMETER_INVALID,
            details=details,
            cause=cause
        )


class BusinessLogicError(MCPError):
    """业务逻辑错误"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        business_context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=business_context or {},
            cause=cause
        )


class NetworkError(MCPError):
    """网络错误"""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        timeout: Optional[float] = None,
        cause: Optional[Exception] = None
    ):
        details = {}
        if url:
            details["url"] = url
        if timeout:
            details["timeout"] = timeout
        
        super().__init__(
            message=message,
            error_code=ErrorCode.NETWORK_ERROR,
            details=details,
            cause=cause
        )


def handle_exception(func):
    """异常处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MCPError:
            # 重新抛出MCP异常
            raise
        except Exception as e:
            # 将其他异常包装为内部错误
            raise MCPError(
                message=f"Internal error in {func.__name__}: {str(e)}",
                error_code=ErrorCode.INTERNAL_ERROR,
                cause=e
            )
    return wrapper


def handle_async_exception(func):
    """异步异常处理装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except MCPError:
            # 重新抛出MCP异常
            raise
        except Exception as e:
            # 将其他异常包装为内部错误
            raise MCPError(
                message=f"Internal error in {func.__name__}: {str(e)}",
                error_code=ErrorCode.INTERNAL_ERROR,
                cause=e
            )
    return wrapper


def create_error_response(
    error: Exception,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """创建标准化错误响应"""
    if isinstance(error, MCPError):
        response = error.to_dict()
    else:
        response = {
            "error": True,
            "error_code": ErrorCode.INTERNAL_ERROR.value,
            "message": str(error),
            "details": {"error_type": type(error).__name__}
        }
    
    if include_traceback:
        import traceback
        response["traceback"] = traceback.format_exc()
    
    return response


def validate_required_params(params: Dict[str, Any], required_fields: list) -> None:
    """验证必需参数"""
    missing_fields = []
    for field in required_fields:
        if field not in params or params[field] is None or params[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            message=f"Missing required parameters: {', '.join(missing_fields)}",
            parameter_name="multiple",
            details={"missing_fields": missing_fields}
        )


def validate_shipper_code(shipper_code: str, supported_codes: Dict[str, str]) -> str:
    """验证快递公司编码"""
    if not shipper_code:
        raise ValidationError(
            message="Shipper code is required",
            parameter_name="shipper_code"
        )
    
    shipper_code = shipper_code.upper().strip()
    
    if shipper_code not in supported_codes:
        available_codes = ", ".join(list(supported_codes.keys())[:10])
        raise BusinessLogicError(
            message=f"Unsupported shipper code: {shipper_code}",
            error_code=ErrorCode.SHIPPER_NOT_SUPPORTED,
            business_context={
                "provided_code": shipper_code,
                "available_codes": available_codes,
                "total_supported": len(supported_codes)
            }
        )
    
    return shipper_code


def validate_logistics_code(logistics_code: str) -> str:
    """验证快递单号"""
    if not logistics_code:
        raise ValidationError(
            message="Logistics code is required",
            parameter_name="logistics_code"
        )
    
    logistics_code = logistics_code.strip()
    
    # 基本格式验证
    if len(logistics_code) < 6 or len(logistics_code) > 30:
        raise ValidationError(
            message="Logistics code length should be between 6-30 characters",
            parameter_name="logistics_code",
            parameter_value=logistics_code,
            expected_format="6-30 characters"
        )
    
    # 检查是否包含有效字符
    if not logistics_code.replace("-", "").replace("_", "").isalnum():
        raise ValidationError(
            message="Logistics code should only contain letters, numbers, hyphens and underscores",
            parameter_name="logistics_code",
            parameter_value=logistics_code,
            expected_format="alphanumeric with hyphens/underscores"
        )
    
    return logistics_code