"""快递鸟MCP服务器"""

import os
import asyncio
from typing import Dict, Any, List, Optional

from fastmcp import FastMCP, Context
from settings import config
from tools.tracking_tool import TrackingTool
from tools.recognize_tool import RecognizeTool
from tools.timeline_tool import TimelineTool
from tools.address_parse_tool import AddressParseTool
from tools.service_point_tool import ServicePointTool
from tools.cross_border_tracking_tool import CrossBorderTrackingTool
from utils.kdniao_client import KDNiaoClient
from utils.logger import app_logger as logger
from docs.doc_provider import DocProvider
from datetime import datetime
from models.kdniao_models import RecognizeRequest


class KDNiaoMCPServer:
    """快递鸟MCP服务器"""
    
    def __init__(self):
        """初始化服务器"""
        # 设置日志
        self._setup_logging()
        
        # 设置鉴权
        self.auth_manager = self._setup_auth()
        
        # 初始化传输模式（默认为stdio）
        self.transport_mode = "stdio"
        
        # 创建FastMCP应用
        self.app = FastMCP(
            name=config.mcp_server.name
            # 移除auth_manager参数
        )
        
        
        # 将server实例引用添加到app中，方便其他模块访问
        self.app._server_instance = self
        
        # 初始化文档提供者
        self.doc_provider = DocProvider()
        
        # 注册工具
        self.tools = {}
        self._register_tools()
        
        # 注册资源
        self._register_resources()
        
        logger.info(f"KDNiao MCP server initialized")
    
    def _setup_logging(self):
        """设置日志"""
        # 日志配置已在logger模块中完成
        logger.info(f"Logging initialized with level {config.log.level}")
    
    def _setup_auth(self):
        """设置鉴权"""
        # 在新版本的fastmcp中，不再使用AuthManager
        # 返回None，FastMCP应用将使用默认的鉴权机制
        logger.info("Authentication disabled in new FastMCP version")
        return None
    
    def _register_tools(self):
        """注册MCP工具"""
        try:
            # 注册轨迹查询工具
            self.tools['tracking'] = TrackingTool(self.app)
            
            # 注册单号识别工具
            self.tools['recognize'] = RecognizeTool(self.app)
            
            # 注册时效预估工具
            self.tools['timeline'] = TimelineTool(self.app)
            
            # # 注册地址解析工具
            self.tools['address_parse'] = AddressParseTool(self.app)
            
            # 注册网点查询工具
            self.tools['service_point'] = ServicePointTool(self.app)
            
            # 注册跨境小包查询工具
            self.tools['cross_border_tracking'] = CrossBorderTrackingTool(self.app)
            
            logger.info(f"All {len(self.tools)} tools registered successfully")
        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            raise
    
    def _register_resources(self):
        """注册MCP资源"""
        try:
            @self.app.resource("kdniao://config")
            async def get_config() -> Dict[str, Any]:
                """获取服务配置信息"""
                return {
                    "server_info": {
                        "name": "快递鸟MCP服务",
                        "version": "1.0.0",
                        "description": "提供快递物流查询服务"
                    },
                    "api_info": {
                        "provider": "快递鸟",
                        "base_url": config.kdniao.api_url,
                        "supported_features": [
                            "轨迹查询",
                            "单号识别", 
                            "时效预估",
                            "地址解析"
                        ]
                    },
                    "supported_shippers": list(self.tools['tracking'].get_supported_shippers()) if 'tracking' in self.tools else []
                }
            
            @self.app.resource("kdniao://health")
            async def health_check(context: Context) -> Dict[str, Any]:
                """健康检查资源"""
                return {
                    "status": "ok",
                    "service": "kdniao",
                    "version": "1.0.0",
                    "timestamp": datetime.now().isoformat()
                }
            
            @self.app.resource("kdniao://shippers")
            async def get_supported_shippers() -> Dict[str, Any]:
                """获取支持的快递公司列表"""
                if 'tracking' in self.tools:
                    shippers = self.tools['tracking'].get_supported_shippers()
                    return {
                        "total_count": len(shippers),
                        "shippers": shippers
                    }
                return {"total_count": 0, "shippers": []}
            
            
            @self.app.resource("kdniao://docs")
            async def get_kdniao_docs() -> Dict[str, Any]:
                """获取快递鸟API文档信息"""
                try:
                    # 获取所有文档资源
                    docs = self.doc_provider.get_all_docs()
                    return docs.dict()
                except Exception as e:
                    logger.error(f"Failed to get KDNiao docs: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/tracking")
            async def get_tracking_docs() -> Dict[str, Any]:
                """获取轨迹查询文档信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return docs.tracking.dict()
                except Exception as e:
                    logger.error(f"Failed to get tracking docs: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/recognize")
            async def get_recognize_docs() -> Dict[str, Any]:
                """获取单号识别文档信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return docs.recognize.dict()
                except Exception as e:
                    logger.error(f"Failed to get recognize docs: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/timeline")
            async def get_timeline_docs() -> Dict[str, Any]:
                """获取时效预估文档信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return docs.timeline.dict()
                except Exception as e:
                    logger.error(f"Failed to get timeline docs: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/address_parse")
            async def get_address_parse_docs() -> Dict[str, Any]:
                """获取地址解析文档信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return docs.address_parse.dict()
                except Exception as e:
                    logger.error(f"Failed to get address parse docs: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/state_codes")
            async def get_state_codes() -> Dict[str, Any]:
                """获取物流状态码信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return {"state_codes": [code.dict() for code in docs.state_codes]}
                except Exception as e:
                    logger.error(f"Failed to get state codes: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/state_ex_codes")
            async def get_state_ex_codes_docs() -> Dict[str, Any]:
                """获取详细物流状态码信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return {"state_ex_codes": [code.dict() for code in docs.state_ex_codes]}
                except Exception as e:
                    logger.error(f"Failed to get state ex codes docs: {e}")
                    return {"error": str(e)}
                    
            @self.app.resource("kdniao://docs/supported_shippers")
            async def get_supported_shippers_docs() -> Dict[str, Any]:
                """获取单号识别支持的快递公司文档"""
                try:
                    supported_shippers = self.doc_provider._get_supported_shippers_doc()
                    return supported_shippers
                except Exception as e:
                    logger.error(f"Failed to get supported shippers docs: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/result_codes")
            async def get_result_codes() -> Dict[str, Any]:
                """获取返回编码列表信息"""
                try:
                    # 从文档提供者获取返回编码列表
                    result_codes = [
                        {"code": "100", "name": "成功", "description": "成功"},
                        {"code": "101", "name": "缺少必要参数", "description": "缺少必要参数"},
                        {"code": "102", "name": "校验问题", "description": "校验问题"},
                        {"code": "103", "name": "格式问题", "description": "格式问题"},
                        {"code": "104", "name": "用户问题", "description": "用户问题"},
                        {"code": "105", "name": "系统问题", "description": "系统问题"},
                        {"code": "106", "name": "接口问题", "description": "接口问题"},
                        {"code": "107", "name": "数据问题", "description": "数据问题"},
                        {"code": "108", "name": "网络问题", "description": "网络问题"},
                        {"code": "109", "name": "其他问题", "description": "其他问题"}
                    ]
                    return {"result_codes": result_codes}
                except Exception as e:
                    logger.error(f"Failed to get result codes: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/cross_border_tracking")
            async def get_cross_border_tracking_docs() -> Dict[str, Any]:
                """获取跨境小包查询文档信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return docs.cross_border_tracking.dict()
                except Exception as e:
                    logger.error(f"Failed to get cross border tracking docs: {e}")
                    return {"error": str(e)}
            
            @self.app.resource("kdniao://docs/cross_border_state_codes")
            async def get_cross_border_state_codes() -> Dict[str, Any]:
                """获取跨境小包状态码信息"""
                try:
                    docs = self.doc_provider.get_all_docs()
                    return {"cross_border_state_codes": [code.dict() for code in docs.cross_border_state_codes]}
                except Exception as e:
                    logger.error(f"Failed to get cross border state codes: {e}")
                    return {"error": str(e)}
            
            logger.info("Resources registered successfully")
        except Exception as e:
            logger.error(f"Failed to register resources: {e}")
            raise
    
    async def start_server(self, transport: str = "stdio"):
        """启动MCP服务器"""
        try:
            # 设置传输模式
            self.transport_mode = transport
            logger.info(f"Starting KDNiao MCP server with {transport} transport...")
            
            # 验证配置
            if not config.kdniao.ebusiness_id or not config.kdniao.api_key:
                logger.warning("Missing required KDNiao API credentials in config, will try to get from connection parameters")
            
            # 创建并启动服务器
            if transport == "stdio":
                # STDIO模式下，鉴权通过环境变量或配置文件控制
                if self.auth_manager and hasattr(self.auth_manager, 'enable_auth') and self.auth_manager.enable_auth:
                    logger.warning("Authentication is enabled but STDIO transport doesn't support HTTP-based auth")
                    logger.info("Consider using token-based validation in your MCP client")
                await self.app.run_async()
            elif transport == "sse":
                # 使用FastMCP的SSE服务器
                logger.info(f"SSE server starting on {config.mcp_server.host}:{config.mcp_server.port}")
                if self.auth_manager and hasattr(self.auth_manager, 'enable_auth') and self.auth_manager.enable_auth:
                    logger.info("Authentication is enabled for SSE transport")
                    logger.info(f"Use header '{config.mcp_server.auth_header_name}' or 'Authorization: Bearer <token>'")
                
                
                logger.info(f"config.mcp_server: {config.mcp_server}")

                # 使用FastMCP的run_sse_async方法启动SSE服务器
                await self.app.run_sse_async(
                    host=config.mcp_server.host,
                    port=config.mcp_server.port
                )
            elif transport == "http":
                if not config.protocol.enable_http:
                    raise ValueError("HTTP transport is disabled in configuration")
                
                # 使用FastMCP的HTTP服务器
                logger.info(f"HTTP server starting on {config.mcp_server.host}:{config.mcp_server.port}")
                if self.auth_manager and hasattr(self.auth_manager, 'enable_auth') and self.auth_manager.enable_auth:
                    logger.info("Authentication is enabled for HTTP transport")
                    logger.info(f"Use header '{config.mcp_server.auth_header_name}' or 'Authorization: Bearer <token>'")
                
                
                logger.info(f"config.mcp_server: {config.mcp_server}")

                # 使用FastMCP的run_http_async方法启动HTTP服务器
                await self.app.run_http_async(
                    host=config.mcp_server.host,
                    port=config.mcp_server.port
                )
            else:
                raise ValueError(f"Unsupported transport: {transport}")
                
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    def get_connection_params(self, session_id: str = 'default') -> Dict[str, Any]:
        """获取连接参数"""
        if hasattr(self, 'connection_middleware'):
            return self.connection_middleware.get_connection_params(session_id) or {}
        return {}
    
    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """获取所有连接的参数"""
        if hasattr(self, 'connection_middleware'):
            return self.connection_middleware.get_all_connections()
        return {}
    
    async def shutdown(self):
        """关闭服务器"""
        try:
            logger.info("Shutting down KDNiao MCP server...")
            # 清理资源
            self.tools.clear()
            logger.info("Server shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


async def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="快递鸟MCP服务器")
    parser.add_argument("--transport", type=str, default="stdio", choices=["stdio", "sse", "http"], help="传输方式: stdio、sse或http")
    args = parser.parse_args()
    
    server = None
    try:
        # 创建服务器实例
        server = KDNiaoMCPServer()
        
        # 获取传输方式，优先使用命令行参数，其次使用环境变量
        transport = args.transport or os.getenv("MCP_TRANSPORT", "stdio")
        
        # 启动服务器
        await server.start_server(transport)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        if server:
            await server.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server failed to start: {e}")
        exit(1)