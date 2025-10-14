"""快递鸟API数据模型定义"""

from enum import IntEnum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TrackingState(IntEnum):
    """物流状态"""
    NO_TRACE = 0
    COLLECTED = 1
    IN_TRANSIT = 2
    SIGNED = 3
    PROBLEM = 4
    FORWARDED = 5
    CUSTOMS = 6


class DetailedTrackingState(IntEnum):
    """详细物流状态定义"""
    # 基本状态
    NO_TRACE = 0
    COLLECTED = 1
    IN_TRANSIT = 2
    SIGNED = 3
    PROBLEM = 4
    FORWARDED = 5
    CUSTOMS = 6
    
    # 详细状态
    WAITING_PICKUP = 10
    ARRIVED_DESTINATION = 201
    OUT_FOR_DELIVERY = 202
    IN_LOCKER_STATION = 211
    AT_SORTING_CENTER = 204
    AT_DELIVERY_POINT = 205
    DISPATCHED_FROM_ORIGIN = 206
    NORMAL_DELIVERY = 301
    DELIVERED_AFTER_PROBLEM = 302
    PROXY_DELIVERY = 304
    LOCKER_DELIVERY = 311
    NO_SHIPPING_INFO = 401
    DELIVERY_TIMEOUT = 402
    UPDATE_TIMEOUT = 403
    REJECTED = 404
    DELIVERY_EXCEPTION = 405
    RETURN_DELIVERED = 406
    RETURN_NOT_DELIVERED = 407
    LOCKER_TIMEOUT = 412
    INTERCEPTED = 413
    DAMAGED = 414
    CANCELLED = 415
    UNREACHABLE = 416
    DELIVERY_DELAYED = 417
    REMOVED_FROM_LOCKER = 418
    REDELIVERY = 419
    ADDRESS_INCOMPLETE = 420
    PHONE_ERROR = 421
    MISSORTED = 422
    OUT_OF_RANGE = 423
    AWAITING_CLEARANCE = 601
    CLEARING_CUSTOMS = 602
    CUSTOMS_CLEARED = 603
    CUSTOMS_EXCEPTION = 604


class TrackTrace(BaseModel):
    """轨迹信息"""
    AcceptTime: str = Field(..., description="时间 '2024-01-15 10:30:00'")
    AcceptStation: str = Field(..., description="描述")
    Remark: Optional[str] = Field(None, description="备注")
    Location: Optional[str] = Field(None, description="所在城市")


class TrackRequest(BaseModel):
    """轨迹查询请求"""
    LogisticCode: str = Field(..., description="快递单号")
    ShipperCode: Optional[str] = Field(None, description="快递公司编码，如 'STO', 'YTO', 'ZTO'")
    CustomerName: Optional[str] = Field(None, description="手机号后四位（顺丰必填）")


class TrackResponse(BaseModel):
    """轨迹查询响应"""
    EBusinessID: str
    Success: bool
    Reason: Optional[str] = None
    State: int = Field(..., description="物流状态码")
    StateEx: int = Field(..., description="详细物流状态码")
    LogisticCode: str
    ShipperCode: str
    Traces: List[TrackTrace] = Field(default_factory=list)


class ShipperInfo(BaseModel):
    """快递公司信息"""
    ShipperCode: str = Field(..., description="快递公司编码")
    ShipperName: str = Field(..., description="快递公司名称")


class RecognizeRequest(BaseModel):
    """单号识别请求"""
    LogisticCode: str = Field(..., description="快递单号")


class RecognizeResponse(BaseModel):
    """单号识别响应"""
    EBusinessID: str
    Success: bool
    LogisticCode: str
    Reason: Optional[str] = None
    Shippers: List[ShipperInfo] = Field(default_factory=list)


