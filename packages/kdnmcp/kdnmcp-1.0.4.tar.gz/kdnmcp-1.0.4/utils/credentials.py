"""API凭证获取工具"""

from typing import Dict, Any, Optional, Tuple
from fastmcp import Context
from utils.logger import app_logger as logger
from settings import config


class CredentialsManager:
    """API凭证管理器
    
    用于统一处理不同连接方式下的API凭证获取
    - SSE连接：从连接参数中获取
    - stdio连接：从配置文件中获取
    """
    
    @staticmethod
    def _get_transport_mode(context: Context) -> str:
        """确定当前的启动方式
        
        Args:
            context: FastMCP上下文对象
            
        Returns:
            str: 启动方式，"sse" 或 "stdio"
        """
        try:
            # 1. 优先从服务器实例获取传输模式（最可靠的方式）
            if hasattr(context, 'fastmcp') and hasattr(context.fastmcp, '_server_instance'):
                server_instance = context.fastmcp._server_instance
                if hasattr(server_instance, 'transport_mode'):
                    transport_mode = server_instance.transport_mode
                    logger.debug(f"Got transport mode from server instance: {transport_mode}")
                    return transport_mode
            # 6. 默认为stdio模式
            logger.debug("No transport mode indicators found, defaulting to stdio")
            return "stdio"
            
        except Exception as e:
            logger.warning(f"Error determining transport mode: {e}, defaulting to stdio")
            return "stdio"
    @staticmethod
    def get_credentials(context: Context) -> Tuple[Optional[str], Optional[str]]:
        """获取API凭证
        
        Args:
            context: FastMCP上下文对象
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (ebusiness_id, api_key)元组
        """
        # 初始化凭证变量
        ebusiness_id = None
        api_key = None
        
        # 确定当前的启动方式
        transport_mode = CredentialsManager._get_transport_mode(context)
        logger.info(f"Current transport mode: {transport_mode}")
        
        if transport_mode == "sse":
            # SSE连接方式：从连接参数中获取凭证
            request = context.get_http_request()
            headers = dict(request.headers)
            ebusiness_id = headers.get('ebusiness_id') or headers.get('EBUSINESS_ID') or None
            api_key = headers.get('api_key') or headers.get('API_KEY') or None
            
        if transport_mode == "http":
            # http连接方式：从连接参数中获取凭证
            request = context.get_http_request()
            query_params = dict(request.query_params)
            ebusiness_id = query_params.get('ebusiness_id') or query_params.get('EBUSINESS_ID') or None
            api_key = query_params.get('api_key') or query_params.get('API_KEY') or None
        
        
            
       

        if transport_mode == "stdio":
            try:
                ebusiness_id = config.kdniao.ebusiness_id
                api_key = config.kdniao.api_key
                logger.info(f"Using credentials from configuration file (transport: {transport_mode})")
            except Exception as e:
                logger.error(f"Failed to get credentials from configuration: {e}")
        
        logger.info(f"ebusiness_id: {ebusiness_id}")
        logger.info(f"api_key: {api_key}")
        return ebusiness_id, api_key