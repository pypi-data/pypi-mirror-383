# AKShare MCP Server

A Model Context Protocol (MCP) server for accessing Chinese stock market data via [AKShare](https://github.com/akfamily/akshare).

## 功能特性

- 🏢 **市场总览**: 获取上海、深圳交易所市场统计数据
- 📈 **个股查询**: 雪球、东方财富等平台个股实时行情
- 📊 **历史数据**: A股历史K线、分时数据
- 🔍 **行业分析**: 行业成交、地区交易排行
- 💰 **融资融券**: 融资融券统计数据
- 📋 **行情报价**: 五档买卖盘口数据

## 安装

```bash
pip install akshare-mcp
```

## 使用方法

### 命令行启动

```bash
akshare-mcp
```

### 作为 MCP 客户端使用

在支持 MCP 的应用（如 Claude Desktop）中配置：

```json
{
  "mcpServers": {
    "akshare": {
      "command": "akshare-mcp"
    }
  }
}
```

### Python 代码中使用

```python
from akshare_mcp import mcp

# 启动服务器
mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")
```

## 可用工具

### 市场总貌
- `get_stock_sse_summary`: 上交所股票数据总貌
- `get_stock_szse_summary`: 深交所证券类别统计
- `get_stock_market_overview`: 中国股票市场总貌

### 个股信息
- `get_stock_info_xueqiu`: 雪球个股实时行情
- `get_stock_bid_ask`: 东方财富行情报价

### 历史数据
- `get_stock_a_hist`: A股历史K线数据
- `get_stock_a_realtime`: A股实时行情
- `get_stock_intraday_em`: 东方财富分时数据

### 行业分析
- `get_stock_szse_area_summary`: 深交所地区交易排行
- `get_stock_szse_sector_summary`: 深交所股票行业成交
- `get_stock_a_industry_comparison`: A股行业对比数据

### 其他数据
- `get_stock_a_dividend_yield`: A股股息率数据
- `get_stock_margin_data`: 融资融券数据
- `get_stock_sse_deal_daily`: 上交所每日股票情况

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src/
ruff check src/
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [AKShare 官方文档](https://akshare.akfamily.xyz/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)