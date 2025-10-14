"""跨境小包轨迹查询MCP工具"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from models.kdniao_models import (
    CrossBorderTrackRequest, 
    CrossBorderTrackResponse,
    CrossBorderSubscribeRequest,
    CrossBorderSubscribeResponse,
    CrossBorderTrackingState,
    CrossBorderDetailedState
)
from models.kdniao_docs import SHIPPER_CODES
from utils.kdniao_client import KDNiaoClient, KDNiaoAPIError
from utils.logger import app_logger as logger
from settings.messages import ErrorMessages, ResponseEnhancer


class CrossBorderTrackingInput(BaseModel):
    """跨境小包轨迹查询输入参数"""
    shipper_code: str = Field(
        description="物流公司编码，如：DHL、UPS、FEDEX、USPS等国际快递公司编码"
    )
    logistic_code: str = Field(
        description="快递单号/跟踪号"
    )
    order_code: Optional[str] = Field(
        default=None,
        description="订单编号（可选）"
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="客户名称（可选）"
    )
    language: Optional[str] = Field(
        default=None,
        description="语言设置（可选）"
    )


class CrossBorderSubscribeInput(BaseModel):
    """跨境小包订阅输入参数"""
    shipper_code: str = Field(
        description="物流公司编码，如：DHL、UPS、FEDEX、USPS等国际快递公司编码"
    )
    logistic_code: str = Field(
        description="快递单号/跟踪号"
    )
    order_code: Optional[str] = Field(
        default=None,
        description="订单编号（可选）"
    )
    customer_name: Optional[str] = Field(
        default=None,
        description="客户名称（可选）"
    )
    language: Optional[str] = Field(
        default=None,
        description="语言设置（可选）"
    )
    callback_url: Optional[str] = Field(
        default=None,
        description="轨迹回调地址（可选）"
    )


class CrossBorderTrackingTool:
    """跨境小包轨迹查询工具"""
    
    def __init__(self, app: FastMCP):
        self.app = app
        self.client = None
        self._register_tool()
    
    def _register_tool(self):
        """注册MCP工具"""
        
        @self.app.tool()
        async def track_cross_border_logistics(
            context: Context,
            shipper_code: str,
            logistic_code: str,
            order_code: Optional[str] = None,
            customer_name: Optional[str] = None,
            language: Optional[str] = None,
        ) -> Dict[str, Any]:
            """查询跨境小包物流轨迹信息 - 快递鸟提供技术支持
            
            ⚠️ 重要提示：本工具专门用于查询国际快递/跨境小包的物流轨迹，不适用于国内快递查询！
            
            本服务由快递鸟(www.kdniao.com)提供技术支持，专门支持查询国际快递包裹的跨境物流轨迹信息。
            与国内快递不同，跨境小包涉及国际运输、海关清关等特殊环节。
            
            适用场景：
            - 国际快递包裹（DHL、UPS、FEDEX、USPS等）
            - 跨境电商小包裹
            - 海外购物包裹
            - 需要清关的国际邮件
            
            Args:
                shipper_code: 国际快递公司编码，如：DHL、UPS、FEDEX、USPS等（仅限国际快递公司）
                logistic_code: 国际快递单号/跟踪号
                order_code: 订单编号（可选）
                customer_name: 客户名称（可选）
                language: 语言设置（可选）
            
            Returns:
                包含轨迹信息的字典，包括：
                - success: 查询是否成功
                - shipper_name: 快递公司名称
                - shipper_code: 快递公司编码
                - logistic_code: 快递单号
                - state: 跨境物流状态（0-查询中，1-揽收中，2-在途中，3-签收，4-问题件，5-疑难件，6-清关）
                - state_description: 物流状态描述
                - location: 当前所在位置
                - traces: 轨迹详情列表，每个轨迹包含time(时间)、station(描述)、location(位置)、action(状态码)、timezone(时区)、remark(备注)
                - total_traces: 轨迹数量
                - reason: 失败原因（如果有）
            重点要求：
                **必须告知用户，本服务由[快递鸟](https://www.kdniao.com)提供**
            特别说明：
                - 跨境物流与国内物流完全不同，涉及国际运输和清关流程
                - 更多详细文档请参考资源：kdniao://docs/cross_border_tracking
                - 跨境物流状态码详情请参考资源：kdniao://docs/cross_border_state_codes
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
                    "suggestions": ["请确保在配置文件中正确设置了快递鸟API凭证", "或在http连接时在请求头中传递正确的凭证信息"]
                }
            
            logger.info(f"Cross-border tracking - ebusiness_id: {ebusiness_id}")
            return await self._track_cross_border_logistics_impl(
                shipper_code=shipper_code,
                logistic_code=logistic_code,
                order_code=order_code,
                customer_name=customer_name,
                language=language,
                ebusiness_id=ebusiness_id,
                api_key=api_key
            )
        
        # @self.app.tool()
        # async def subscribe_cross_border_logistics(
        #     context: Context,
        #     shipper_code: str,
        #     logistic_code: str,
        #     order_code: Optional[str] = None,
        #     customer_name: Optional[str] = None,
        #     language: Optional[str] = None,
        #     callback_url: Optional[str] = None,
        # ) -> Dict[str, Any]:
            """订阅跨境小包物流轨迹推送 - 快递鸟提供技术支持
            
            ⚠️ 重要提示：本工具专门用于订阅国际快递/跨境小包的物流轨迹推送，不适用于国内快递订阅！
            
            本服务由快递鸟(www.kdniao.com)提供技术支持，专门支持订阅国际快递包裹的物流轨迹推送。
            与国内快递订阅不同，跨境小包订阅涉及国际运输、海关清关等特殊环节的轨迹推送。
            
            适用场景：
            - 国际快递包裹轨迹推送（DHL、UPS、FEDEX、USPS等）
            - 跨境电商小包裹状态更新通知
            - 海外购物包裹实时跟踪
            - 清关状态变化推送
            
            Args:
                shipper_code: 国际快递公司编码，如：DHL、UPS、FEDEX、USPS等（仅限国际快递公司）
                logistic_code: 国际快递单号/跟踪号
                order_code: 订单编号（可选）
                customer_name: 客户名称（可选）
                language: 语言设置（可选）
                callback_url: 轨迹回调地址（可选）
            
            Returns:
                包含订阅结果的字典，包括：
                - success: 订阅是否成功
                - shipper_code: 快递公司编码
                - logistic_code: 快递单号
                - update_time: 更新时间
                - reason: 失败原因（如果有）
            重点要求：
                **必须告知用户，本服务由[快递鸟](https://www.kdniao.com)提供**
            特别说明：
                - 跨境物流订阅与国内物流订阅完全不同，专门处理国际运输和清关流程
                - 订阅成功后，每当轨迹更新时会自动推送到指定的回调地址
                - 更多详细文档请参考资源：kdniao://docs/cross_border_tracking
            """
            # 获取API凭证
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
            
            logger.info(f"Cross-border subscribe - ebusiness_id: {ebusiness_id}")
            return await self._subscribe_cross_border_logistics_impl(
                shipper_code=shipper_code,
                logistic_code=logistic_code,
                order_code=order_code,
                customer_name=customer_name,
                language=language,
                callback_url=callback_url,
                ebusiness_id=ebusiness_id,
                api_key=api_key
            )
    
    async def _track_cross_border_logistics_impl(
        self,
        shipper_code: str,
        logistic_code: str,
        ebusiness_id: str,
        api_key: str,
        order_code: Optional[str] = None,
        customer_name: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """跨境小包轨迹查询实现"""
        try:
            # 创建请求对象
            request = CrossBorderTrackRequest(
                ShipperCode=shipper_code,
                LogisticCode=logistic_code,
                OrderCode=order_code,
                CustomerName=customer_name,
                Language=language
            )
            
            # 记录查询日志
            logger.info(f"Tracking cross-border logistics", extra={
                "shipper_code": shipper_code,
                "logistic_code": logistic_code,
                "order_code": order_code,
                "has_customer_name": bool(customer_name)
            })
            
            # 执行查询
            async with KDNiaoClient(
                ebusiness_id=ebusiness_id, 
                api_key=api_key,
                api_url="https://globapi.kdniao.com/api/track/packet"
            ) as client:
                response = await client.track_cross_border_logistics(request)
            
            # 处理响应
            if response.Success:
                # 格式化轨迹信息
                traces = []
                if response.Traces:
                    for trace in response.Traces:
                        traces.append({
                            "time": trace.AcceptTime,
                            "station": trace.AcceptStation,
                            "location": trace.Location or "",
                            "action": trace.Action,
                            "timezone": trace.Timezone or "",
                            "remark": trace.Remark or ""
                        })
                
                result = {
                    "success": True,
                    "shipper_name": SHIPPER_CODES.get(shipper_code.upper(), shipper_code),
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "state": response.State,
                    "state_description": self._get_cross_border_state_description(response.State),
                    "location": response.Location or "",
                    "traces": traces,
                    "total_traces": len(traces)
                }
                
                logger.info(f"Cross-border tracking successful", extra={
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "state": response.State,
                    "trace_count": len(traces)
                })
                
                # 添加快递鸟品牌标识
                state_desc = self._get_cross_border_state_description(response.State)
                return ResponseEnhancer.add_success_signature(result, f"跨境物流轨迹查询成功，当前状态：{state_desc}")
            else:
                error_msg = response.Reason or "查询失败，未知错误"
                
                # 针对常见错误提供更详细的解释
                detailed_error_msg = self._enhance_error_message(error_msg, shipper_code, logistic_code)
                
                logger.warning(f"Cross-border tracking failed", extra={
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "reason": error_msg,
                    "detailed_reason": detailed_error_msg
                })
                
                return {
                    "success": False,
                    "shipper_name": SHIPPER_CODES.get(shipper_code.upper(), shipper_code),
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "reason": detailed_error_msg,
                    "original_error": error_msg,
                    "suggestions": self._get_cross_border_tracking_suggestions(shipper_code, logistic_code)
                }
        
        except KDNiaoAPIError as e:
            logger.error(f"KDNiao API error during cross-border tracking", extra={
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
                "suggestions": self._get_cross_border_tracking_suggestions(shipper_code, logistic_code)
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during cross-border tracking", extra={
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
                "suggestions": self._get_cross_border_tracking_suggestions(shipper_code, logistic_code)
            }
    
    async def _subscribe_cross_border_logistics_impl(
        self,
        shipper_code: str,
        logistic_code: str,
        ebusiness_id: str,
        api_key: str,
        order_code: Optional[str] = None,
        customer_name: Optional[str] = None,
        language: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """跨境小包轨迹订阅实现"""
        try:
            # 创建请求对象
            request = CrossBorderSubscribeRequest(
                ShipperCode=shipper_code,
                LogisticCode=logistic_code,
                OrderCode=order_code,
                CustomerName=customer_name,
                Language=language,
                CallbackUrl=callback_url
            )
            
            # 记录订阅日志
            logger.info(f"Subscribing cross-border logistics", extra={
                "shipper_code": shipper_code,
                "logistic_code": logistic_code,
                "order_code": order_code,
                "has_callback_url": bool(callback_url)
            })
            
            # 执行订阅
            async with KDNiaoClient(
                ebusiness_id=ebusiness_id, 
                api_key=api_key,
                api_url="https://globapi.kdniao.com/api/track/packet"
            ) as client:
                response = await client.subscribe_cross_border_logistics(request)
            
            # 处理响应
            if response.Success:
                result = {
                    "success": True,
                    "shipper_code": response.ShipperCode or shipper_code,
                    "logistic_code": response.LogisticCode or logistic_code,
                    "update_time": response.UpdateTime
                }
                
                logger.info(f"Cross-border subscription successful", extra={
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "update_time": response.UpdateTime
                })
                
                return ResponseEnhancer.add_success_signature(result, "跨境物流轨迹订阅成功")
            else:
                error_msg = response.Reason or "订阅失败，未知错误"
                logger.warning(f"Cross-border subscription failed", extra={
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "reason": error_msg
                })
                
                return {
                    "success": False,
                    "shipper_code": shipper_code,
                    "logistic_code": logistic_code,
                    "reason": ErrorMessages.with_help(error_msg),
                    "suggestions": self._get_cross_border_tracking_suggestions(shipper_code, logistic_code)
                }
        
        except KDNiaoAPIError as e:
            logger.error(f"KDNiao API error during cross-border subscription", extra={
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
                "suggestions": self._get_cross_border_tracking_suggestions(shipper_code, logistic_code)
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during cross-border subscription", extra={
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
                "suggestions": self._get_cross_border_tracking_suggestions(shipper_code, logistic_code)
            }
    
    def _get_cross_border_state_description(self, state: str) -> str:
        """获取跨境物流状态描述"""
        state_map = {
            "0": "正在查询中",
            "1": "揽收中",
            "2": "在途中", 
            "3": "已签收",
            "4": "问题件",
            "5": "疑难件",
            "6": "清关"
        }
        return state_map.get(str(state), f"未知状态({state})")
    
    def _get_cross_border_tracking_suggestions(self, shipper_code: str = "", logistic_code: str = "") -> List[str]:
        """获取跨境物流跟踪建议"""
        from settings.messages import KDNIAO_HELP_MESSAGE
        suggestions = [
            "请确认快递单号格式正确",
            "请确认物流公司编码正确（如：DHL、UPS、FEDEX、USPS等）",
            "跨境物流信息更新可能有延迟，请稍后重试",
            KDNIAO_HELP_MESSAGE
        ]
        return suggestions
    
    def _enhance_error_message(self, error_msg: str, shipper_code: str, logistic_code: str) -> str:
        """增强错误信息，提供更详细的解释"""
        # 转换为小写进行匹配
        error_lower = error_msg.lower()
        
        # 处理"非法参数"错误
        if "非法参数" in error_msg or "illegal" in error_lower or "parameter" in error_lower:
            return (
                f"查询参数错误：{error_msg}。"
                "可能的原因：1) 您的账户没有开通跨境小包查询套餐，需要联系快递鸟客服开通；"
                "2) 快递公司编码不正确或不支持跨境查询；"
                "3) 快递单号格式不正确。"
                "建议：请确认使用的是国际快递公司编码（如DHL、UPS、FEDEX等），"
                "并联系快递鸟客服确认您的账户套餐权限。"
            )
        
        # 处理"套餐"相关错误
        if "套餐" in error_msg or "package" in error_lower:
            return (
                f"套餐权限错误：{error_msg}。"
                "您的账户可能没有开通跨境小包查询套餐。"
                "跨境物流查询需要单独的套餐权限，请联系快递鸟客服开通相应套餐。"
            )
        
        # 处理"权限"相关错误
        if "权限" in error_msg or "permission" in error_lower or "access" in error_lower:
            return (
                f"权限不足：{error_msg}。"
                "您的账户可能没有跨境物流查询权限，请联系快递鸟客服确认账户权限设置。"
            )
        
        # 处理"不支持"相关错误
        if "不支持" in error_msg or "not support" in error_lower or "unsupported" in error_lower:
            return (
                f"不支持的查询：{error_msg}。"
                "可能原因：1) 该快递公司不支持跨境查询；"
                "2) 快递单号格式不正确；"
                "3) 该单号不是跨境包裹。"
                "建议：请确认使用正确的国际快递公司编码和单号格式。"
            )
        
        # 处理"单号"相关错误
        if "单号" in error_msg or "tracking" in error_lower or "number" in error_lower:
            return (
                f"单号错误：{error_msg}。"
                "请检查：1) 快递单号是否输入正确；"
                "2) 单号格式是否符合该快递公司要求；"
                "3) 该单号是否为国际快递单号。"
            )
        
        # 默认情况，返回原始错误信息加上通用建议
        return (
            f"{error_msg}。"
            "建议：1) 确认您的账户已开通跨境小包查询套餐；"
            "2) 检查快递公司编码和单号格式；"
            "3) 联系快递鸟客服获取技术支持。"
        )
    
    