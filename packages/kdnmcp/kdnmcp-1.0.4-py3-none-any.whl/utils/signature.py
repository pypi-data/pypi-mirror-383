"""快递鸟API签名生成工具"""

import hashlib
import base64
from urllib.parse import quote
from typing import Dict, Any
import json


def generate_signature(request_data: str, api_key: str) -> str:
    """生成快递鸟API签名
    
    Args:
        request_data: 请求数据JSON字符串
        api_key: API密钥
        
    Returns:
        Base64编码的MD5签名
    """
    # 拼接字符串：RequestData + ApiKey
    sign_str = request_data + api_key
    
    # MD5加密 - 使用hexdigest()获取十六进制字符串，与官方demo一致
    md5_hex = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    # Base64编码十六进制字符串
    signature = base64.b64encode(md5_hex.encode('utf-8')).decode('utf-8')
    
    return signature


def prepare_request_params(ebusiness_id: str, request_type: str, 
                          request_data: Dict[Any, Any], api_key: str) -> Dict[str, str]:
    """准备快递鸟API请求参数
    
    Args:
        ebusiness_id: 商户ID
        request_type: 请求类型
        request_data: 请求数据字典
        api_key: API密钥
        
    Returns:
        包含所有请求参数的字典
    """
    # 将请求数据转换为JSON字符串
    request_data_json = json.dumps(request_data, ensure_ascii=False, separators=(',', ':'))
    
    # 生成签名
    data_sign = generate_signature(request_data_json, api_key)
    
    # 准备请求参数
    params = {
        'EBusinessID': ebusiness_id,
        'RequestType': request_type,
        'RequestData': quote(request_data_json, safe=''),  # URL编码
        'DataSign': quote(data_sign, safe=''),  # URL编码
        'DataType': '2',  # 返回数据类型：2-JSON
        "request_from" : "kdniao_mcp"
    }
    
    return params


def validate_request_data(request_data: Dict[Any, Any], required_fields: list) -> bool:
    """验证请求数据完整性
    
    Args:
        request_data: 请求数据字典
        required_fields: 必需字段列表
        
    Returns:
        验证是否通过
    """
    for field in required_fields:
        if field not in request_data or not request_data[field]:
            return False
    return True


def sanitize_phone_number(phone: str) -> str:
    """处理手机号，只保留后四位
    
    Args:
        phone: 原始手机号
        
    Returns:
        后四位手机号
    """
    if not phone:
        return ""
    
    # 移除所有非数字字符
    phone_digits = ''.join(filter(str.isdigit, phone))
    
    # 返回后四位
    return phone_digits[-4:] if len(phone_digits) >= 4 else phone_digits


def format_datetime(dt_str: str) -> str:
    """格式化日期时间字符串
    
    Args:
        dt_str: 日期时间字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    if not dt_str:
        return ""
    
    try:
        from datetime import datetime
        # 尝试解析常见的日期时间格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        # 如果都不匹配，返回原字符串
        return dt_str
    except Exception:
        return dt_str