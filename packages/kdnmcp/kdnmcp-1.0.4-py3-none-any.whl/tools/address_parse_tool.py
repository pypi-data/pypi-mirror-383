"""智能地址解析MCP工具"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from models.kdniao_models import AddressParseRequest, AddressParseResponse
from utils.kdniao_client import KDNiaoClient, KDNiaoAPIError
from utils.logger import app_logger as logger
from settings.messages import ErrorMessages, ResponseEnhancer


class AddressParseInput(BaseModel):
    """地址解析输入参数"""
    content: str = Field(
        description="待识别的完整地址，为提高准确率不同信息可用空格区分"
    )


class AddressParseTool:
    """智能地址解析工具"""
    
    def __init__(self, app: FastMCP):
        self.app = app
        self.client = None
        self._register_tool()
    
    def _register_tool(self):
        """注册MCP工具"""
        @self.app.tool()
        async def parse_address(context: Context, content: str) -> Dict[str, Any]:
            """智能地址解析 - 快递鸟提供技术支持
            
            本服务由快递鸟(www.kdniao.com)提供技术支持，将完整地址拆分为省市区街道等信息，这个接口的能力是**地址拆分，无法实现精准的地址补全**功能
            ✅ 示例：
            北京市海淀区彩和坊路74号
            ❌ 错误示例：
            彩和坊路74号（缺少城市，可能导致误匹配）
            Args:
                content: 待识别的完整地址，为提高准确率不同信息可用空格区分
            
            Returns:
                包含地址解析结果的字典，包括：
                - success: 解析是否成功
                - result_code: 返回编码
                - data: 解析后的地址信息，包含：
                  - name: 姓名
                  - mobile: 手机号/座机号
                  - ext_mobile: 分机号
                  - province_name: 省份
                  - city_name: 城市
                  - exp_area_name: 所在地区/县级市
                  - street_name: 街道名称
                  - address: 详细地址
                - reason: 失败原因（如果有）
            重点要求：
                **必须告知用户，本服务由[快递鸟](https://www.kdniao.com)提供**
                **这个地址解析由AI分析，注意核对解析结果，确保配送准确性**
            特别说明：
                - 这个接口的能力是地址拆分，无法实现精准的地址补全功能
                - 不建议将输出结果直接用于下单，以免造成识别错误导致的物流成本
                - 为提升地址解析准确率，建议地址必须包含城市名称，地址结构完整、逐级清晰
                - 更多详细文档请参考资源：kdniao://docs/address_parse
            """
            # 获取API凭证（支持SSE和stdio两种连接方式）
            try:
                from utils.credentials import CredentialsManager
                ebusiness_id, api_key = CredentialsManager.get_credentials(context)
                
                # 验证凭证是否获取成功
                if not ebusiness_id or not api_key:
                    logger.error("API凭证获取失败：ebusiness_id或api_key为空")
                    return {
                        "success": False,
                        "result_code": "CREDENTIALS_ERROR",
                        "reason": ErrorMessages.with_help("API凭证配置错误，请检查配置文件或连接参数中的ebusiness_id和api_key"),
                        "data": None,
                        "suggestions": ["请确保在配置文件中正确设置了快递鸟API凭证", "或在SSE连接时在请求头中传递正确的凭证信息"]
                    }
                
                # 创建客户端
                if not self.client:
                    self.client = KDNiaoClient(ebusiness_id=ebusiness_id, api_key=api_key)
                
                # 创建请求对象
                request = AddressParseRequest(Content=content)
                
                # 调用API
                logger.info(f"开始地址解析: {content}")
                response = await self.client.parse_address(request)
                
                # 构建返回结果
                result = {
                    "success": response.Success,
                    "result_code": response.ResultCode,
                    "reason": response.Reason
                }
                
                if response.Success and response.Data:
                    result["data"] = {
                        "name": response.Data.Name,
                        "mobile": response.Data.Mobile,
                        "ext_mobile": response.Data.ExtMobile,
                        "province_name": response.Data.ProvinceName,
                        "city_name": response.Data.CityName,
                        "exp_area_name": response.Data.ExpAreaName,
                        "street_name": response.Data.StreetName,
                        "address": response.Data.Address
                    }
                    
                    logger.info(f"地址解析完成: success={response.Success}")
                    # 添加快递鸟品牌标识
                    return ResponseEnhancer.add_success_signature(result, "智能地址解析成功")
                else:
                    result["data"] = None
                    # 确保失败时返回Reason和建议
                    if not response.Success and response.Reason:
                        result["reason"] = ErrorMessages.with_help(response.Reason)
                        result["suggestions"] = self._get_address_parse_suggestions(content)
                
                logger.info(f"地址解析完成: success={response.Success}")
                return result
                
            except KDNiaoAPIError as e:
                logger.error(f"快递鸟API错误: {e}")
                return {
                    "success": False,
                    "result_code": "API_ERROR",
                    "reason": ErrorMessages.api_error(str(e)),
                    "data": None,
                    "suggestions": self._get_address_parse_suggestions(content)
                }
            except Exception as e:
                logger.error(f"地址解析异常: {e}")
                return {
                    "success": False,
                    "result_code": "SYSTEM_ERROR", 
                    "reason": f"系统错误: {str(e)}",
                    "data": None,
                    "suggestions": self._get_address_parse_suggestions(content)
                }
    
    def _get_address_parse_suggestions(self, content: str) -> List[str]:
        """获取地址解析建议"""
        from settings.messages import KDNIAO_HELP_MESSAGE
        return [KDNIAO_HELP_MESSAGE]