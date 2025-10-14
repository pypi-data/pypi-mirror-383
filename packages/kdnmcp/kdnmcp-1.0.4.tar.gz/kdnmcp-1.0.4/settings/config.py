"""配置管理模块"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv

# 加载环境变量
# load_dotenv()


class KDNiaoConfig(BaseSettings):
    """快递鸟API配置"""
    ebusiness_id: Optional[str] = Field(None, alias="EBUSINESS_ID")
    api_key:  Optional[str] = Field(None, alias="API_KEY")
    api_url: str = Field("https://api.kdniao.com/api/dist", alias="KDNIAO_API_URL")
    
    # model_config = ConfigDict(
    #     env_prefix="KDNIAO_",
    #     env_file=".env",
    #     populate_by_name=True,
    #     extra='ignore'
    # )


class MCPServerConfig(BaseSettings):
    """MCP服务器配置"""
    name: str = Field("快递鸟物流服务 - KDNiao Logistics MCP Service", alias="MCP_SERVER_NAME")
    port: int = Field(8000, alias="MCP_SERVER_PORT")
    host: str = Field("0.0.0.0", alias="MCP_SERVER_HOST")
    
    # model_config = ConfigDict(
    #     env_prefix="MCP_",
    #     env_file=".env",
    #     validate_assignment=True,
    #     populate_by_name=True,
    #     extra='ignore'
    # )


class LogConfig(BaseSettings):
    """日志配置"""
    level: str = Field("INFO", alias="LOG_LEVEL")
    format: str = Field("json", alias="LOG_FORMAT")
    
    model_config = ConfigDict(env_prefix="LOG_", populate_by_name=True, extra='ignore')


class ProtocolConfig(BaseSettings):
    """协议配置"""
    enable_sse: bool = Field(True, alias="ENABLE_SSE")
    http_timeout: int = Field(60, alias="HTTP_TIMEOUT")
    
    model_config = ConfigDict(env_prefix="PROTOCOL_", populate_by_name=True, extra='ignore')


class RequestConfig(BaseSettings):
    """请求配置"""
    timeout: int = Field(30, alias="REQUEST_TIMEOUT")
    max_retries: int = Field(3, alias="MAX_RETRIES")
    
    model_config = ConfigDict(env_prefix="REQUEST_", populate_by_name=True, extra='ignore')


class AppConfig:
    """应用配置聚合类"""
    
    def __init__(self):
        self.reload()
    
    def reload(self):
        """重新加载配置"""
        # 重新创建配置实例
        self.kdniao = KDNiaoConfig()
        self.mcp_server = MCPServerConfig()
        self.log = LogConfig()
        self.protocol = ProtocolConfig()
        self.request = RequestConfig()
        
        # 手动更新端口配置（如果环境变量存在）
        if 'MCP_SERVER_PORT' in os.environ:
            try:
                self.mcp_server.port = int(os.environ['MCP_SERVER_PORT'])
            except ValueError:
                pass  # 如果转换失败，保持默认值
    
    def validate(self) -> bool:
        """验证配置完整性"""
        try:
            # 检查必需的配置项
            # if not self.kdniao.ebusiness_id:
            #     raise ValueError("EBUSINESS_ID is required")
            # if not self.kdniao.api_key:
            #     raise ValueError("API_KEY is required")
            
            # 检查协议配置
            if not self.protocol.enable_sse and not self.protocol.enable_stdio and not self.protocol.enable_http:
                raise ValueError("At least one protocol (SSE, STDIO, or HTTP) must be enabled")
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# 全局配置实例
config = AppConfig()