class TimeEfficiencyRequest(BaseModel):
    """时效预估请求"""
    ShipperCode: str = Field(..., description="快递公司编码")
    LogisticCode: Optional[str] = Field(None, description="发货后必填")
    SendProvince: str = Field(..., description="寄件省份")
    SendCity: str = Field(..., description="寄件城市")
    SendArea: str = Field(..., description="寄件区县")
    SendAddress: Optional[str] = Field(None, description="寄件详细地址")
    ReceiveProvince: str = Field(..., description="收件省份")
    ReceiveCity: str = Field(..., description="收件城市")
    ReceiveArea: str = Field(..., description="收件区县")
    ReceiveAddress: Optional[str] = Field(None, description="收件详细地址")
    CatchTime: Optional[str] = Field(None, description="揽收时间")
    SenderPhone: Optional[str] = Field(None, description="寄件人手机后四位（顺丰必填）")
    ReceiverPhone: Optional[str] = Field(None, description="收件人手机后四位（顺丰必填）")
    Weight: Optional[float] = Field(None, description="重量(KG)")
    Volume: Optional[float] = Field(None, description="体积(cm³)")
    Quantity: Optional[int] = Field(1, description="件数")


class TimeEfficiencyResponse(BaseModel):
    """时效预估响应"""
    EBusinessID: str
    Success: bool
    Reason: Optional[str] = None
    LogisticCode: Optional[str] = None
    ShipperCode: str
    SendProvince: Optional[str] = Field(None, description="始发省")
    SendCity: Optional[str] = Field(None, description="始发市")
    SendArea: Optional[str] = Field(None, description="始发区县")
    SendAddress: Optional[str] = Field(None, description="始发详细地址")
    ReceiveProvince: Optional[str] = Field(None, description="目的省")
    ReceiveCity: Optional[str] = Field(None, description="目的市")
    ReceiveArea: Optional[str] = Field(None, description="目的区县")
    ReceiveAddress: Optional[str] = Field(None, description="目的详细地址")
    LatestStation: Optional[str] = Field(None, description="最新轨迹发生的站点（发货后）")
    LatestProvince: Optional[str] = Field(None, description="最新所在省份（发货后）")
    LatestCity: Optional[str] = Field(None, description="最新所在城市（发货后）")
    LatestArea: Optional[str] = Field(None, description="最新所在区县（发货后）")
    DeliveryTime: Optional[str] = Field(None, description="预计送达时间，如：06月15日下午可达")
    DeliveryDate: Optional[str] = Field(None, description="预计送达日期，格式：2024-04-20")
    Hour: Optional[str] = Field(None, description="预计时效，如：36h")
    PredictPath: Optional[str] = Field(None, description="预估行驶线路")
    DeliveryMemo: Optional[str] = Field(None, description="备注（发货后）")


class AddressParseRequest(BaseModel):
    """地址解析请求"""
    Content: str = Field(..., description="待识别的完整地址，为提高准确率不同信息可用空格区分")


class AddressParseData(BaseModel):
    """地址解析数据"""
    Name: Optional[str] = Field(None, description="姓名")
    Mobile: Optional[str] = Field(None, description="手机号/座机号")
    ExtMobile: Optional[str] = Field(None, description="分机号")
    ProvinceName: Optional[str] = Field(None, description="省份")
    CityName: Optional[str] = Field(None, description="城市")
    ExpAreaName: Optional[str] = Field(None, description="所在地区/县级市")
    StreetName: Optional[str] = Field(None, description="街道名称")
    Address: Optional[str] = Field(None, description="详细地址")


class AddressParseResponse(BaseModel):
    """地址解析响应"""
    EBusinessID: str
    Success: bool
    Reason: Optional[str] = None
    ResultCode: str
    Data: Optional[AddressParseData] = None


class CrossBorderTrackingState(IntEnum):
    """跨境物流状态"""
    QUERYING = 0  # 正在查询中
    COLLECTING = 1  # 揽收中
    IN_TRANSIT = 2  # 在途中
    SIGNED = 3  # 签收
    PROBLEM = 4  # 问题件
    DIFFICULT = 5  # 疑难件
    CUSTOMS = 6  # 清关


