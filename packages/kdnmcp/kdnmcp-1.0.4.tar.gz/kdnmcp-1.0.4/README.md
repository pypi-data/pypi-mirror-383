# 快递鸟物流服务 - KDNiao Logistics MCP Service

基于快递鸟API的MCP服务，为AI助手提供物流查询、单号识别、时效预估、地址解析、网点查询和跨境物流查询功能。

## 功能特性

- **物流轨迹查询**：支持100+快递公司的实时物流轨迹查询
- **智能单号识别**：自动识别快递单号对应的快递公司
- **时效预估**：预估快递配送时间和路线
- **智能地址解析**：解析完整地址信息，拆分省市区街道、姓名、电话等
- **网点查询**：查询快递公司在指定地区的服务网点信息
- **跨境物流查询**：支持国际快递的物流轨迹查询，包含清关状态

## 快速开始

### 1. 安装

```bash
git clone <repository-url>
cd mcptrae
pip install -r requirements.txt
```

### 2. 获取API密钥

1. 访问 [快递鸟官网](https://www.kdniao.com/) 注册账户
2. 获取 `EBusinessID` 和 `APIKey`

### 3. 启动服务

**MCP客户端配置**：
```json
{
  "mcpServers": {
    "kdniao-mcp": {
      "command": "python",
      "args": ["-m", "kdnmcp.main"],
      "env": {
        "EBUSINESS_ID": "your_ebusiness_id",
        "API_KEY": "your_api_key"
      }
    }
  }
}
```

**直接启动**：
```bash
# Stdio模式（推荐）
EBUSINESS_ID=your_id API_KEY=your_key python -m kdnmcp.main

# Web模式
python -m kdnmcp.main --transport http --port 8000
```

## 可用工具

### 1. 物流轨迹查询 (track_logistics)
查询快递包裹的实时物流轨迹信息。

**参数：**
- `logistic_code` (必需): 快递单号
- `shipper_code` (可选): 快递公司编码
- `mobile` (可选): 手机号后四位（顺丰需要）

### 2. 单号识别 (recognize_logistics_code)
自动识别快递单号对应的快递公司。

**参数：**
- `logistic_code` (必需): 快递单号

### 3. 时效预估 (estimate_delivery_time)
预估快递配送时间和路线信息。

**参数：**
- `shipper_code` (必需): 快递公司编码
- `send_province/city/area` (必需): 发件地址
- `receive_province/city/area` (必需): 收件地址
- `logistic_code` (可选): 快递单号

### 4. 智能地址解析 (parse_address)
解析完整地址信息，拆分为省市区街道、姓名、电话等。

**参数：**
- `content` (必需): 待识别的完整地址

### 5. 网点查询 (query_service_points)
查询快递公司在指定地区的服务网点信息。

**参数：**
- `shipper_code` (必需): 快递公司编码
- `province_name` (必需): 省份名称
- `city_name/area_name` (可选): 城市/区县名称
- `address` (可选): 地址关键词（顺丰和极兔必填）

### 6. 跨境物流查询 (track_cross_border_logistics)
查询国际快递的物流轨迹信息，支持清关状态。

**参数：**
- `shipper_code` (必需): 物流公司编码
- `logistic_code` (必需): 快递单号
- `order_code` (可选): 订单编号

## 支持的快递公司

支持100+快递公司，主要包括：顺丰(SF)、圆通(YTO)、中通(ZTO)、申通(STO)、韵达(YD)、极兔(JTSD)、京东(JD)、邮政EMS、德邦(DBL)、百世(HTKY)等。

## 常见问题

**API认证失败**
- 检查 `EBUSINESS_ID` 和 `API_KEY` 是否正确
- 确认快递鸟账户状态正常

**参数验证错误**
- 检查快递公司编码是否正确
- 验证快递单号格式

**调试模式**
```bash
EBUSINESS_ID=your_id API_KEY=your_key python -m kdnmcp.main --debug
```

## 许可证

MIT License

---

*由快递鸟(www.kdniao.com)提供技术支持*