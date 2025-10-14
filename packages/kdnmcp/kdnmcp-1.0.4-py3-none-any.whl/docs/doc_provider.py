"""快递鸟文档资源提供者"""

import os
from typing import Dict, List, Any, Optional

from models.kdniao_docs import (
    KDNiaoDocResources,
    TrackingDocInfo,
    RecognizeDocInfo,
    TimelineDocInfo,
    StateCodeInfo,
    CrossBorderTrackingDocInfo,
    ServicePointDocInfo
)
from utils.logger import app_logger as logger


class DocProvider:
    """文档资源提供者"""
    
    def __init__(self, doc_dir: str = None):
        """初始化文档提供者
        """
        
        
    def get_all_docs(self) -> KDNiaoDocResources:
        """获取所有文档资源"""
        try:
            return KDNiaoDocResources(
            tracking=self._get_tracking_doc(),
            recognize=self._get_recognize_doc(),
            timeline=self._get_timeline_doc(),
            address_parse=self._get_address_parse_doc(),
            service_point=self._get_service_point_doc(),
            state_codes=self._get_state_codes(),
            state_ex_codes=self._get_state_ex_codes(),
            cross_border_tracking=self._get_cross_border_tracking_doc(),
            cross_border_state_codes=self._get_cross_border_state_codes()
        )
        except Exception as e:
            logger.error(f"Error getting all docs: {e}")
            raise
    
    def _get_tracking_doc(self) -> TrackingDocInfo:
        """获取轨迹查询文档信息"""
        # 即时查询和快递查询合并为轨迹查询文档
        return TrackingDocInfo(
            request_type="8001(即时查询)/8002(快递查询)",
            batch_support="不支持，并发20次/秒",
            billing_rule="8001: 40个自然日内同一(物流编码+单号)不限查询次数，计费1单；查询无轨迹不计费\n8002: 按请求成功次数计算，返回无轨迹不做计费",
            sort_rule="默认按照发生时间的升序排列",
            api_url="https://api.kdniao.com/api/dist",
            supported_companies="支持查询国内物流公司轨迹，国际查询支持DHL、UPS、FEDEX",
            special_requirements=[
                "顺丰/跨越速运/中通快递：须通过CustomerName传正确的寄件人or收件人的手机号码/座机号后四位方可查询",
                "菜鸟橙运需要传入菜鸟橙运分配的货主编号",
                "中通仅支持查询签收后6个月内的单号"
            ],
            request_params={
                "ShipperCode": {
                    "type": "String(10)",
                    "required": True,
                    "description": "快递公司编码，8002接口可选"
                },
                "LogisticCode": {
                    "type": "String(30)",
                    "required": True,
                    "description": "快递单号"
                },
                "CustomerName": {
                    "type": "String(50)",
                    "required": False,
                    "description": "寄件人or收件人手机号/座机号后四位，顺丰/跨越/中通必填"
                },
                "Sort": {
                    "type": "Int(1)",
                    "required": False,
                    "description": "轨迹按时间排序，0-升序，1-降序，默认0"
                },
                "OrderCode": {
                    "type": "String(30)",
                    "required": False,
                    "description": "订单编号"
                }
            },
            response_params={
                "EBusinessID": {
                    "type": "String(10)",
                    "required": True,
                    "description": "用户ID"
                },
                "ShipperCode": {
                    "type": "String(10)",
                    "required": True,
                    "description": "快递公司编码"
                },
                "LogisticCode": {
                    "type": "String(30)",
                    "required": True,
                    "description": "快递单号"
                },
                "Success": {
                    "type": "Bool(10)",
                    "required": True,
                    "description": "成功与否(true/false)"
                },
                "Reason": {
                    "type": "String(50)",
                    "required": False,
                    "description": "失败原因"
                },
                "State": {
                    "type": "String(5)",
                    "required": True,
                    "description": "普通物流状态：0-暂无轨迹，1-已揽收，2-在途中，3-已签收，4-问题件，5-转寄"
                },
                "StateEx": {
                    "type": "String(5)",
                    "required": True,
                    "description": "详细物流状态，如1-已揽收，10-待揽件，201-到达派件城市等"
                },
                "Location": {
                    "type": "String(20)",
                    "required": True,
                    "description": "当前所在城市"
                },
                "Traces.AcceptTime": {
                    "type": "String(32)",
                    "required": True,
                    "description": "轨迹发生时间"
                },
                "Traces.AcceptStation": {
                    "type": "String(500)",
                    "required": True,
                    "description": "轨迹描述"
                },
                "Traces.Location": {
                    "type": "String(20)",
                    "required": False,
                    "description": "历史节点所在城市"
                },
                "Traces.Action": {
                    "type": "String(50)",
                    "required": True,
                    "description": "同StateEx"
                },
                "Traces.Remark": {
                    "type": "String(20)",
                    "required": False,
                    "description": "备注"
                }
            }
        )
    
    def _get_recognize_doc(self) -> RecognizeDocInfo:
        """获取单号识别文档信息"""
        return RecognizeDocInfo(
            request_type="2002",
            batch_support="不支持，并发不超过10次/S",
            billing_rule="按请求成功次数计算。当返回无结果（Shippers=[]）时，不计费",
            api_url="https://api.kdniao.com/api/dist",
            rules=[
                "接口只对快递单号进行识别，返回可能属于的一家或多家快递公司，实际归属哪家快递公司仍需用户判断",
                "识别失败，接口返回为空；如发现识别错误，请联系我们订正数据",
                "快递公司新上线的号段首次会识别失败；进行轨迹订阅并拉取到轨迹后，单号识别接口学习机制会完善此类单号的识别",
                "由于各快递公司单号生成规则独立，存在一个单号规则命中多家快递的情况，若返回多结果，需用户侧人工判断"
            ],
            request_params={
                "LogisticCode": {
                    "type": "String(30)",
                    "required": True,
                    "description": "快递单号"
                }
            },
            response_params={
                "EBusinessID": {
                    "type": "String(10)",
                    "required": True,
                    "description": "用户ID"
                },
                "LogisticCode": {
                    "type": "String(30)",
                    "required": True,
                    "description": "快递单号"
                },
                "Success": {
                    "type": "Bool(10)",
                    "required": True,
                    "description": "成功与否(true/false)"
                },
                "Reason": {
                    "type": "String(30)",
                    "required": False,
                    "description": "失败原因"
                },
                "Shippers.ShipperCode": {
                    "type": "String(10)",
                    "required": False,
                    "description": "快递公司编码"
                },
                "Shippers.ShipperName": {
                    "type": "String(30)",
                    "required": False,
                    "description": "快递公司名称"
                }
            }
        )
    
    def _get_address_parse_doc(self) -> TrackingDocInfo:
        """获取地址解析文档信息"""
        return TrackingDocInfo(
            request_type="6001",
            batch_support="不支持批量，可并发",
            billing_rule="按请求成功次数计费，请求失败不计费",
            sort_rule="不适用",
            api_url="https://api.kdniao.com/api/dist",
            supported_companies="支持全国地址解析",
            special_requirements=[
                "地址字符串长度不超过200个字符",
                "支持中文地址解析",
                "返回省市区县及详细地址信息"
            ],
            request_params={
                "Address": {
                    "type": "String(200)",
                    "required": True,
                    "description": "需要解析的地址字符串"
                }
            },
            response_params={
                "EBusinessID": {
                    "type": "String(10)",
                    "required": True,
                    "description": "用户ID"
                },
                "Success": {
                    "type": "Bool(10)",
                    "required": True,
                    "description": "成功与否(true/false)"
                },
                "Reason": {
                    "type": "String(50)",
                    "required": False,
                    "description": "失败原因"
                },
                "Data.Province": {
                    "type": "String(20)",
                    "required": False,
                    "description": "省份"
                },
                "Data.City": {
                    "type": "String(20)",
                    "required": False,
                    "description": "城市"
                },
                "Data.County": {
                    "type": "String(20)",
                    "required": False,
                    "description": "区县"
                },
                "Data.Detail": {
                    "type": "String(200)",
                    "required": False,
                    "description": "详细地址"
                }
            }
        )
    
    def _get_timeline_doc(self) -> TimelineDocInfo:
        """获取时效预估文档信息"""
        return TimelineDocInfo(
            request_type="6004(发货前)/6006(发货后)/6016(发货后)",
            batch_support="不支持批量，可并发",
            billing_rule={
                "6004/6006": "按照请求成功次数计费，请求失败不计费",
                "6016": "40个自然日内1个物流编码+1个单号不限查询次数，订阅成功即计算使用1单"
            },
            api_url="https://api.kdniao.com/api/dist",
            scenarios=[
                {
                    "name": "发货前调用",
                    "description": "买家浏览商品-下单前，根据买家默认地址--商家发货地址计算预计到达时间，减少沟通成本"
                },
                {
                    "name": "发货后调用",
                    "description": "在轨迹信息更新中动态显示预计送达时间，减少买家信息差，提升服务体验"
                }
            ],
            request_params={
                "ShipperCode": {
                    "type": "String(10)",
                    "required": True,
                    "description": "快递公司编码"
                },
                "SendProvince": {
                    "type": "String(20)",
                    "required": True,
                    "description": "始发省"
                },
                "SendCity": {
                    "type": "String(20)",
                    "required": True,
                    "description": "始发市"
                },
                "SendArea": {
                    "type": "String(20)",
                    "required": True,
                    "description": "始发区县"
                },
                "SendAddress": {
                    "type": "String(20)",
                    "required": False,
                    "description": "始发详细地址"
                },
                "ReceiveProvince": {
                    "type": "String(20)",
                    "required": True,
                    "description": "目的省"
                },
                "ReceiveCity": {
                    "type": "String(20)",
                    "required": True,
                    "description": "目的市"
                },
                "ReceiveArea": {
                    "type": "String(20)",
                    "required": True,
                    "description": "目的区县"
                },
                "ReceiveAddress": {
                    "type": "String(20)",
                    "required": False,
                    "description": "目的详细地址"
                },
                "CatchTime": {
                    "type": "LocalDataTime",
                    "required": False,
                    "description": "揽收时间，如不传，默认当前时间为揽收时间"
                }
            },
            response_params={
                "DeliveryTime": {
                    "type": "String",
                    "required": True,
                    "description": "预计送达时间，示例：06月15日下午可达"
                },
                "DeliveryDate": {
                    "type": "String",
                    "required": True,
                    "description": "xxxx-xx-xx格式日期，示例：2024-04-20"
                },
                "Hour": {
                    "type": "String",
                    "required": True,
                    "description": "预计时效，示例：36h"
                },
                "PredictPath": {
                    "type": "String",
                    "required": False,
                    "description": "预估行驶线路，示例：深圳观澜事业部->深圳转运中心->广州转运中心->广州白云投揽部"
                }
            },
            delivery_time_calculation=[
                "有传入揽收时间：DeliveryTime=揽收时间+预计时效",
                "没有传入揽收时间：DeliveryTime=当前时间+预计时效",
                "0~12小时上午可达；12~24小时下午可达"
            ]
        )
    
    def _get_state_codes(self) -> List[StateCodeInfo]:
        """获取普通物流状态码信息"""
        return [
            StateCodeInfo(code="0", name="暂无轨迹信息", description="货物暂无轨迹信息"),
            StateCodeInfo(code="1", name="已揽收", description="快递员已上门揽收快递"),
            StateCodeInfo(code="2", name="在途中", description="货物在途中运输"),
            StateCodeInfo(code="3", name="已签收", description="快件被签收"),
            StateCodeInfo(code="4", name="问题件", description="货物运输途中存在异常（若中途存在问题件，则后续轨迹将一直保持问题件状态）"),
            StateCodeInfo(code="5", name="转寄", description="快递被转寄到新地址")
        ]
    
    def _get_state_ex_codes(self) -> List[StateCodeInfo]:
        """获取详细物流状态码信息"""
        return [
            # 已揽收
            StateCodeInfo(code="1", name="已揽收", description="快递员已上门揽收快递"),
            StateCodeInfo(code="10", name="待揽件", description="快递员未去取件"),
            # 在途中
            StateCodeInfo(code="201", name="到达派件城市", description="快件到达派件城市"),
            StateCodeInfo(code="202", name="派件中", description="快件由派件员进行派件"),
            StateCodeInfo(code="211", name="已放入快递柜或驿站", description="快件放入快递柜或者驿站"),
            StateCodeInfo(code="204", name="到达转运中心", description="快件在转运中心做到件扫描"),
            StateCodeInfo(code="205", name="到达派件网点", description="快件在派件网点做到件扫描"),
            StateCodeInfo(code="206", name="寄件网点发件", description="快件在寄件网点做发件扫描"),
            StateCodeInfo(code="2", name="在途", description="货物在途中运输"),
            # 已签收
            StateCodeInfo(code="301", name="正常签收", description="快件由收件人签收"),
            StateCodeInfo(code="302", name="异常后最终签收", description="快件途中出现异常后，正常签收"),
            StateCodeInfo(code="304", name="代收签收", description="快件由非收件人本人代签"),
            StateCodeInfo(code="311", name="快递柜或驿站签收", description="快件由快递柜或驿站签收"),
            StateCodeInfo(code="3", name="已签收", description="快件被签收"),
            # 转寄
            StateCodeInfo(code="5", name="转寄", description="快递被转寄到新地址"),
            # 问题件
            StateCodeInfo(code="401", name="发货无信息", description="运单轨迹中没有任何描述，或者直接为空，或者描述上发货无信息"),
            StateCodeInfo(code="402", name="超时未签收", description="运单最后一条轨迹(含有派件动作的描述)，该条轨迹产生时间，距当前查询时间，超时36小时或轨迹中描述超时未签收"),
            StateCodeInfo(code="403", name="超时未更新", description="运单轨迹最后一条时间距当前时间超过5天"),
            StateCodeInfo(code="404", name="拒收（退件）", description="客户拒收产生退件"),
            StateCodeInfo(code="405", name="派件异常", description="派件异常"),
            StateCodeInfo(code="406", name="退货签收", description="退件后由寄件人进行签收"),
            StateCodeInfo(code="407", name="退货未签收", description="退件后由寄件人未签收"),
            StateCodeInfo(code="412", name="快递柜或驿站超时未取", description="放入快递柜后超过18个小时没有取件"),
            StateCodeInfo(code="413", name="单号已拦截", description="快件在途中被快递员拦截"),
            StateCodeInfo(code="414", name="破损", description="货物破损"),
            StateCodeInfo(code="415", name="客户取消发货", description="客户取消下单"),
            StateCodeInfo(code="416", name="无法联系", description="派送中无法联系到收件人"),
            StateCodeInfo(code="417", name="配送延迟", description="快递公司配送延迟"),
            StateCodeInfo(code="418", name="快件取出", description="快递员把快件从快递柜取出"),
            StateCodeInfo(code="419", name="重新派送", description="快递员与客户沟通 重新派送"),
            StateCodeInfo(code="420", name="收货地址不详细", description="收货地址不详细"),
            StateCodeInfo(code="421", name="收件人电话错误", description="收件人电话错误"),
            StateCodeInfo(code="422", name="错分件", description="网点或中心错误分拣"),
            StateCodeInfo(code="423", name="超区件", description="派件超出派送范围"),
            StateCodeInfo(code="4", name="问题件", description="问题件"),
            # 清关
            StateCodeInfo(code="6", name="清关", description="货物在目的国清关"),
            StateCodeInfo(code="601", name="待清关", description="货物在目的国待清关"),
            StateCodeInfo(code="602", name="清关中", description="货物在目的国清关"),
            StateCodeInfo(code="603", name="已清关", description="货物在目的国已清关"),
            StateCodeInfo(code="604", name="清关异常", description="货物在目的国出现清关异常")
        ]
        
    def _get_supported_shippers_doc(self) -> Dict[str, Any]:
        """获取单号识别支持的快递公司文档"""
        # 直接在代码中定义快递公司编码和名称，而不是从文件中读取
        shippers = [
            {"code": "ZTO", "name": "中通快递"},
            {"code": "YTO", "name": "圆通速递"},
            {"code": "YD", "name": "韵达速递"},
            {"code": "STO", "name": "申通快递"},
            {"code": "SF", "name": "顺丰速运"},
            {"code": "JD", "name": "京东快递"},
            {"code": "YZPY", "name": "邮政快递包裹"},
            {"code": "EMS", "name": "EMS"},
            {"code": "JTSD", "name": "极兔速递"},
            {"code": "DBL", "name": "德邦快递"},
            {"code": "FWX", "name": "丰网速运"},
            {"code": "HTKY", "name": "百世快递"},
            {"code": "DNWL", "name": "东骏快捷物流"},
            {"code": "FEDEX", "name": "FEDEX联邦（国内）"},
            {"code": "RRS", "name": "日日顺物流"},
            {"code": "ANEKY", "name": "安能快运/物流"},
            {"code": "ZTOKY", "name": "中通快运"},
            {"code": "ANE", "name": "安能快递"},
            {"code": "SX", "name": "顺心捷达"},
            {"code": "BTWL", "name": "百世快运"},
            {"code": "XFEX", "name": "信丰物流"},
            {"code": "YMDD", "name": "壹米滴答"},
            {"code": "JGSD", "name": "京广速递"},
            {"code": "DBLKY", "name": "德邦快运/德邦物流"},
            {"code": "KYSY", "name": "跨越速运"},
            {"code": "JDKY", "name": "京东快运"},
            {"code": "YDKY", "name": "韵达快运"},
            {"code": "TJS", "name": "特急送"},
            {"code": "UPS", "name": "UPS"},
            {"code": "YAD", "name": "源安达快递"},
            {"code": "ANNTO", "name": "安得物流"},
            {"code": "LHT", "name": "联昊通速递"},
            {"code": "ZJS", "name": "宅急送"},
            {"code": "YF", "name": "耀飞快递"},
            {"code": "USPS", "name": "USPS美国邮政"},
            {"code": "DHL", "name": "DHL-中国件"},
            {"code": "FASTGO", "name": "速派快递"},
            {"code": "HSSY", "name": "汇森速运"},
            {"code": "JYM", "name": "加运美"},
            {"code": "ZTOGLOBAL", "name": "中通国际"},
            {"code": "UC", "name": "优速快递"},
            {"code": "HOAU", "name": "天地华宇"},
            {"code": "TNJEX", "name": "明通国际快递"},
            {"code": "DPDUK", "name": "DPD(UK)"},
            {"code": "DSWL", "name": "D速物流"},
            {"code": "EWE", "name": "EWE"},
            {"code": "SHWL", "name": "盛辉物流"},
            {"code": "YJWL", "name": "云聚物流"},
            {"code": "ZY_FY", "name": "飞洋快递"},
            {"code": "YXWL", "name": "宇鑫物流"},
            {"code": "PADTF", "name": "平安达腾飞快递"},
            {"code": "ZYE", "name": "众邮快递"},
            {"code": "UBONEX", "name": "优邦国际速运"},
            {"code": "ZHONGTIEWULIU", "name": "中铁飞豹"},
            {"code": "HDWL", "name": "宏递快运"},
            {"code": "CRAZY", "name": "疯狂快递"},
            {"code": "STWL", "name": "速腾快递"},
            {"code": "CTWL", "name": "长通物流"},
            {"code": "PANEX", "name": "泛捷快递"},
            {"code": "LB", "name": "龙邦快递"},
            {"code": "BETWL", "name": "百腾物流"},
            {"code": "AUEXPRESS", "name": "澳邮中国快运AuExpress"},
            {"code": "ESDEX", "name": "卓志速运"},
            {"code": "SFWL", "name": "盛丰物流"},
            {"code": "JP", "name": "日本邮政"},
            {"code": "ZY100", "name": "中远快运"},
            {"code": "HTB56", "name": "徽托邦物流"},
            {"code": "YBG", "name": "洋包裹"},
            {"code": "ZTWL", "name": "中铁物流"},
            {"code": "ZHONGHUAN", "name": "中环国际快递"},
            {"code": "HTWL", "name": "鸿泰物流"},
            {"code": "BCTWL", "name": "百城通物流"},
            {"code": "SNWL", "name": "苏宁物流"},
            {"code": "TU", "name": "运联科技"},
            {"code": "TBZS", "name": "特宝专送"},
            {"code": "FTD", "name": "富腾达"},
            {"code": "JIUYE", "name": "九曳供应链"},
            {"code": "CSTD", "name": "畅顺通达"},
            {"code": "HISENSE", "name": "海信物流"},
            {"code": "AUODEXPRESS", "name": "澳德物流"},
            {"code": "GJYZBG", "name": "国际邮政包裹"},
            {"code": "YLFWL", "name": "一路发物流"},
            {"code": "WHXBWL", "name": "武汉晓毕物流"},
            {"code": "YSDF", "name": "余氏东风"},
            {"code": "JAD", "name": "捷安达"},
            {"code": "AUEX", "name": "澳货通"},
            {"code": "SUBIDA", "name": "速必达物流"},
            {"code": "SYJWDX", "name": "佳旺达物流"},
            {"code": "ROYALMAIL", "name": "RoyalMail"},
            {"code": "FZGJ", "name": "方舟国际速递"},
            {"code": "XJ", "name": "新杰物流"},
            {"code": "TNT", "name": "TNT国际快递"},
            {"code": "SENDCN", "name": "速递中国"},
            {"code": "EMSBG", "name": "EMS包裹"},
            {"code": "DTWL", "name": "大田物流"},
            {"code": "D4PX", "name": "递四方速递"},
            {"code": "CJKOREAEXPRESS", "name": "大韩通运"},
            {"code": "JGWL", "name": "景光物流"},
            {"code": "CJEXPRESS", "name": "长江国际速递"},
            {"code": "CITY56", "name": "城市映急"},
            {"code": "CHT361", "name": "诚和通"},
            {"code": "ONEEXPRESS", "name": "一速递"},
            {"code": "XDEXPRESS", "name": "迅达速递"},
            {"code": "BN", "name": "笨鸟国际"},
            {"code": "NSF", "name": "新顺丰国际速递"},
            {"code": "EPOST", "name": "韩国邮政"},
            {"code": "JUMSTC", "name": "聚盟共建"},
            {"code": "TAQBINJP", "name": "Yamato宅急便"},
            {"code": "A4PX", "name": "转运四方"},
            {"code": "DEKUN", "name": "德坤"},
            {"code": "COE", "name": "COE东方快递"},
            {"code": "DFWL", "name": "达发物流"},
            {"code": "TZKY", "name": "铁中快运"},
            {"code": "LYT", "name": "联运通物流"},
            {"code": "DHLGLOBALLOGISTICS", "name": "DHL全球货运"},
            {"code": "SWEDENPOST", "name": "瑞典邮政"},
            {"code": "BEEBIRD", "name": "锋鸟物流"},
            {"code": "CFWL", "name": "春风物流"},
            {"code": "JYWL", "name": "佳怡物流"},
            {"code": "XYJ", "name": "西邮寄"},
            {"code": "LINGSONG", "name": "领送送"},
            {"code": "SJA56", "name": "四季安物流"},
            {"code": "WTP", "name": "微特派"},
            {"code": "HAOXIANGWULIU", "name": "豪翔物流"},
            {"code": "HCT", "name": "新竹物流HCT"},
            {"code": "SUYD56", "name": "速邮达物流"},
            {"code": "YBWL", "name": "优拜物流"},
            {"code": "COSCO", "name": "中远e环球"},
            {"code": "GOEX", "name": "时安达速递"},
            {"code": "IADLYYZ", "name": "澳大利亚邮政"},
            {"code": "LHTEX", "name": "联昊通"},
            {"code": "LNET", "name": "新易泰"},
            {"code": "WJWL", "name": "万家物流"},
            {"code": "AX", "name": "安迅物流"},
            {"code": "CCES", "name": "CCES/国通快递"},
            {"code": "DPD", "name": "DPD"},
            {"code": "FAMIPORT", "name": "全家快递"},
            {"code": "HJWL", "name": "汇捷物流"},
            {"code": "HNTLWL", "name": "泰联物流"},
            {"code": "HQSY", "name": "环球速运"},
            {"code": "JTEXPRESS", "name": "J&TExpress"},
            {"code": "KEJIE", "name": "科捷物流"},
            {"code": "KZWL", "name": "科紫物流"},
            {"code": "MHKD", "name": "民航快递"},
            {"code": "SHPOST", "name": "同城快寄"},
            {"code": "SINGAPOREPOST", "name": "新加坡邮政"},
            {"code": "SINGAPORESPEEDPOST", "name": "新加坡特快专递"},
            {"code": "STSD", "name": "三态速递"},
            {"code": "UPSEN", "name": "UPS-全球件"},
            {"code": "WJK", "name": "万家康"},
            {"code": "XCWL", "name": "迅驰物流"},
            {"code": "XLOBO", "name": "贝海国际速递"},
            {"code": "YYSD", "name": "优优速递"}
        ]
        
        return {
            "title": "单号识别支持的快递公司",
            "description": "快递鸟单号识别接口支持的快递公司列表",
            "shippers": shippers
        }
        
    def _get_cross_border_tracking_doc(self) -> CrossBorderTrackingDocInfo:
        """获取跨境小包查询文档信息"""
        return CrossBorderTrackingDocInfo(
            request_type="8001(跨境小包即时查询)/8002(跨境小包订阅查询)",
            batch_support="不支持，并发20次/秒",
            billing_rule="8001: 40个自然日内同一(物流编码+单号)不限查询次数，计费1单；查询无轨迹不计费\n8002: 按请求成功次数计算，返回无轨迹不做计费",
            api_url="https://api.kdniao.com/api/dist",
            supported_companies="支持查询国际快递公司轨迹：DHL、UPS、FEDEX、FEDEXCN、TNT、ARAMEX、USPS",
            special_requirements=[
                "跨境小包查询需要提供正确的国际快递公司编码",
                "部分国际快递公司可能需要额外的验证信息",
                "查询结果包含国际物流状态和清关信息"
            ],
            request_params={
                "ShipperCode": {
                    "type": "String(10)",
                    "required": True,
                    "description": "国际快递公司编码"
                },
                "LogisticCode": {
                    "type": "String(30)",
                    "required": True,
                    "description": "国际快递单号"
                },
                "OrderCode": {
                    "type": "String(30)",
                    "required": False,
                    "description": "订单编号"
                }
            },
            response_params={
                "EBusinessID": {
                    "type": "String(10)",
                    "required": True,
                    "description": "用户ID"
                },
                "ShipperCode": {
                    "type": "String(10)",
                    "required": True,
                    "description": "国际快递公司编码"
                },
                "LogisticCode": {
                    "type": "String(30)",
                    "required": True,
                    "description": "国际快递单号"
                },
                "Success": {
                    "type": "Bool",
                    "required": True,
                    "description": "成功与否(true/false)"
                },
                "State": {
                    "type": "String(2)",
                    "required": True,
                    "description": "物流状态：0-暂无轨迹，1-已揽收，2-在途中，3-已签收，4-问题件，5-转寄，6-清关"
                },
                "Traces": {
                    "type": "Array",
                    "required": False,
                    "description": "轨迹明细数组"
                }
            }
        )
    
    def _get_service_point_doc(self) -> ServicePointDocInfo:
        """获取网点查询文档信息"""
        return ServicePointDocInfo(
            request_type="6002",
            batch_support="不支持批量，可并发",
            billing_rule="按请求成功次数计费，请求失败不计费",
            sort_rule="不适用",
            api_url="https://api.kdniao.com/api/dist",
            supported_companies="支持顺丰(SF)、极兔速递(JTSD)等快递公司",
            special_requirements=[
                "必须提供快递公司编码(ShipperCode)",
                "必须提供省份名称(ProvinceName)",
                "可选提供城市名称(CityName)、区县名称(AreaName)、详细地址(Address)",
                "支持精确查询和模糊查询"
            ],
            request_params={
                "ShipperCode": {
                    "type": "String(10)",
                    "required": True,
                    "description": "快递公司编码，如SF(顺丰)、JTSD(极兔速递)"
                },
                "ProvinceName": {
                    "type": "String(20)",
                    "required": True,
                    "description": "省份名称"
                },
                "CityName": {
                    "type": "String(20)",
                    "required": False,
                    "description": "城市名称"
                },
                "AreaName": {
                    "type": "String(20)",
                    "required": False,
                    "description": "区县名称"
                },
                "Address": {
                    "type": "String(200)",
                    "required": False,
                    "description": "详细地址，用于精确查询"
                }
            },
            response_params={
                "EBusinessID": {
                    "type": "String(10)",
                    "required": True,
                    "description": "用户ID"
                },
                "Success": {
                    "type": "Bool(10)",
                    "required": True,
                    "description": "成功与否(true/false)"
                },
                "Reason": {
                    "type": "String(50)",
                    "required": False,
                    "description": "失败原因"
                },
                "ServicePointInfos": {
                    "type": "Array",
                    "required": False,
                    "description": "网点信息数组"
                },
                "ServicePointInfos[].ServicePointName": {
                    "type": "String(100)",
                    "required": False,
                    "description": "网点名称"
                },
                "ServicePointInfos[].ServicePointCode": {
                    "type": "String(50)",
                    "required": False,
                    "description": "网点编码"
                },
                "ServicePointInfos[].Address": {
                    "type": "String(200)",
                    "required": False,
                    "description": "网点地址"
                },
                "ServicePointInfos[].Phone": {
                    "type": "String(50)",
                    "required": False,
                    "description": "联系电话"
                },
                "ServicePointInfos[].Province": {
                    "type": "String(20)",
                    "required": False,
                    "description": "省份"
                },
                "ServicePointInfos[].City": {
                    "type": "String(20)",
                    "required": False,
                    "description": "城市"
                },
                "ServicePointInfos[].Area": {
                    "type": "String(20)",
                    "required": False,
                    "description": "区县"
                }
            }
        )
    
    def _get_cross_border_state_codes(self) -> List[StateCodeInfo]:
        """获取跨境小包状态码信息"""
        return [
            StateCodeInfo(code="0", name="暂无轨迹信息", description="暂时没有物流轨迹信息"),
            StateCodeInfo(code="1", name="已揽收", description="快递公司已收取包裹"),
            StateCodeInfo(code="2", name="在途中", description="包裹正在运输途中"),
            StateCodeInfo(code="201", name="到达派件城市", description="包裹已到达目的城市"),
            StateCodeInfo(code="202", name="派件中", description="正在进行派送"),
            StateCodeInfo(code="204", name="到达转运中心", description="包裹已到达转运中心"),
            StateCodeInfo(code="205", name="到达派件网点", description="包裹已到达派送网点"),
            StateCodeInfo(code="206", name="寄件网点发件", description="从寄件网点发出"),
            StateCodeInfo(code="3", name="已签收", description="包裹已成功签收"),
            StateCodeInfo(code="301", name="正常签收", description="正常情况下的签收"),
            StateCodeInfo(code="302", name="异常后最终签收", description="经过异常处理后最终签收"),
            StateCodeInfo(code="304", name="代收签收", description="他人代为签收"),
            StateCodeInfo(code="4", name="问题件", description="包裹出现问题"),
            StateCodeInfo(code="401", name="发货无信息", description="发货后无物流信息"),
            StateCodeInfo(code="402", name="超时未签收", description="超过预期时间未签收"),
            StateCodeInfo(code="403", name="超时未更新", description="物流信息长时间未更新"),
            StateCodeInfo(code="404", name="拒收（退件）", description="收件人拒收，包裹退回"),
            StateCodeInfo(code="405", name="派件异常", description="派件异常"),
            StateCodeInfo(code="5", name="转寄", description="包裹被转寄到其他地址"),
            StateCodeInfo(code="6", name="清关", description="国际包裹清关状态"),
            StateCodeInfo(code="601", name="待清关", description="等待海关清关"),
            StateCodeInfo(code="602", name="清关中", description="正在进行清关手续"),
            StateCodeInfo(code="603", name="已清关", description="清关手续已完成"),
            StateCodeInfo(code="604", name="清关异常", description="清关过程中出现异常")
        ]