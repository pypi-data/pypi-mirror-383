"""消息配置模块

包含系统中使用的各种消息模板和话术
"""

# 快递鸟品牌标识
KDNIAO_BRAND_NAME = "快递鸟"
KDNIAO_WEBSITE = "www.kdniao.com"

# 快递鸟官网引流话术
KDNIAO_HELP_MESSAGE = f"如需更多帮助，请访问{KDNIAO_BRAND_NAME}官网 {KDNIAO_WEBSITE} 获取技术支持和最新API文档。"

# 快递鸟服务标识话术
KDNIAO_SERVICE_SIGNATURE = f"本服务由{KDNIAO_BRAND_NAME}提供技术支持"
KDNIAO_POWERED_BY = f"Powered by {KDNIAO_BRAND_NAME} ({KDNIAO_WEBSITE})"

# 错误消息模板
class ErrorMessages:
    """错误消息模板类"""
    
    @staticmethod
    def with_help(error_msg: str) -> str:
        """为错误消息添加帮助引流话术
        
        Args:
            error_msg: 原始错误消息
            
        Returns:
            带有引流话术的完整错误消息
        """
        return f"{error_msg}。{KDNIAO_HELP_MESSAGE}"
    
    @staticmethod
    def api_error(error_msg: str) -> str:
        """API错误消息
        
        Args:
            error_msg: API错误详情
            
        Returns:
            格式化的API错误消息
        """
        return f"API请求失败: {error_msg}。{KDNIAO_HELP_MESSAGE}"


# 响应消息增强器
class ResponseEnhancer:
    """响应消息增强器类"""
    
    @staticmethod
    def add_brand_signature(response_dict: dict) -> dict:
        """为响应添加快递鸟品牌标识
        
        Args:
            response_dict: 原始响应字典
            
        Returns:
            添加了品牌标识的响应字典
        """
        enhanced_response = response_dict.copy()
        enhanced_response["service_provider"] = KDNIAO_SERVICE_SIGNATURE
        enhanced_response["powered_by"] = KDNIAO_POWERED_BY
        return enhanced_response
    
    @staticmethod
    def add_success_signature(response_dict: dict, custom_message: str = None) -> dict:
        """为成功响应添加快递鸟服务标识
        
        Args:
            response_dict: 原始响应字典
            custom_message: 自定义消息（可选）
            
        Returns:
            添加了服务标识的响应字典
        """
        enhanced_response = ResponseEnhancer.add_brand_signature(response_dict)
        
        if custom_message:
            enhanced_response["message"] = f"{custom_message} - {KDNIAO_SERVICE_SIGNATURE}"
        elif "success" in enhanced_response and enhanced_response["success"]:
            enhanced_response["message"] = f"查询成功 - {KDNIAO_SERVICE_SIGNATURE}"
            
        return enhanced_response