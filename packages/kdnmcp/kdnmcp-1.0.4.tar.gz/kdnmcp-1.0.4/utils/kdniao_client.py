"""快递鸟API客户端"""

import httpx
import json
from typing import Dict, Any, Optional, Union
from urllib.parse import urlencode

from settings import config
from models.kdniao_models import (
    TrackRequest, TrackResponse,
    RecognizeRequest, RecognizeResponse,
    TimeEfficiencyRequest, TimeEfficiencyResponse,
    AddressParseRequest, AddressParseResponse,
    CrossBorderTrackRequest, CrossBorderTrackResponse,
    CrossBorderSubscribeRequest, CrossBorderSubscribeResponse,
    ServicePointRequest, ServicePointResponse
)
from .signature import prepare_request_params, validate_request_data, sanitize_phone_number
from .logger import app_logger as logger


class KDNiaoAPIError(Exception):
    """快递鸟API异常"""
    def __init__(self, message: str, error_code: Optional[str] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.response_data = response_data


class KDNiaoClient:
    """快递鸟API客户端"""
    
    def __init__(self, ebusiness_id=None, api_key=None, api_url=None):
        # 优先使用传入的参数，如果没有则使用配置文件中的参数
        self.ebusiness_id = ebusiness_id or config.kdniao.ebusiness_id
        self.api_key = api_key or config.kdniao.api_key
        self.api_url = api_url or config.kdniao.api_url
        self.timeout = config.request.timeout
        self.max_retries = config.request.max_retries
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                'User-Agent': 'KDNiao-MCP-Client/1.0.0'
            }
        )
        
        logger.info("KDNiao client initialized", extra={
            "ebusiness_id": self.ebusiness_id,
            "api_url": self.api_url
        })
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        logger.info("KDNiao client closed")
    
    async def _make_request(self, request_type: str, request_data: Dict[Any, Any]) -> Dict[Any, Any]:
        """发送API请求
        
        Args:
            request_type: 请求类型
            request_data: 请求数据
            
        Returns:
            API响应数据
            
        Raises:
            KDNiaoAPIError: API请求失败
        """
        # 准备请求参数
        params = prepare_request_params(
            self.ebusiness_id,
            request_type,
            request_data,
            self.api_key
        )
        
        # 记录请求日志
        logger.info(f"Making KDNiao API request", extra={
            "request_type": request_type,
            "ebusiness_id": self.ebusiness_id,
            "request_data": request_data
        })
        
        # 重试机制
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                # 发送POST请求
                response = await self.client.post(
                    self.api_url,
                    data=urlencode(params),
                    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
                )
                
                # 检查HTTP状态码
                response.raise_for_status()
                
                # 解析响应数据
                response_text = response.text
                logger.debug(f"Raw API response: {response_text}")
                
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {response_text}")
                    raise KDNiaoAPIError(f"Invalid JSON response: {str(e)}", response_data={"raw_response": response_text})
                
                # 记录响应日志
                logger.info(f"KDNiao API response received", extra={
                    "request_type": request_type,
                    "success": response_data.get('Success', False),
                    "reason": response_data.get('Reason')
                })
                
                return response_data
                
            except httpx.HTTPStatusError as e:
                last_exception = e
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e.response.status_code} - {e.response.text}")
                
                if attempt < self.max_retries:
                    await self._wait_before_retry(attempt)
                    continue
                else:
                    raise KDNiaoAPIError(
                        f"HTTP error after {self.max_retries + 1} attempts: {e.response.status_code}",
                        error_code=str(e.response.status_code),
                        response_data={"status_code": e.response.status_code, "response_text": e.response.text}
                    )
                    
            except httpx.RequestError as e:
                last_exception = e
                logger.warning(f"Request error on attempt {attempt + 1}: {str(e)}")
                
                if attempt < self.max_retries:
                    await self._wait_before_retry(attempt)
                    continue
                else:
                    raise KDNiaoAPIError(
                        f"Request error after {self.max_retries + 1} attempts: {str(e)}",
                        response_data={"error": str(e)}
                    )
        
        # 如果所有重试都失败了
        raise KDNiaoAPIError(
            f"All {self.max_retries + 1} attempts failed",
            response_data={"last_exception": str(last_exception)}
        )
    
    async def _wait_before_retry(self, attempt: int):
        """重试前等待"""
        import asyncio
        wait_time = min(2 ** attempt, 10)  # 指数退避，最大10秒
        logger.info(f"Waiting {wait_time} seconds before retry")
        await asyncio.sleep(wait_time)
    
    async def track_logistics(self, request: TrackRequest) -> TrackResponse:
        """查询快递轨迹
        
        Args:
            request: 轨迹查询请求
            
        Returns:
            轨迹查询响应
        """
        # 验证必需字段
        if not request.LogisticCode:
            raise KDNiaoAPIError("ShipperCode and LogisticCode are required")
        
        # 处理顺丰特殊要求
        request_data = {
            "ShipperCode": request.ShipperCode,
            "LogisticCode": request.LogisticCode
        }
        if request.CustomerName:
                request_data["CustomerName"] = request.CustomerName
        else:
            if request.ShipperCode.upper() == 'SF' or request.ShipperCode.upper() == 'ZTO' or request.ShipperCode.upper() == 'KYSY':
                if not request.CustomerName :
                    raise KDNiaoAPIError("顺丰，中通，跨越速运要求提供寄件人/收件人手机后四位")
            
            
            
        
        # 根据是否有ShipperCode决定使用的接口
        # 如果有ShipperCode使用8001（即时查询），否则使用8002（单号识别+查询）
        request_type = "8001" if request.ShipperCode else "8002"
        response_data = await self._make_request(request_type, request_data)
        
        # 确保响应包含所有必需字段，无论请求是否成功
        response_data.setdefault('EBusinessID', self.ebusiness_id)
        response_data.setdefault('LogisticCode', request.LogisticCode)
        response_data.setdefault('ShipperCode', request.ShipperCode)
        response_data.setdefault('State', 0)  # 默认为暂无轨迹
        response_data.setdefault('StateEx', 0)  # 默认为暂无轨迹
        response_data.setdefault('Traces', [])
        
        # 转换为响应模型
        return TrackResponse(**response_data)
    
    async def recognize_logistics_code(self, request: RecognizeRequest) -> RecognizeResponse:
        """识别快递单号
        
        Args:
            request: 单号识别请求
            
        Returns:
            单号识别响应
        """
        if not request.LogisticCode:
            raise KDNiaoAPIError("LogisticCode is required")
        
        request_data = {
            "LogisticCode": request.LogisticCode
        }
        
        # 发送请求
        response_data = await self._make_request("2002", request_data)
        
        # 确保响应包含所有必需字段
        if not response_data.get('Success', False):
            # 如果请求失败，确保返回所有必需字段
            response_data.setdefault('EBusinessID', self.ebusiness_id)
            response_data.setdefault('LogisticCode', request.LogisticCode)
            response_data.setdefault('Shippers', [])
        
        # 转换为响应模型
        return RecognizeResponse(**response_data)
    
    async def get_time_efficiency(self, request: TimeEfficiencyRequest) -> TimeEfficiencyResponse:
        """查询时效预估
        
        Args:
            request: 时效预估请求
            
        Returns:
            时效预估响应
        """
        # 验证必需字段
        required_fields = [
            "ShipperCode", "SendProvince", "SendCity", "SendArea",
            "ReceiveProvince", "ReceiveCity", "ReceiveArea"
        ]
        
        request_dict = request.dict(exclude_none=True)
        
        for field in required_fields:
            if field not in request_dict or not request_dict[field]:
                raise KDNiaoAPIError(f"{field} is required")
        # 根据是否有快递单号选择请求类型
        if not request.LogisticCode:
            request_type = "6004"  # 发货前时效查询
        else:
            request_type = "6006"  # 发货后时效查询
        
        # 发送请求
        response_data = await self._make_request(request_type, request_dict)
        
        # 处理API响应结构 - API返回的数据在Data字段中
        processed_data = {
            'EBusinessID': response_data.get('EBusinessID', self.ebusiness_id),
            'Success': response_data.get('Success', False),
            'Reason': response_data.get('Reason'),
            'ShipperCode': request.ShipperCode
        }
        
        # 如果有Data字段，提取其中的时效信息
        if 'Data' in response_data and response_data['Data']:
            data = response_data['Data']
            processed_data.update({
                'SendProvince': data.get('SendProvince'),
                'SendCity': data.get('SendCity'),
                'SendArea': data.get('SendArea'),
                'SendAddress': data.get('SendAddress'),
                'ReceiveProvince': data.get('ReceiveProvince'),
                'ReceiveCity': data.get('ReceiveCity'),
                'ReceiveArea': data.get('ReceiveArea'),
                'ReceiveAddress': data.get('ReceiveAddress'),
                'DeliveryTime': data.get('DeliveryTime'),
                'DeliveryDate': data.get('DeliveryDate'),
                'Hour': data.get('Hour'),
                'PredictPath': data.get('PredictPath')
            })
        
        # 转换为响应模型
        return TimeEfficiencyResponse(**processed_data)
    
    async def parse_address(self, request: AddressParseRequest) -> AddressParseResponse:
        """智能地址解析
        
        Args:
            request: 地址解析请求
            
        Returns:
            地址解析响应
        """
        if not request.Content:
            raise KDNiaoAPIError("Content is required")
        
        request_data = {
            "Content": request.Content
        }
        
        # 发送请求
        response_data = await self._make_request("6001", request_data)
        
        # 确保响应包含所有必需字段
        if not response_data.get('Success', False):
            # 如果请求失败，确保返回所有必需字段
            response_data.setdefault('EBusinessID', self.ebusiness_id)
            response_data.setdefault('ResultCode', response_data.get('ResultCode', 'UNKNOWN'))
        
        # 转换为响应模型
        return AddressParseResponse(**response_data)
    
    async def health_check(self) -> bool:
        """健康检查
        
        Returns:
            服务是否正常
        """
        try:
            # 使用一个简单的单号识别请求来检查服务状态
            test_request = RecognizeRequest(LogisticCode="123456789")
            await self.recognize_logistics_code(test_request)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def track_cross_border_logistics(self, request: CrossBorderTrackRequest) -> CrossBorderTrackResponse:
        """查询跨境小包轨迹
        
        Args:
            request: 跨境小包轨迹查询请求
            
        Returns:
            跨境小包轨迹查询响应
        """
        # 验证必需字段
        if not request.ShipperCode or not request.LogisticCode:
            raise KDNiaoAPIError("ShipperCode and LogisticCode are required")
        
        request_data = {
            "ShipperCode": request.ShipperCode,
            "LogisticCode": request.LogisticCode
        }
        
        # 添加可选字段
        if request.OrderCode:
            request_data["OrderCode"] = request.OrderCode
        if request.CustomerName:
            request_data["CustomerName"] = request.CustomerName
        if request.Language:
            request_data["Language"] = request.Language
        if request.CallBack:
            request_data["CallBack"] = request.CallBack
        
        # 使用跨境小包查询接口
        response_data = await self._make_request("7101", request_data)
        
        # 确保响应包含所有必需字段
        response_data.setdefault('EBusinessID', self.ebusiness_id)
        response_data.setdefault('ShipperCode', request.ShipperCode)
        response_data.setdefault('LogisticCode', request.LogisticCode)
        response_data.setdefault('State', '0')  # 默认为查询中
        response_data.setdefault('Traces', [])
        
        # 转换为响应模型
        return CrossBorderTrackResponse(**response_data)
    
    async def subscribe_cross_border_logistics(self, request: CrossBorderSubscribeRequest) -> CrossBorderSubscribeResponse:
        """订阅跨境小包轨迹推送
        
        Args:
            request: 跨境小包轨迹订阅请求
            
        Returns:
            跨境小包轨迹订阅响应
        """
        # 验证必需字段
        if not request.ShipperCode or not request.LogisticCode:
            raise KDNiaoAPIError("ShipperCode and LogisticCode are required")
        
        request_data = {
            "ShipperCode": request.ShipperCode,
            "LogisticCode": request.LogisticCode
        }
        
        # 添加可选字段
        if request.OrderCode:
            request_data["OrderCode"] = request.OrderCode
        if request.CustomerName:
            request_data["CustomerName"] = request.CustomerName
        if request.Language:
            request_data["Language"] = request.Language
        if request.CallbackUrl:
            request_data["CallbackUrl"] = request.CallbackUrl
        
        # 使用跨境小包订阅接口
        response_data = await self._make_request("7108", request_data)
        
        # 确保响应包含所有必需字段
        response_data.setdefault('EBusinessID', self.ebusiness_id)
        response_data.setdefault('UpdateTime', '')
        
        # 转换为响应模型
        return CrossBorderSubscribeResponse(**response_data)
    
    async def query_service_points(self, request: ServicePointRequest) -> ServicePointResponse:
        """网点查询
        
        Args:
            request: 网点查询请求
            
        Returns:
            网点查询响应
        """
        if not request.ShipperCode:
            raise KDNiaoAPIError("ShipperCode is required")
        if not request.ProvinceName:
            raise KDNiaoAPIError("ProvinceName is required")
        
        request_data = {
            "ShipperCode": request.ShipperCode,
            "ProvinceName": request.ProvinceName
        }
        
        # 添加可选字段
        if request.CityName:
            request_data["CityName"] = request.CityName
        if request.AreaName:
            request_data["AreaName"] = request.AreaName
        if request.Address:
            request_data["Address"] = request.Address
        
        # 发送请求 - 使用网点查询接口 RequestType 6002
        response_data = await self._make_request("6002", request_data)
        
        # 确保响应包含所有必需字段
        if not response_data.get('Success', False):
            # 如果请求失败，确保返回所有必需字段
            response_data.setdefault('EBusinessID', self.ebusiness_id)
            response_data.setdefault('ResultCode', response_data.get('ResultCode', 'UNKNOWN'))
        
        # 转换为响应模型
        return ServicePointResponse(**response_data)