class CrossBorderDetailedState(IntEnum):
    """跨境详细物流状态"""
    # 在途中详细状态
    ARRIVED_HUB = 204  # 货件到达枢纽或分拣中心
    ARRIVED_PICKUP_POINT = 211  # 包裹到达附近代取点
    ARRIVED_DESTINATION_COUNTRY = 222  # 到达目的国/地区
    DEPARTED_AIRPORT = 220  # 从机场出发
    ARRIVED_AIRPORT = 221  # 到达目的机场
    
    # 派送状态
    OUT_FOR_DELIVERY = 202  # 包裹派送中
    CONTACT_BEFORE_DELIVERY = 223  # 派送前联系客户
    SCHEDULED_DELIVERY = 224  # 预约派送
    
    # 签收状态
    SUCCESSFUL_DELIVERY = 301  # 成功签收
    SIGNATURE_DELIVERY = 305  # 客户签名签收
    SELF_PICKUP = 306  # 客户自提成功
    COD_SUCCESS = 307  # 货到付款成功
    THIRD_PARTY_DELIVERY = 304  # 第三方代签收
    
    # 问题件状态
    ADDRESS_UNAVAILABLE = 420  # 收货地址不可用
    RECIPIENT_NOT_FOUND = 416  # 找不到收件人
    BUSINESS_CANCELLED = 415  # 交货时，业务取消
    DELIVERY_REFUSED = 404  # 收件人拒收，交付失败
    LONG_TERM_UNCLAIMED = 424  # 客户长期不领取包裹
    RETURNING_TO_SENDER = 425  # 包裹正在退回给发件人中
    RETURNED_TO_SENDER = 406  # 包裹已成功退回发件人
    PACKAGE_DAMAGED = 414  # 包裹破损、遗失或被丢弃
    PACKAGE_LOST = 426  # 包裹丢失
    PACKAGE_VIOLATION = 427  # 包裹违规，承运商拒绝
    INCORRECT_ADDRESS = 420  # 收件人地址不正确
    ORDER_CANCELLED = 430  # 订单在揽件前被取消
    
    # 清关状态
    CUSTOMS_HANDOVER = 605  # 移交清关
    CUSTOMS_CLEARED = 603  # 清关完成
    CUSTOMS_DELAYED = 604  # 清关问题，包裹延误
    CUSTOMS_PAYMENT_REQUIRED = 606  # 客户未付款，海关扣留


class CrossBorderTrackTrace(BaseModel):
    """跨境轨迹信息"""
    AcceptTime: str = Field(..., description="轨迹发生时间，示例：2024-06-28T11:23:51")
    AcceptStation: str = Field(..., description="轨迹描述")
    Location: Optional[str] = Field(None, description="国家/地区、州、城市（STOCKTON,CA,US）")
    Action: str = Field(..., description="同StateEx，详细状态码")
    Timezone: Optional[str] = Field(None, description="轨迹时区，如：-05:00")
    Remark: Optional[str] = Field(None, description="备注")


class CrossBorderTrackRequest(BaseModel):
    """跨境小包轨迹查询请求"""
    ShipperCode: str = Field(..., description="物流公司编码，见支持表--物流商简码")
    LogisticCode: str = Field(..., description="快递单号")
    OrderCode: Optional[str] = Field(None, description="订单编号")
    CallBack: Optional[str] = Field(None, description="用户自定义回传字段")
    CustomerName: Optional[str] = Field(None, description="客户名称")
    Language: Optional[str] = Field(None, description="语言设置，待更新...")


class CrossBorderTrackResponse(BaseModel):
    """跨境小包轨迹查询响应"""
    EBusinessID: str = Field(..., description="用户ID")
    ShipperCode: str = Field(..., description="快递公司编码")
    LogisticCode: str = Field(..., description="快递单号")
    Success: bool = Field(..., description="成功与否(true/false)")
    Reason: Optional[str] = Field(None, description="失败原因")
    State: str = Field(..., description="物流状态编码")
    StateEx: Optional[str] = Field(None, description="详细物流状态编码")
    Location: Optional[str] = Field(None, description="当前所在城市")
    Traces: List[CrossBorderTrackTrace] = Field(default_factory=list, description="轨迹详情列表")


