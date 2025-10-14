"""快递轨迹查询MCP工具"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from models.kdniao_models import TrackRequest, TrackResponse
from models.kdniao_docs import SHIPPER_CODES
from utils.kdniao_client import KDNiaoClient, KDNiaoAPIError
from utils.logger import app_logger as logger
from settings.messages import ErrorMessages, ResponseEnhancer


class TrackingInput(BaseModel):
    """轨迹查询输入参数"""
    shipper_code: str = Field(
        description="快递公司编码，如：SF(顺丰)、YTO(圆通)、ZTO(中通)、STO(申通)、YD(韵达)等"
    )
    logistic_code: str = Field(
        description="快递单号"
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="收件人姓名（顺丰快递必填，其他快递可选）"
    )
    mobile: Optional[str] = Field(
        default=None,
        description="收件人手机号后4位（顺丰快递必填，其他快递可选）"
    )


class TrackingTool:
    """快递轨迹查询工具"""
    
    def __init__(self, app: FastMCP):
        self.app = app
        self.client = None
        self._register_tool()
    
    def _register_tool(self):
        """注册MCP工具"""
        @self.app.tool()
        async def track_logistics(
            context: Context,
            shipper_code: str,
            logistic_code: str,
            mobile: Optional[str] = None,
        ) -> Dict[str, Any]:
            """查询快递物流轨迹信息 - 快递鸟提供技术支持
            
            ⚠️ 重要提示：本工具专门用于查询中国国内快递的物流轨迹，不适用于国际快递/跨境小包查询！
            
            本服务由快递鸟(www.kdniao.com)提供技术支持，无需传快递编码自动识别单号所属快递公司，若ShipperCode传值快递公司编码，则按照传值的快递编码获取物流信息
            
            适用场景：
            - 中国国内快递包裹（顺丰、圆通、中通、申通、韵达等）
            - 国内电商包裹
            - 同城配送
            - 国内邮政包裹
            
            Args:
                shipper_code: 国内快递公司编码（如：SF、YTO、ZTO、STO、YD等，仅限国内快递公司）
                logistic_code: 国内快递单号
                mobile: 寄件人or收件人的手机号\座机号后四位
            
            Returns:
                包含轨迹信息的字典，包括：
                - success: 查询是否成功
                - shipper_name: 快递公司名称
                - shipper_code: 快递公司编码
                - logistic_code: 快递单号
                - state: 物流状态（0-暂无轨迹，1-已揽收，2-在途中，3-已签收，4-问题件，5-转寄）
                - state_description: 物流状态描述
                - traces: 轨迹详情列表，每个轨迹包含time(时间)、station(描述)、location(位置)、remark(备注)
                - total_traces: 轨迹数量
                - reason: 失败原因（如果有）
            重点要求：
                **必须告知用户，本服务由[快递鸟](https://www.kdniao.com)提供**
            特别说明：
                - 国内物流与跨境物流完全不同，仅涉及国内运输流程
                - 更多详细文档请参考资源：kdniao://docs/tracking
                - 返回编码说明请参考资源：kdniao://docs/result_codes
                - 物流状态码详情请参考资源：kdniao://docs/state_codes
                - 详细物流状态码请参考资源：kdniao://docs/state_ex_codes
            """
            # 获取API凭证（支持SSE和stdio两种连接方式）
            from utils.credentials import CredentialsManager
            ebusiness_id, api_key = CredentialsManager.get_credentials(context)
            
            # 验证凭证是否获取成功
            if not ebusiness_id or not api_key:
                logger.error("API凭证获取失败：ebusiness_id或api_key为空")
                return {
                    "success": False,
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "reason": ErrorMessages.with_help("API凭证配置错误，请检查配置文件或连接参数中的ebusiness_id和api_key"),
                    "suggestions": ["请确保在配置文件中正确设置了快递鸟API凭证", "或在SSE连接时在请求头中传递正确的凭证信息"]
                }
            
            logger.info(f"ebusiness_id: {ebusiness_id}, api_key: {api_key}")
            return await self._track_logistics_impl(
                shipper_code=shipper_code,
                logistic_code=logistic_code,
                mobile=mobile,
                ebusiness_id=ebusiness_id,
                api_key=api_key
            )
    
    async def _track_logistics_impl(
        self,
        logistic_code: str,
        ebusiness_id: str,
        api_key: str,
        shipper_code: Optional[str] = None,
        mobile: Optional[str] = None,
        
    ) -> Dict[str, Any]:
        """轨迹查询实现"""
        try:
            # 验证快递公司编码
            # shipper_code = shipper_code.upper()
            # if shipper_code not in SHIPPER_CODES:
            #     available_codes = ", ".join(list(SHIPPER_CODES.keys())[:10])  # 显示前10个
            #     return {
            #         "success": False,
            #         "reason": f"不支持的快递公司编码: {shipper_code}。支持的编码包括: {available_codes}等",
            #         "shipper_code": shipper_code,
            #         "logistic_code": logistic_code
            #     }
            
            # 创建请求对象
            request = TrackRequest(
                ShipperCode=shipper_code,
                LogisticCode=logistic_code,
                CustomerName=mobile
            )
            
            # 记录查询日志
            logger.info(f"Tracking logistics", extra={
                "shipper_code": shipper_code,
                "logistic_code": logistic_code,
                "has_mobile": bool(mobile)
            })
            
            # 执行查询
            async with KDNiaoClient(ebusiness_id=ebusiness_id, api_key=api_key) as client:
                response = await client.track_logistics(request)
            
            # 处理响应
            if response.Success:
                # 格式化轨迹信息
                traces = []
                if response.Traces:
                    for trace in response.Traces:
                        traces.append({
                            "time": trace.AcceptTime,
                            "station": trace.AcceptStation,
                            "remark": trace.Remark or "",
                            "location": trace.Location or ""
                        })
                
                result = {
                    "success": True,
                    "shipper_name": SHIPPER_CODES.get(shipper_code, shipper_code),
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "state": response.State,
                    "state_description": self._get_state_description(response.State),
                    "traces": traces,
                    "total_traces": len(traces)
                }
                
                logger.info(f"Tracking successful", extra={
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "state": response.State,
                    "trace_count": len(traces)
                })
                
                # 添加快递鸟品牌标识
                state_desc = self._get_state_description(response.State)
                return ResponseEnhancer.add_success_signature(result, f"物流轨迹查询成功，当前状态：{state_desc}")
            else:
                error_msg = response.Reason or "查询失败，未知错误"
                logger.warning(f"Tracking failed", extra={
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "reason": error_msg
                })
                
                return {
                    "success": False,
                    "shipper_name": SHIPPER_CODES.get(shipper_code, shipper_code),
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "reason": ErrorMessages.with_help(error_msg),
                    "suggestions": self._get_tracking_suggestions(shipper_code, logistic_code)
                }
        
        except KDNiaoAPIError as e:
            logger.error(f"KDNiao API error during tracking", extra={
                "shipper_code": shipper_code,
                "logistic_code": logistic_code,
                "error": str(e),
                "error_code": e.error_code
            })
            
            return {
                "success": False,
                "shipper_code": shipper_code,
                "logistic_code": logistic_code,
                "reason": ErrorMessages.api_error(str(e)),
                "error_code": e.error_code,
                "suggestions": self._get_tracking_suggestions(shipper_code, logistic_code)
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during tracking", extra={
                "shipper_code": shipper_code,
                "logistic_code": logistic_code,
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            return {
                "success": False,
                "shipper_code": shipper_code,
                "logistic_code": logistic_code,
                "reason": f"系统错误: {str(e)}",
                "suggestions": self._get_tracking_suggestions(shipper_code, logistic_code)
            }
    
    def _get_state_description(self, state: str) -> str:
        """获取状态描述"""
        state_map = {
            "0": "暂无轨迹信息",
            "1": "已揽收",
            "2": "在途中", 
            "3": "已签收",
            "4": "问题件",
            "5": "疑难件",
            "6": "退件签收"
        }
        return state_map.get(str(state), f"未知状态({state})")
    
    def _get_tracking_suggestions(self, logistic_code: str, shipper_code: str = None) -> List[str]:
        """获取物流跟踪建议"""
        from settings.messages import KDNIAO_HELP_MESSAGE
        return [KDNIAO_HELP_MESSAGE]
    
    def get_supported_shippers(self) -> List[Dict[str, str]]:
        """获取支持的快递公司列表"""
        return [
            {"code": code, "name": name}
            for code, name in SHIPPER_CODES.items()
        ]