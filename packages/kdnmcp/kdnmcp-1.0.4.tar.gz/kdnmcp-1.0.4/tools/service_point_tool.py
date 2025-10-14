"""网点查询MCP工具"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from models.kdniao_models import ServicePointRequest, ServicePointResponse
from models.kdniao_docs import SHIPPER_CODES
from utils.kdniao_client import KDNiaoClient, KDNiaoAPIError
from utils.logger import app_logger as logger
from settings.messages import ErrorMessages, ResponseEnhancer


class ServicePointInput(BaseModel):
    """网点查询输入参数"""
    shipper_code: str = Field(
        description="快递公司编码，如：SF(顺丰)、YTO(圆通)、ZTO(中通)、STO(申通)、YD(韵达)、JTSD(极兔)、DBL(德邦)、EMS(EMS)、YZPY(邮政平邮)"
    )
    province_name: str = Field(
        description="省份名称，如：广东省、北京市"
    )
    city_name: Optional[str] = Field(
        default=None,
        description="城市名称，如：广州市、深圳市"
    )
    area_name: Optional[str] = Field(
        default=None,
        description="区县名称，如：黄埔区、南山区"
    )
    address: Optional[str] = Field(
        default=None,
        description="地址关键词（模糊匹配），顺丰和极兔必填"
    )


class ServicePointTool:
    """网点查询工具"""
    
    def __init__(self, app: FastMCP):
        self.app = app
        self.client = None
        self._register_tool()
    
    def _register_tool(self):
        """注册MCP工具"""
        @self.app.tool()
        async def query_service_points(
            context: Context,
            shipper_code: str,
            province_name: str,
            city_name: Optional[str] = None,
            area_name: Optional[str] = None,
            address: Optional[str] = None,
        ) -> Dict[str, Any]:
            """查询快递网点信息 - 快递鸟提供技术支持
            
            根据地址查询网点的详细信息（详细地址、网点联系人、电话、服务时间、经纬度）
            
            支持的快递公司：
            - 顺丰速运(SF)、中通快递(ZTO)、圆通快递(YTO)、申通快递(STO)
            - 韵达快递(YD)、极兔速递(JTSD)、德邦快递(DBL)、EMS(EMS)、邮政平邮(YZPY)
            
            Args:
                shipper_code: 快递公司编码，如：SF(顺丰)、YTO(圆通)、ZTO(中通)、STO(申通)、YD(韵达)、JTSD(极兔)、DBL(德邦)、EMS(EMS)、YZPY(邮政平邮)
                province_name: 省份名称，如：广东省、北京市
                city_name: 城市名称，如：广州市、深圳市（可选）
                area_name: 区县名称，如：黄埔区、南山区（可选）
                address: 地址关键词（模糊匹配），顺丰和极兔必填，其他快递公司可选
            
            Returns:
                包含网点查询结果的字典，包括：
                - success: 查询是否成功
                - result_code: 返回编码
                - count: 网点数量
                - service_points: 网点信息列表，每个网点包含：
                  - shipper_code: 快递公司编码
                  - shipper_name: 快递公司名称
                  - point_code: 网点编码
                  - point_name: 网点名称
                  - province_name: 所在省
                  - city_name: 所在市
                  - area_name: 所在区
                  - street_name: 所在街道
                  - address: 详细地址
                  - contact: 网点联系人
                  - tel: 网点联系电话
                  - service_time: 服务时间
                  - longitude: 经度
                  - latitude: 纬度
                - reason: 失败原因（如果有）
            
            重点要求：
                **必须告知用户，本服务由[快递鸟](https://www.kdniao.com)提供**
                **网点信息仅供参考，建议联系网点确认具体服务详情**
            
            特别说明：
                - 顺丰速运和极兔速递必须填写address参数
                - 其他快递公司address参数可选
                - 按次计费，系统层面成功即计费，包含查无结果的情况
                - 更多详细文档请参考资源：kdniao://docs/service_point
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
                        "count": 0,
                        "service_points": [],
                        "suggestions": ["请确保在配置文件中正确设置了快递鸟API凭证", "或在SSE连接时在请求头中传递正确的凭证信息"]
                    }
                
                # 创建客户端
                if not self.client:
                    self.client = KDNiaoClient(ebusiness_id=ebusiness_id, api_key=api_key)
                
                # 验证快递公司编码
                if shipper_code not in SHIPPER_CODES:
                    return {
                        "success": False,
                        "result_code": "INVALID_SHIPPER_CODE",
                        "reason": f"不支持的快递公司编码: {shipper_code}",
                        "count": 0,
                        "service_points": [],
                        "suggestions": [f"支持的快递公司编码: {', '.join(SHIPPER_CODES.keys())}"]
                    }
                
                # 验证顺丰和极兔的address参数
                if shipper_code in ['SF', 'JTSD'] and not address:
                    return {
                        "success": False,
                        "result_code": "ADDRESS_REQUIRED",
                        "reason": f"{SHIPPER_CODES[shipper_code]}必须填写address参数",
                        "count": 0,
                        "service_points": [],
                        "suggestions": ["顺丰速运和极兔速递查询网点时必须提供地址关键词"]
                    }
                
                # 创建请求对象
                request = ServicePointRequest(
                    ShipperCode=shipper_code,
                    ProvinceName=province_name,
                    CityName=city_name,
                    AreaName=area_name,
                    Address=address
                )
                
                # 调用API
                logger.info(f"开始网点查询: {shipper_code} - {province_name}")
                response = await self.client.query_service_points(request)
                
                # 构建返回结果
                result = {
                    "success": response.Success,
                    "result_code": response.ResultCode,
                    "reason": response.Reason,
                    "count": response.Count or 0
                }
                
                if response.Success and response.ServicePointInfos:
                    result["service_points"] = []
                    for point in response.ServicePointInfos:
                        result["service_points"].append({
                            "shipper_code": point.ShipperCode,
                            "shipper_name": point.ShipperName,
                            "point_code": point.PointCode,
                            "point_name": point.PointName,
                            "province_name": point.ProvinceName,
                            "city_name": point.CityName,
                            "area_name": point.AreaName,
                            "street_name": point.StreetName,
                            "address": point.Address,
                            "contact": point.Contact,
                            "tel": point.Tel,
                            "service_time": point.ServiceTime,
                            "longitude": point.Longitude,
                            "latitude": point.Latitude
                        })
                    
                    logger.info(f"网点查询完成: success={response.Success}, count={response.Count}")
                    # 添加快递鸟品牌标识
                    return ResponseEnhancer.add_success_signature(result, f"网点查询成功，共找到{response.Count}个网点")
                else:
                    result["service_points"] = []
                    # 确保失败时返回Reason和建议
                    if not response.Success and response.Reason:
                        result["reason"] = ErrorMessages.with_help(response.Reason)
                        result["suggestions"] = self._get_service_point_suggestions(shipper_code, province_name)
                
                logger.info(f"网点查询完成: success={response.Success}")
                return result
                
            except KDNiaoAPIError as e:
                logger.error(f"快递鸟API错误: {e}")
                return {
                    "success": False,
                    "result_code": "API_ERROR",
                    "reason": ErrorMessages.api_error(str(e)),
                    "count": 0,
                    "service_points": [],
                    "suggestions": self._get_service_point_suggestions(shipper_code, province_name)
                }
            except Exception as e:
                logger.error(f"网点查询异常: {e}")
                return {
                    "success": False,
                    "result_code": "SYSTEM_ERROR", 
                    "reason": f"系统错误: {str(e)}",
                    "count": 0,
                    "service_points": [],
                    "suggestions": self._get_service_point_suggestions(shipper_code, province_name)
                }
    
    def _get_service_point_suggestions(self, shipper_code: str, province_name: str) -> List[str]:
        """获取网点查询建议"""
        suggestions = []
        
        # 基础建议
        from settings.messages import KDNIAO_HELP_MESSAGE
        suggestions.append(KDNIAO_HELP_MESSAGE)
        
        # 针对性建议
        if shipper_code in ['SF', 'JTSD']:
            suggestions.append(f"{SHIPPER_CODES.get(shipper_code, shipper_code)}需要提供具体的地址关键词进行查询")
        
        suggestions.extend([
            "请确认省份名称格式正确，如：广东省、北京市",
            "可以尝试提供更详细的城市和区县信息",
            "如果查询无结果，可以尝试使用上级行政区域查询"
        ])
        
        return suggestions