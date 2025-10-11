# AKShare MCP 服务器

一个用于通过 [AKShare](https://github.com/akfamily/akshare) 访问中国股票市场数据的模型上下文协议（MCP）服务器。

## 功能特性

- 🏢 **市场总览**: 获取上海、深圳交易所市场统计数据
- 🏢 **个股信息**: 东方财富个股信息、雪球财经公司概况
- 🏭 **行业板块**: 行业板块数据、实时行情、成份股信息
- 🔥 **股票热度**: A股人气排行榜、雪球交易排行榜
- 📈 **实时行情**: 沪深京A股实时行情、个股报价、涨停股池
- 📊 **历史数据**: A股历史K线、腾讯证券历史数据、分时行情
- 💰 **基本面分析**: 财务指标、盈利预测、信息披露公告
- 📈 **资金流向**: 龙虎榜详情、个股资金流向、机构参与度
- 📰 **新闻资讯**: 全球财经快讯、富途牛牛快讯
- 📊 **同行比较**: 估值比较、成长性比较
- 🔧 **辅助工具**: 股票代码查询、交易日历、内部交易数据、个股研报

## 安装

```bash
pip install akshare-tools
```

## 使用方法

### 使用 MCP Inspector

MCP Inspector 是一个用于测试和调试 MCP 服务器的命令行工具：

```bash
npx @modelcontextprotocol/inspector uvx akshare-tools
```

### 作为 MCP 客户端使用

在支持 MCP 的应用（如 Claude Desktop）中配置：

```json
{
    "mcpServers": {
      "akshare-mcp": {
        "command": "uvx",
        "args": [
          "akshare-tools"
        ]
      }
    }
}
```

## 可用工具

### 📊 股票市场总貌
- `get_stock_sse_summary`: 上海证券交易所股票数据总貌
- `get_stock_szse_summary`: 深圳证券交易所市场总貌-证券类别统计

### 🏢 个股信息
- `get_stock_individual_info_em`: 东方财富-个股-股票信息
- `get_stock_individual_basic_info_xq`: 雪球财经-个股-公司概况-公司简介

### 🏭 行业板块
- `get_stock_board_industry_name_em`: 东方财富-沪深京板块-行业板块数据
- `get_stock_board_industry_spot_em`: 东方财富网-沪深板块-行业板块-实时行情数据
- `get_stock_board_industry_cons_em`: 东方财富-沪深板块-行业板块-板块成份股数据

### 🔥 股票热度
- `get_stock_hot_rank_em`: 东方财富网站-股票热度-人气榜数据
- `get_stock_hot_deal_xq`: 雪球-沪深股市-热度排行榜-交易排行榜数据

### 📈 实时行情
- `get_stock_zh_a_spot_em`: 沪深京A股实时行情数据
- `get_stock_info_xueqiu`: 雪球个股实时市场数据信息
- `get_stock_zt_pool_em`: 东方财富网-涨停股池数据

### 📊 历史数据
- `get_stock_a_hist`: A股历史K线数据
- `get_stock_zh_a_hist_tx`: 腾讯证券-日频-股票历史数据
- `get_stock_zh_a_hist_min_em`: 东方财富网-沪深京A股-每日分时行情数据

### 💰 基本面分析
- `get_stock_financial_analysis_indicator`: 新浪财经-财务分析-财务指标数据
- `get_stock_profit_forecast_em`: 东方财富网-数据中心-研究报告-盈利预测
- `get_stock_zh_a_disclosure_report_cninfo`: 巨潮资讯网-信息披露公告

### 📈 资金流向
- `get_stock_lhb_detail_em`: 东方财富网-数据中心-龙虎榜单-龙虎榜详情
- `get_stock_individual_fund_flow`: 东方财富网-数据中心-个股资金流向
- `get_stock_comment_detail_zlkp_jgcyd_em`: 东方财富网-数据中心-特色数据-千股千评-主力控盘-机构参与度数据

### 📰 新闻资讯
- `get_stock_info_global_em`: 东方财富-全球财经快讯
- `get_stock_info_global_futu`: 富途牛牛-快讯

### 📊 同行比较
- `get_stock_zh_valuation_comparison_em`: 东方财富-行情中心-同行比较-估值比较数据
- `get_stock_zh_growth_comparison_em`: 东方财富-行情中心-同行比较-成长性比较数据

### 🔧 辅助工具
- `get_stock_info_a_code_name`: 沪深京A股股票代码和股票简称数据（支持公司名称模糊匹配）
- `get_tool_trade_date_hist_sina`: 新浪财经-股票交易日历数据
- `get_stock_inner_trade_xq`: 雪球-行情中心-沪深股市-内部交易数据
- `get_stock_research_report_em`: 东方财富网-数据中心-研究报告-个股研报数据

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

---
*Language: [English](README.md) | [中文](README_CN.md)*