class CrossBorderSubscribeRequest(BaseModel):
    """跨境小包订阅请求"""
    ShipperCode: str = Field(..., description="物流公司编码，见支持表--物流商简码")
    LogisticCode: str = Field(..., description="快递单号")
    OrderCode: Optional[str] = Field(None, description="订单编号")
    CustomerName: Optional[str] = Field(None, description="客户名称")
    Language: Optional[str] = Field(None, description="语言设置，待更新...")
    CallbackUrl: Optional[str] = Field(None, description="轨迹回调地址")


class CrossBorderSubscribeResponse(BaseModel):
    """跨境小包订阅响应"""
    EBusinessID: str = Field(..., description="用户ID")
    UpdateTime: str = Field(..., description="更新时间")
    Success: bool = Field(..., description="成功与否(true/false)")
    ShipperCode: Optional[str] = Field(None, description="快递公司编码")
    LogisticCode: Optional[str] = Field(None, description="快递单号")
    Reason: Optional[str] = Field(None, description="失败原因")


class ShipperInfo(BaseModel):
    """快递公司信息"""
    ShipperCode: str = Field(..., description="快递公司编码")
    ShipperName: str = Field(..., description="快递公司名称")


class RecognizeRequest(BaseModel):
    """单号识别请求"""
    LogisticCode: str = Field(..., description="快递单号")


class RecognizeResponse(BaseModel):
    """单号识别响应"""
    EBusinessID: str
    Success: bool
    LogisticCode: str
    Reason: Optional[str] = None
    Shippers: List[ShipperInfo] = Field(default_factory=list)


class TimeEfficiencyRequest(BaseModel):
    """时效预估请求"""
    ShipperCode: str = Field(..., description="快递公司编码")
    LogisticCode: Optional[str] = Field(None, description="发货后必填")
    SendProvince: str = Field(..., description="寄件省份")
    SendCity: str = Field(..., description="寄件城市")
    SendArea: str = Field(..., description="寄件区县")
    SendAddress: Optional[str] = Field(None, description="寄件详细地址")
    ReceiveProvince: str = Field(..., description="收件省份")
    ReceiveCity: str = Field(..., description="收件城市")
    ReceiveArea: str = Field(..., description="收件区县")
    ReceiveAddress: Optional[str] = Field(None, description="收件详细地址")
    CatchTime: Optional[str] = Field(None, description="揽收时间")
    SenderPhone: Optional[str] = Field(None, description="寄件人手机后四位（顺丰必填）")
    ReceiverPhone: Optional[str] = Field(None, description="收件人手机后四位（顺丰必填）")
    Weight: Optional[float] = Field(None, description="重量(KG)")
    Volume: Optional[float] = Field(None, description="体积(cm³)")
    Quantity: Optional[int] = Field(1, description="件数")


class TimeEfficiencyResponse(BaseModel):
    """时效预估响应"""
    EBusinessID: str
    Success: bool
    Reason: Optional[str] = None
    LogisticCode: Optional[str] = None
    ShipperCode: str
    SendProvince: Optional[str] = Field(None, description="始发省")
    SendCity: Optional[str] = Field(None, description="始发市")
    SendArea: Optional[str] = Field(None, description="始发区县")
    SendAddress: Optional[str] = Field(None, description="始发详细地址")
    ReceiveProvince: Optional[str] = Field(None, description="目的省")
    ReceiveCity: Optional[str] = Field(None, description="目的市")
    ReceiveArea: Optional[str] = Field(None, description="目的区县")
    ReceiveAddress: Optional[str] = Field(None, description="目的详细地址")
    LatestStation: Optional[str] = Field(None, description="最新轨迹发生的站点（发货后）")
    LatestProvince: Optional[str] = Field(None, description="最新所在省份（发货后）")
    LatestCity: Optional[str] = Field(None, description="最新所在城市（发货后）")
    LatestArea: Optional[str] = Field(None, description="最新所在区县（发货后）")
    DeliveryTime: Optional[str] = Field(None, description="预计送达时间，如：06月15日下午可达")
    DeliveryDate: Optional[str] = Field(None, description="预计送达日期，格式：2024-04-20")
    Hour: Optional[str] = Field(None, description="预计时效，如：36h")
    PredictPath: Optional[str] = Field(None, description="预估行驶线路")
    DeliveryMemo: Optional[str] = Field(None, description="备注（发货后）")


