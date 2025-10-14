"""配置管理模块"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class KDNiaoConfig(BaseSettings):
    """快递鸟API配置"""
    ebusiness_id: str = Field(..., alias="EBUSINESS_ID")
    api_key: str = Field(..., alias="API_KEY")
    api_url: str = Field("https://api.kdniao.com/api/dist", alias="KDNIAO_API_URL")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')


class MCPServerConfig(BaseSettings):
    """MCP服务器配置"""
    name: str = Field("快递鸟物流服务 - KDNiao Logistics MCP Service", alias="MCP_SERVER_NAME")
    port: int = Field(8000, alias="MCP_SERVER_PORT")
    host: str = Field("0.0.0.0", alias="MCP_SERVER_HOST")
    
    model_config = ConfigDict(
        populate_by_name=True,
        # 允许重新验证以重新读取环境变量
        validate_assignment=True,
        extra='ignore'
    )


class LogConfig(BaseSettings):
    """日志配置"""
    level: str = Field("INFO", alias="LOG_LEVEL")
    format: str = Field("json", alias="LOG_FORMAT")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')


class ProtocolConfig(BaseSettings):
    """协议配置"""
    enable_sse: bool = Field(True, alias="ENABLE_SSE")
    enable_stdio: bool = Field(True, alias="ENABLE_STDIO")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')


class RequestConfig(BaseSettings):
    """请求配置"""
    timeout: int = Field(30, alias="REQUEST_TIMEOUT")
    max_retries: int = Field(3, alias="MAX_RETRIES")
    
    model_config = ConfigDict(populate_by_name=True, extra='ignore')


class AppConfig:
    """应用配置聚合类"""
    
    def __init__(self):
        self.kdniao = KDNiaoConfig()
        self.mcp_server = MCPServerConfig()
        self.log = LogConfig()
        self.protocol = ProtocolConfig()
        self.request = RequestConfig()
    
    def validate(self) -> bool:
        """验证配置完整性"""
        try:
            # 检查必需的配置项
            if not self.kdniao.ebusiness_id:
                raise ValueError("KDNIAO_EBUSINESS_ID is required")
            if not self.kdniao.api_key:
                raise ValueError("KDNIAO_API_KEY is required")
            
            # 检查协议配置
            if not self.protocol.enable_sse and not self.protocol.enable_stdio:
                raise ValueError("At least one protocol (SSE or STDIO) must be enabled")
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# 全局配置实例
config = AppConfig()