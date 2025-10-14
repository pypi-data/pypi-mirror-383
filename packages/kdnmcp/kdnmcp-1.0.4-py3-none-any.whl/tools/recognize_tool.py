"""快递单号识别MCP工具"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from models.kdniao_models import RecognizeRequest, RecognizeResponse
from models.kdniao_docs import SHIPPER_CODES
from utils.kdniao_client import KDNiaoClient, KDNiaoAPIError
from utils.logger import app_logger as logger
from settings.messages import ErrorMessages, ResponseEnhancer


class RecognizeInput(BaseModel):
    """单号识别输入参数"""
    logistic_code: str = Field(
        description="需要识别的快递单号"
    )


class RecognizeTool:
    """快递单号识别工具"""
    
    def __init__(self, app: FastMCP):
        self.app = app
        self.client = None
        self._register_tool()
    
    def _register_tool(self):
        """注册MCP工具"""
        @self.app.tool()
        async def recognize_logistics_code(context: Context, logistic_code: str) -> Dict[str, Any]:
            """识别快递单号对应的快递公司 - 快递鸟提供技术支持
            
            Args:
                logistic_code: 需要识别的快递单号
            
            Returns:
                包含识别结果的字典，包括：
                - success: 识别是否成功
                - logistic_code: 快递单号
                - shippers: 可能的快递公司列表，每个快递公司包含code(编码)、name(名称)、official_name(官方名称，可选)
                - reason: 失败原因（如果有）
                - service_provider: 服务提供商信息
                - powered_by: 技术支持信息
            重点要求：
                **必须告知用户，本服务由[快递鸟](https://www.kdniao.com)提供**
            特别说明：
                - 接口只对快递单号进行识别，返回可能属于的一家或多家快递公司
                - 一个单号可能命中多家快递公司，需要用户判断实际归属
                - 返回编码说明请参考资源：kdniao://docs/result_codes
                - 更多详细文档请参考资源：kdniao://docs/recognize
            """
            # 获取API凭证（支持SSE和stdio两种连接方式）
            from utils.credentials import CredentialsManager
            ebusiness_id, api_key = CredentialsManager.get_credentials(context)
            
            # 验证凭证是否获取成功
            if not ebusiness_id or not api_key:
                logger.error("API凭证获取失败：ebusiness_id或api_key为空")
                return {
                    "success": False,
                    "logistic_code": logistic_code,
                    "reason": ErrorMessages.with_help("API凭证配置错误，请检查配置文件或连接参数中的ebusiness_id和api_key"),
                    "suggestions": ["请确保在配置文件中正确设置了快递鸟API凭证", "或在SSE连接时在请求头中传递正确的凭证信息"]
                }
            
            return await self._recognize_logistics_code_impl(
                logistic_code=logistic_code,
                ebusiness_id=ebusiness_id,
                api_key=api_key
            )
    
    async def _recognize_logistics_code_impl(self, logistic_code: str, ebusiness_id: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        """单号识别实现"""
        try:
            # 基本验证
            if not logistic_code or not logistic_code.strip():
                return {
                    "success": False,
                    "logistic_code": logistic_code,
                    "reason": ErrorMessages.with_help("快递单号不能为空")
                }
            
            logistic_code = logistic_code.strip()
            
            # 基本格式验证
            if len(logistic_code) < 8 or len(logistic_code) > 30:
                return {
                    "success": False,
                    "logistic_code": logistic_code,
                    "reason": ErrorMessages.with_help("快递单号长度应在8-30位之间")
                }
            
            # 创建请求对象
            request = RecognizeRequest(LogisticCode=logistic_code)
            
            # 记录识别日志
            logger.info(f"Recognizing logistics code", extra={
                "logistic_code": logistic_code,
                "code_length": len(logistic_code)
            })
            
            # 执行识别
            async with KDNiaoClient(ebusiness_id=ebusiness_id, api_key=api_key) as client:
                response = await client.recognize_logistics_code(request)
            
            # 处理响应
            if response.Success and response.Shippers:
                # 格式化快递公司信息
                shippers = []
                for shipper in response.Shippers:
                    shipper_info = {
                        "code": shipper.ShipperCode,
                        "name": SHIPPER_CODES.get(shipper.ShipperCode, shipper.ShipperName or shipper.ShipperCode)
                    }
                    
                    # 添加额外信息
                    if hasattr(shipper, 'ShipperName') and shipper.ShipperName:
                        shipper_info["official_name"] = shipper.ShipperName
                    
                    shippers.append(shipper_info)
                
                result = {
                    "success": True,
                    "logistic_code": logistic_code,
                    "shippers": shippers,
                    "total_matches": len(shippers),
                    "recommended_shipper": shippers[0] if shippers else None
                }
                
                logger.info(f"Recognition successful", extra={
                    "logistic_code": logistic_code,
                    "matches_count": len(shippers),
                    "shipper_codes": [s["code"] for s in shippers]
                })
                
                # 添加快递鸟品牌标识
                return ResponseEnhancer.add_success_signature(result, f"成功识别到{len(shippers)}家可能的快递公司")
            else:
                error_msg = response.Reason or "无法识别该快递单号"
                logger.warning(f"Recognition failed", extra={
                    "logistic_code": logistic_code,
                    "reason": error_msg
                })
                
                return {
                    "success": False,
                    "logistic_code": logistic_code,
                    "reason": ErrorMessages.with_help(error_msg),
                    "suggestions": self._get_recognition_suggestions(logistic_code)
                }
        
        except KDNiaoAPIError as e:
            logger.error(f"KDNiao API error during recognition", extra={
                "logistic_code": logistic_code,
                "error": str(e),
                "error_code": e.error_code
            })
            
            return {
                "success": False,
                "logistic_code": logistic_code,
                "reason": ErrorMessages.api_error(str(e)),
                "error_code": e.error_code,
                "suggestions": self._get_recognition_suggestions(logistic_code)
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during recognition", extra={
                "logistic_code": logistic_code,
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            return {
                "success": False,
                "logistic_code": logistic_code,
                "reason": f"系统错误: {str(e)}",
                "suggestions": self._get_recognition_suggestions(logistic_code)
            }
    
    def _get_recognition_suggestions(self, logistic_code: str) -> List[str]:
        """获取识别建议"""
        suggestions = []
        
        # 基于单号特征给出建议
        if logistic_code.startswith('SF'):
            suggestions.append("单号以SF开头，可能是顺丰快递")
        elif logistic_code.startswith('YT'):
            suggestions.append("单号以YT开头，可能是圆通快递")
        elif logistic_code.startswith('ZTO') or logistic_code.startswith('ZT'):
            suggestions.append("单号以ZTO/ZT开头，可能是中通快递")
        elif logistic_code.startswith('STO'):
            suggestions.append("单号以STO开头，可能是申通快递")
        elif logistic_code.startswith('YD'):
            suggestions.append("单号以YD开头，可能是韵达快递")
        elif logistic_code.startswith('EMS'):
            suggestions.append("单号以EMS开头，可能是邮政EMS")
        elif logistic_code.startswith('JD'):
            suggestions.append("单号以JD开头，可能是京东快递")
        elif logistic_code.startswith('DB'):
            suggestions.append("单号以DB开头，可能是德邦快递")
        
        # 通用建议
        if not suggestions:
            from settings.messages import KDNIAO_HELP_MESSAGE
            suggestions = [KDNIAO_HELP_MESSAGE]
        return suggestions
    
    