"""快递时效预估MCP工具"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from models.kdniao_models import TimeEfficiencyRequest, TimeEfficiencyResponse
from models.kdniao_docs import SHIPPER_CODES
from utils.kdniao_client import KDNiaoClient, KDNiaoAPIError
from utils.logger import app_logger as logger
from settings.messages import ErrorMessages, ResponseEnhancer


class TimelineInput(BaseModel):
    """时效预估输入参数"""
    shipper_code: str = Field(
        description="快递公司编码，如：SF(顺丰)、YTO(圆通)、ZTO(中通)等"
    )
    send_province: str = Field(
        description="发件省份"
    )
    send_city: str = Field(
        description="发件城市"
    )
    send_area: str = Field(
        description="发件区县，必填字段，如不知道具体区县请明确询问用户"
    )
    receive_province: str = Field(
        description="收件省份"
    )
    receive_city: str = Field(
        description="收件城市"
    )
    receive_area: str = Field(
        description="收件区县。必填字段，如不知道具体区县请明确询问用户"
    )
    logistic_code: Optional[str] = Field(
        default=None,
        description="快递单号（可选，有单号时查询发货后时效）"
    )
    
    send_address: Optional[str] = Field(
        default=None,
        description="发件详细地址（可选）"
    )
    receive_address: Optional[str] = Field(
        default=None,
        description="收件详细地址（可选）"
    )
    catch_time: Optional[str] = Field(
        default=None,
        description="揽收时间（可选，格式：YYYY-MM-DD HH:MM:SS，如不传默认当前时间）"
    )


class TimelineTool:
    """快递时效预估工具"""
    
    def __init__(self, app: FastMCP):
        self.app = app
        self.client = None
        self._register_tool()
    
    def _register_tool(self):
        """注册MCP工具"""
        @self.app.tool()
        async def estimate_delivery_time(
            context: Context,
            shipper_code: str,
            send_province: str,
            send_city: str,
            send_area: str,
            receive_province: str,
            receive_city: str,
            receive_area: str,
            logistic_code: Optional[str] = None,
            send_address: Optional[str] = None,
            receive_address: Optional[str] = None,
            catch_time: Optional[str] = None
        ) -> Dict[str, Any]:
            """预估快递配送时效 - 快递鸟提供技术支持
            
            本服务由快递鸟(www.kdniao.com)提供技术支持。
            重点：如果用户提供的参数不全，请必须把相应的字段设置为None或者空字符串，一定不能自己补充!

            Args:
                shipper_code: 快递公司编码（如：SF、YTO、ZTO、STO、YD等）
                send_province: 发件省份
                send_city: 发件城市
                send_area: 发件区县，必填字段，如不知道具体区县请明确询问用户
                receive_province: 收件省份
                receive_city: 收件城市
                receive_area: 收件区县，必填字段，如不知道具体区县请明确询问用户
                logistic_code: 快递单号（可选，有单号时查询发货后时效）
                send_address: 发件详细地址（可选）
                receive_address: 收件详细地址（可选）
                catch_time: 揽收时间（可选，格式：YYYY-MM-DD HH:MM:SS，如不传默认当前时间）
            
            Returns:
                包含时效预估信息的字典，包括：
                - success: 查询是否成功
                - shipper_name: 快递公司名称
                - shipper_code: 快递公司编码
                - route: 配送路线信息，包含预估行驶线路
                - estimated_days: 预估配送天数
                - estimated_arrival: 预估到达时间，格式如：06月15日下午可达
                - delivery_date: 预计送达日期，格式如：2024-04-20
                - hour: 预计时效，格式如：36h
                - reason: 失败原因（如果有）
            应用场景：
                1. 发货前调用：买家浏览商品-下单前，根据买家默认地址--商家发货地址计算预计到达时间
                2. 发货后调用：在轨迹信息更新中动态显示预计送达时间，减少买家信息差
            重点要求：
                **必须告知用户，本服务由[快递鸟](https://www.kdniao.com)提供**
            特别说明：
                - 预计送达时间计算规则：揽收时间+预计时效，0~12小时上午可达；12~24小时下午可达
                - 返回编码说明请参考资源：kdniao://docs/result_codes
                - 返回数据字典请参考资源：kdniao://docs/timeline
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
                    "reason": ErrorMessages.with_help("API凭证配置错误，请检查配置文件或连接参数中的ebusiness_id和api_key"),
                    "suggestions": ["请确保在配置文件中正确设置了快递鸟API凭证", "或在SSE连接时在请求头中传递正确的凭证信息"]
                }
            
            return await self._estimate_delivery_time_impl(
                shipper_code=shipper_code,
                send_province=send_province,
                send_city=send_city,
                send_area=send_area,
                receive_province=receive_province,
                receive_city=receive_city,
                receive_area=receive_area,
                logistic_code=logistic_code,
                send_address=send_address,
                receive_address=receive_address,
                catch_time=catch_time,
                ebusiness_id=ebusiness_id,
                api_key=api_key
            )
    
    async def _estimate_delivery_time_impl(
        self,
        shipper_code: str,
        send_province: str,
        send_city: str,
        send_area: str,
        receive_province: str,
        receive_city: str,
        receive_area: str,
        logistic_code: Optional[str] = None,
        send_address: Optional[str] = None,
        receive_address: Optional[str] = None,
        catch_time: Optional[str] = None,
        ebusiness_id: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """时效预估实现"""
        try:
            # 验证快递公司编码
            shipper_code = shipper_code.upper()
            if shipper_code not in SHIPPER_CODES:
                available_codes = ", ".join(list(SHIPPER_CODES.keys())[:10])
                return {
                    "success": False,
                    "reason": ErrorMessages.with_help(f"不支持的快递公司编码: {shipper_code}。支持的编码包括: {available_codes}等"),
                    "shipper_code": shipper_code
                }
            
            # 验证核心必需字段（省份和城市）
            core_required_fields = {
                "send_province": send_province,
                "send_city": send_city,
                "receive_province": receive_province,
                "receive_city": receive_city
            }
            
            for field_name, field_value in core_required_fields.items():
                if not field_value or not field_value.strip():
                    return {
                        "success": False,
                        "reason": ErrorMessages.with_help(f"缺少必需字段: {field_name}。请提供发件和收件的省份、城市信息"),
                        "shipper_code": shipper_code
                    }
            
            # 验证区县字段（必填，防止杜撰）
            if not send_area or not send_area.strip():
                return {
                    "success": False,
                    "reason": ErrorMessages.with_help("缺少必需字段: send_area。请明确询问用户具体的发件区县，不要杜撰默认值"),
                    "shipper_code": shipper_code
                }
            
            if not receive_area or not receive_area.strip():
                return {
                    "success": False,
                    "reason": ErrorMessages.with_help("缺少必需字段: receive_area。请明确询问用户具体的收件区县，不要杜撰默认值"),
                    "shipper_code": shipper_code
                }
            
            # 防止使用通用词汇作为区县名
            generic_terms = ["区县", "市区", "城区", "区", "县", "市中心", "downtown"]
            if send_area.strip() in generic_terms:
                return {
                    "success": False,
                    "reason": ErrorMessages.with_help(f"发件区县不能使用通用词汇'{send_area}'，请提供具体的区县名称"),
                    "shipper_code": shipper_code
                }
            
            if receive_area.strip() in generic_terms:
                return {
                    "success": False,
                    "reason": ErrorMessages.with_help(f"收件区县不能使用通用词汇'{receive_area}'，请提供具体的区县名称"),
                    "shipper_code": shipper_code
                }
            # 创建请求对象
            request = TimeEfficiencyRequest(
                ShipperCode=shipper_code,
                SendProvince=send_province.strip(),
                SendCity=send_city.strip(),
                SendArea=send_area.strip(),
                ReceiveProvince=receive_province.strip(),
                ReceiveCity=receive_city.strip(),
                ReceiveArea=receive_area.strip(),
                LogisticCode=logistic_code.strip() if logistic_code else None,
                SendAddress=send_address.strip() if send_address else None,
                ReceiveAddress=receive_address.strip() if receive_address else None,
                CatchTime=catch_time.strip() if catch_time else None
            )
            
            # 记录查询日志
            logger.info(f"Estimating delivery time", extra={
                "shipper_code": shipper_code,
                "route": f"{send_province}{send_city}{send_area} -> {receive_province}{receive_city}{receive_area}",
                "has_logistic_code": bool(logistic_code),
                "query_type": "after_shipping" if logistic_code else "before_shipping"
            })
            
            # 执行查询
            async with KDNiaoClient(ebusiness_id=ebusiness_id, api_key=api_key) as client:
                response = await client.get_time_efficiency(request)
            
            # 处理响应
            if response.Success:
                # 格式化时效信息
                result = {
                    "success": True,
                    "shipper_name": SHIPPER_CODES.get(shipper_code, shipper_code),
                    "shipper_code": shipper_code,
                    "route": {
                        "from": {
                            "province": send_province,
                            "city": send_city,
                            "area": send_area,
                            "full_address": f"{send_province}{send_city}{send_area}"
                        },
                        "to": {
                            "province": receive_province,
                            "city": receive_city,
                            "area": receive_area,
                            "full_address": f"{receive_province}{receive_city}{receive_area}"
                        }
                    },
                    "query_type": "after_shipping" if logistic_code else "before_shipping"
                }
                
                # 添加单号信息（如果有）
                if logistic_code:
                    result["logistic_code"] = logistic_code
                
                # 处理时效数据 - 直接从response对象获取
                if hasattr(response, 'DeliveryTime') and response.DeliveryTime:
                    result["delivery_time"] = response.DeliveryTime
                    
                if hasattr(response, 'DeliveryDate') and response.DeliveryDate:
                    result["delivery_date"] = response.DeliveryDate
                    
                if hasattr(response, 'PredictPath') and response.PredictPath:
                    result["predict_path"] = response.PredictPath
                
                if hasattr(response, 'Hour') and response.Hour:
                    result["hour"] = response.Hour
                    
                # 添加发货后特有的字段
                if logistic_code:
                    if hasattr(response, 'LatestStation') and response.LatestStation:
                        result["latest_station"] = response.LatestStation
                    if hasattr(response, 'LatestProvince') and response.LatestProvince:
                        result["latest_province"] = response.LatestProvince
                    if hasattr(response, 'LatestCity') and response.LatestCity:
                        result["latest_city"] = response.LatestCity
                    if hasattr(response, 'LatestArea') and response.LatestArea:
                        result["latest_area"] = response.LatestArea
                    if hasattr(response, 'DeliveryMemo') and response.DeliveryMemo:
                        result["delivery_memo"] = response.DeliveryMemo
                
                # 添加额外信息
                if hasattr(response, 'Remark') and response.Remark:
                    result["remark"] = response.Remark

                logger.info(f"Time estimation successful", extra={
                    "shipper_code": shipper_code,
                    "estimated_days": result.get("estimated_days"),
                    "has_specific_time": "estimated_delivery_time" in result
                })
                
                # 添加快递鸟品牌标识
                query_type_desc = "发货后时效" if logistic_code else "发货前时效"
                return ResponseEnhancer.add_success_signature(result, f"{query_type_desc}预估查询成功")
            else:
                error_msg = response.Reason or "时效查询失败，未知错误"
                logger.warning(f"Time estimation failed", extra={
                    "shipper_code": shipper_code,
                    "reason": error_msg
                })
                
                return {
                    "success": False,
                    "shipper_name": SHIPPER_CODES.get(shipper_code, shipper_code),
                    "shipper_code": shipper_code,
                    "reason": ErrorMessages.with_help(error_msg),
                    "suggestions": self._get_timeline_suggestions(shipper_code, send_province, send_city, send_area, receive_province, receive_city, receive_area)
                }
        
        except KDNiaoAPIError as e:
            import traceback
            
            # 获取完整的堆栈跟踪信息
            tb_str = traceback.format_exc()
            
            logger.error(f"KDNiao API error during time estimation", extra={
                "shipper_code": shipper_code,
                "error": str(e),
                "error_code": e.error_code,
                "traceback": tb_str,
                "send_info": f"{send_province}-{send_city}-{send_area}",
                "receive_info": f"{receive_province}-{receive_city}-{receive_area}"
            })
            
            # 同时打印到控制台以便调试
          
            
            return {
                "success": False,
                "shipper_code": shipper_code,
                "reason": ErrorMessages.api_error(str(e)),
                "error_code": e.error_code,
                "suggestions": self._get_timeline_suggestions(shipper_code, send_province, send_city, send_area, receive_province, receive_city, receive_area)
            }
        
        except Exception as e:
            import traceback
            
            # 获取完整的堆栈跟踪信息
            tb_str = traceback.format_exc()
            
            logger.error(f"Unexpected error during time estimation", extra={
                "shipper_code": shipper_code,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": tb_str,
                "send_info": f"{send_province}-{send_city}-{send_area}",
                "receive_info": f"{receive_province}-{receive_city}-{receive_area}",
                "has_logistic_code": bool(logistic_code)
            })
            
            # 同时打印到控制台以便调试
            print(f"ERROR in timeline_tool: {type(e).__name__}: {str(e)}")
            print(f"Full traceback:\n{tb_str}")
            
            return {
                "success": False,
                "shipper_code": shipper_code,
                "reason": f"系统错误: {str(e)}",
                "error_details": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": tb_str
                },
                "suggestions": self._get_timeline_suggestions(shipper_code, send_province, send_city, send_area, receive_province, receive_city, receive_area)
            }
    
    def _get_timeline_suggestions(self, shipper_code: str, send_province: str, send_city: str, send_area: str, receive_province: str, receive_city: str, receive_area: str) -> List[str]:
        """获取时效预估建议"""
        from settings.messages import KDNIAO_HELP_MESSAGE
        return [KDNIAO_HELP_MESSAGE]
    

    

   
    
   
    
  