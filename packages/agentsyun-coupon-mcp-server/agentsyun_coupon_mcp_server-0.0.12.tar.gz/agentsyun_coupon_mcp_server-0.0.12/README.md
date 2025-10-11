# Agentsyun优惠券MCP服务

这是一个基于MCP协议的优惠券服务，提供多品类优惠券查询、筛选和推广链接生成功能，支持外卖、美食、休闲娱乐、酒店民宿、门票度假、医药等多个类目。

## 功能特性

- 支持6大类优惠券查询：
  - 外卖商品券
  - 美食优惠券
  - 休闲娱乐券
  - 酒店民宿券
  - 门票度假券
  - 医药券

- 提供完整的优惠券生命周期管理：
  - 优惠券列表查询
  - 推广链接生成（支持多种链接类型）

## 环境要求

- Python >= 3.12
- 环境变量配置：
  - [APP_KEY](file://D:\pyProject\huizhi_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L33-L33): 应用Key
  - [APP_SECRET](file://D:\pyProject\huizhi_coupon_mcp_server\agentsyun_coupon_mcp_server\server.py#L34-L34): 应用密钥

## 安装方式

```bash
pip install agentsyun-coupon-mcp-server
```

## API接口说明

### 优惠券列表查询

1. `list_takeaway_coupons` - 外卖商品券列表
2. `list_restaurant_coupons` - 美食优惠券列表
3. `list_entertainment_coupons` - 休闲娱乐券列表
4. `list_hotel_coupons` - 酒店民宿券列表
5. `list_travel_coupons` - 门票度假券列表
6. `list_medical_coupons` - 医药券列表

### 推广链接生成

1. `get_takeaway_promotion_link` - 外卖商品券推广链接
2. `get_restaurant_promotion_link` - 美食优惠券推广链接
3. `get_entertainment_promotion_link` - 休闲娱乐券推广链接
4. `get_hotel_promotion_link` - 酒店民宿券推广链接
5. `get_travel_promotion_link` - 门票度假券推广链接
6. `get_medical_promotion_link` - 医药券推广链接

## 配置说明

- 支持美团渠道优惠券
- 支持MCP通道推广链接生成
- 所有请求均需签名验证

## 传输方式

## 传输方式配置

服务支持三种传输方式：stdio（默认）、sse 和 streamable-http。

### stdio 传输（默认）
直接在客户端配置如下MCP Server即可。

```json
{
    "mcpServers": {
        "agentsyun-coupon-mcp-server": {
            "command": "agentsyun-coupon-mcp-server",
            "env": {
                "APP_KEY": "your_app_key",
                "APP_SECRET": "your_app_secret"
            }
        }
    }
}
```


### SSE 传输
SSE传输支持实时数据推送，适合远程部署MCP Server。

本地以SSE运行服务：
```bash
export APP_KEY=你的应用Key
export APP_SECRET=你的应用密钥
agentsyun-coupon-mcp-server sse
```

```cmd
set APP_KEY=你的应用Key
set APP_SECRET=你的应用密钥
agentsyun-coupon-mcp-server sse
```

```PowerShell
$env:APP_KEY="你的应用Key"
$env:APP_SECRET="你的应用密钥"
agentsyun-coupon-mcp-server sse
```


MCP客户端配置：
```json
{
    "mcpServers": {
        "agentsyun-coupon-mcp-server": {
            "url": "http://localhost:8000/sse",
            "env": {
                "APP_KEY": "your_app_key",
                "APP_SECRET": "your_app_secret"
            }
        }
    }
}
```


### Streamable HTTP 传输
本地以Streamable HTTP运行服务：
```bash
export APP_KEY=你的应用Key
export APP_SECRET=你的应用密钥
agentsyun-coupon-mcp-server streamable-http
```


MCP客户端配置：
```json
{
    "mcpServers": {
        "agentsyun-coupon-mcp-server": {
            "url": "http://localhost:8000/mcp",
            "env": {
                "APP_KEY": "your_app_key",
                "APP_SECRET": "your_app_secret"
            }
        }
    }
}
```


## 依赖项
- mcp
- requests>=2.32.5
- annotated>=0.0.2