class AddressParseRequest(BaseModel):
    """地址解析请求"""
    Content: str = Field(..., description="待识别的完整地址，为提高准确率不同信息可用空格区分")


class AddressParseData(BaseModel):
    """地址解析数据"""
    Name: Optional[str] = Field(None, description="姓名")
    Mobile: Optional[str] = Field(None, description="手机号/座机号")
    ExtMobile: Optional[str] = Field(None, description="分机号")
    ProvinceName: Optional[str] = Field(None, description="省份")
    CityName: Optional[str] = Field(None, description="城市")
    ExpAreaName: Optional[str] = Field(None, description="所在地区/县级市")
    StreetName: Optional[str] = Field(None, description="街道名称")
    Address: Optional[str] = Field(None, description="详细地址")


class AddressParseResponse(BaseModel):
    """地址解析响应"""
    EBusinessID: str
    Success: bool
    Reason: Optional[str] = None
    ResultCode: str
    Data: Optional[AddressParseData] = None


class ServicePointRequest(BaseModel):
    """网点查询请求"""
    ShipperCode: str = Field(..., description="快递公司编码")
    ProvinceName: str = Field(..., description="省份")
    CityName: Optional[str] = Field(None, description="城市")
    AreaName: Optional[str] = Field(None, description="区县")
    Address: Optional[str] = Field(None, description="地址关键词（模糊匹配），顺丰和极兔必填")


class ServicePointInfo(BaseModel):
    """网点信息"""
    ShipperCode: str = Field(..., description="快递公司编码")
    ShipperName: str = Field(..., description="快递公司名称")
    PointCode: Optional[str] = Field(None, description="网点编码")
    PointName: str = Field(..., description="网点名称")
    ProvinceName: str = Field(..., description="所在省")
    CityName: str = Field(..., description="所在市")
    AreaName: str = Field(..., description="所在区")
    StreetName: Optional[str] = Field(None, description="所在街道")
    Address: str = Field(..., description="详细地址")
    Contact: Optional[str] = Field(None, description="网点联系人")
    Tel: Optional[str] = Field(None, description="网点联系电话")
    ServiceTime: Optional[str] = Field(None, description="服务时间")
    Longitude: Optional[int] = Field(None, description="经度")
    Latitude: Optional[int] = Field(None, description="纬度")


class ServicePointResponse(BaseModel):
    """网点查询响应"""
    EBusinessID: str = Field(..., description="用户ID")
    Success: bool = Field(..., description="成功与否")
    ResultCode: str = Field(..., description="返回编码")
    Reason: Optional[str] = Field(None, description="失败原因")
    Count: Optional[int] = Field(None, description="网点数量")
    ServicePointInfos: List[ServicePointInfo] = Field(default_factory=list, description="网点信息列表")


# 快递公司编码映射
# 注意：详细的快递公司编码映射已移至kdniao_docs.py
from models.kdniao_docs import SHIPPER_CODES


def get_shipper_name(code: str) -> str:
    """根据编码获取快递公司名称
    
    注意：此函数使用kdniao_docs.py中的SHIPPER_CODES
    """
    from models.kdniao_docs import SHIPPER_CODES
    return SHIPPER_CODES.get(code.upper(), code)


def get_state_description(state: int, state_ex: int = None) -> str:
    """获取状态描述
    
    注意：此函数仅返回基本状态描述，详细状态描述请参考文档模型
    """
    # 从文档模型中获取状态描述
    from models.kdniao_docs import get_state_description as get_doc_state_description
    
    # 如果有详细状态，优先使用详细状态
    if state_ex is not None:
        return get_doc_state_description(state_ex=state_ex)
    
    return get_doc_state_description(state=state)