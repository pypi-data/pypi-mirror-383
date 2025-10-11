# AKShare MCP Server

A Model Context Protocol (MCP) server for accessing Chinese stock market data via [AKShare](https://github.com/akfamily/akshare).

## 功能特性

- 🏢 **市场总览**: 获取上海、深圳交易所市场统计数据
- 📈 **实时行情**: 沪深京A股实时行情、个股报价、涨停股池
- 📊 **历史数据**: A股历史K线、分时数据、历史分时行情
- 💰 **基本面分析**: 财务指标、盈利预测、信息披露公告
- 📈 **技术分析**: 龙虎榜详情、个股资金流向
- 📰 **新闻资讯**: 全球财经快讯、市场动态
- 🔧 **辅助工具**: 股票代码查询、交易日历

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

### 📈 实时行情
- `get_stock_zh_a_spot_em`: 沪深京A股实时行情数据
- `get_stock_info_xueqiu`: 雪球个股实时市场数据信息
- `get_stock_zt_pool_em`: 东方财富网-涨停股池数据

### 📊 历史数据
- `get_stock_a_hist`: A股历史K线数据
- `get_stock_zh_a_hist_min_em`: 东方财富网-沪深京A股-每日分时行情数据

### 💰 基本面分析
- `get_stock_financial_analysis_indicator`: 新浪财经-财务分析-财务指标数据
- `get_stock_profit_forecast_em`: 东方财富网-数据中心-研究报告-盈利预测
- `get_stock_zh_a_disclosure_report_cninfo`: 巨潮资讯网-信息披露公告

### 📈 技术分析
- `get_stock_lhb_detail_em`: 东方财富网-数据中心-龙虎榜单-龙虎榜详情
- `get_stock_individual_fund_flow`: 东方财富网-数据中心-个股资金流向

### 📰 新闻资讯
- `get_stock_info_global_em`: 东方财富-全球财经快讯
- `get_stock_info_global_futu`: 富途牛牛-快讯

### 🔧 辅助工具
- `get_stock_info_a_code_name`: 沪深京A股股票代码和股票简称数据
- `get_tool_trade_date_hist_sina`: 新浪财经-股票交易日历数据

## 开发

### 安装开发依赖

```bash
pip install -r requirements-dev.txt
pip install -e ".[dev]"
```

### 测试策略

项目采用分层测试策略，包含以下测试类型：

#### 1. 快速测试检查

```bash
# 检查测试覆盖率
python scripts/generate_test_skeleton.py check

# 检查测试环境
python scripts/run_tests.py check
```

#### 2. 分类测试

```bash
# 运行单元测试
python scripts/run_tests.py unit

# 运行参数验证测试
python scripts/run_tests.py validation

# 运行集成测试
python scripts/run_tests.py integration

# 运行回归测试
python scripts/run_tests.py regression

# 运行所有测试
python scripts/run_tests.py all

# 运行覆盖率测试
python scripts/run_tests.py coverage
```

#### 3. 自动生成测试用例

当添加新的工具函数后，可以自动生成测试骨架：

```bash
# 生成缺失的测试用例
python scripts/generate_test_skeleton.py generate
```

#### 4. 特定测试模式

```bash
# 运行特定模式的测试
python scripts/run_tests.py pattern "test_market"
python scripts/run_tests.py pattern "test_financial"
```

### 代码质量

```bash
# 代码格式化
black src/ tests/

# 代码检查
ruff check src/ tests/

# 类型检查
mypy src/ --ignore-missing-imports
```

### 测试结构

```
tests/
├── conftest.py              # pytest配置
├── test_server.py           # 主要测试文件
├── test_validation.py       # 参数验证测试
└── data/                    # 测试数据目录
```

### 持续集成

项目配置了GitHub Actions自动测试，每次提交都会：
- 运行所有测试用例
- 检查代码覆盖率
- 验证代码格式和风格
- 在多个Python版本下测试

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [AKShare 官方文档](https://akshare.akfamily.xyz/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)