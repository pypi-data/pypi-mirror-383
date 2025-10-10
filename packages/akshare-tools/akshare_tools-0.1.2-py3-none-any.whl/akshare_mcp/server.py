from fastmcp import FastMCP
import akshare as ak

mcp = FastMCP("akshare")

# ===================== 股票市场总貌 ===================== #

@mcp.tool
def get_stock_sse_summary() -> str:
    """获取上海证券交易所股票数据总貌

    Returns:
        str: 上交所股票数据总貌的JSON格式字符串，包含流通股本、总市值、平均市盈率、上市公司数、流通市值等统计信息
    """
    try:
        df = ak.stock_sse_summary()
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取上交所股票数据总貌失败: {str(e)}"

@mcp.tool
def get_stock_szse_summary(date: str = "") -> str:
    """获取深圳证券交易所市场总貌-证券类别统计
    
    Args:
        date (str): 查询日期，格式："20200619"，为空则查询最新数据
    
    Returns:
        str: 深交所证券类别统计数据的JSON格式字符串，包含股票、基金、债券等各类证券的数量、成交金额、总市值、流通市值等
    """
    try:
        if not date:
            # 如果没有指定日期，使用今天
            from datetime import datetime
            date = datetime.now().strftime("%Y%m%d")
        
        df = ak.stock_szse_summary(date=date)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取深交所股票数据总貌失败: {str(e)}"

# ===================== 实时行情 ===================== #

@mcp.tool
def get_stock_zh_a_spot_em() -> str:
    """获取沪深京A股实时行情数据

    Returns:
        str: 沪深京A股实时行情数据的JSON格式字符串，包含所有上市公司的最新价、涨跌幅、成交量、市值等信息
    """
    try:
        df = ak.stock_zh_a_spot_em()
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取沪深京A股实时行情数据失败: {str(e)}"

@mcp.tool
def get_stock_info_xueqiu(symbol: str) -> str:
    """获取雪球个股实时市场数据信息
    
    Args:
        symbol (str): 股票代码，例如："SH601318"(中国平安)
    
    Returns:
        str: 个股信息的JSON格式字符串，包含实时价格、涨跌幅、成交量等数据
    """
    try:
        df = ak.stock_individual_spot_xq(symbol=symbol)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取雪球个股信息失败: {str(e)}"

@mcp.tool
def get_stock_zt_pool_em(date: str = "") -> str:
    """获取东方财富网-涨停股池数据
    
    Args:
        date (str): 查询日期，格式："20241008"，为空则查询最新数据
    
    Returns:
        str: 涨停股池数据的JSON格式字符串，包含涨停股票的序号、代码、名称、涨跌幅、最新价、成交额、流通市值、总市值、换手率、封板资金、首次封板时间、最后封板时间、炸板次数、涨停统计、连板数、所属行业等信息
    """
    try:
        if not date:
            # 如果没有指定日期，使用今天
            from datetime import datetime
            date = datetime.now().strftime("%Y%m%d")
        
        df = ak.stock_zt_pool_em(date=date)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取涨停股池数据失败: {str(e)}"

# ===================== 历史行情 ===================== #

@mcp.tool
def get_stock_a_hist(symbol: str, period: str = "daily", start_date: str = "", end_date: str = "",
                     adjust: str = "") -> str:
    """获取A股历史K线数据

    Args:
        symbol (str): 股票代码，例如："000001"(平安银行)
        period (str): 周期，可选 "daily"(日线), "weekly"(周线), "monthly"(月线)
        start_date (str): 开始日期，格式："20220101"
        end_date (str): 结束日期，格式："20221231"
        adjust (str): 复权方式，""不复权，"qfq"前复权，"hfq"后复权

    Returns:
        str: A股历史数据的JSON格式字符串，包含日期、开盘价、收盘价、最高价、最低价、成交量等信息
    """
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取A股历史数据失败: {str(e)}"

@mcp.tool
def get_stock_zh_a_hist_min_em(symbol: str, start_date: str = "", end_date: str = "", period: str = "5",
                               adjust: str = "") -> str:
    """获取东方财富网-沪深京A股-每日分时行情数据

    Args:
        symbol (str): 股票代码，例如："000001"
        start_date (str): 开始日期时间，格式："2024-03-20 09:30:00"，为空则返回所有数据
        end_date (str): 结束日期时间，格式："2024-03-20 15:00:00"，为空则返回所有数据
        period (str): 时间周期，可选："1", "5", "15", "30", "60"，其中1分钟数据只返回近5个交易日数据且不复权
        adjust (str): 复权方式，可选：""(不复权), "qfq"(前复权), "hfq"(后复权)，其中1分钟数据只返回近5个交易日数据且不复权

    Returns:
        str: 分时行情数据的JSON格式字符串，1分钟数据包含时间、开盘、收盘、最高、最低、成交量、成交额、均价；其他周期数据还包含涨跌幅、涨跌额、振幅、换手率等信息
    """
    try:
        df = ak.stock_zh_a_hist_min_em(symbol=symbol, start_date=start_date, end_date=end_date, period=period,
                                       adjust=adjust)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取A股历史分时数据失败: {str(e)}"

# ===================== 基本面 ===================== #

@mcp.tool
def get_stock_financial_analysis_indicator(symbol: str, start_year: str = "2020") -> str:
    """获取新浪财经-财务分析-财务指标数据
    
    Args:
        symbol (str): 股票代码，例如："600004"
        start_year (str): 开始查询的时间，例如："2020"
    
    Returns:
        str: 财务指标数据的JSON格式字符串，包含日期、摊薄每股收益、加权每股收益、每股净资产、总资产利润率、主营业务利润率、净资产收益率、应收账款周转率、流动比率、资产负债率等86项财务指标
    """
    try:
        df = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=start_year)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取财务指标数据失败: {str(e)}"

@mcp.tool
def get_stock_profit_forecast_em(symbol: str = "") -> str:
    """获取东方财富网-数据中心-研究报告-盈利预测数据
    
    Args:
        symbol (str): 股票代码或行业板块，默认为获取全部数据；例如："船舶制造"，行业板块可以通过 ak.stock_board_industry_name_em() 接口获取
    
    Returns:
        str: 盈利预测数据的JSON格式字符串，包含序号、代码、名称、研报数、机构投资评级（买入、增持、中性、减持、卖出）、各年度预测每股收益等信息
    """
    try:
        df = ak.stock_profit_forecast_em(symbol=symbol)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取东方财富盈利预测数据失败: {str(e)}"

@mcp.tool
def get_stock_zh_a_disclosure_report_cninfo(symbol: str, market: str = "沪深京", keyword: str = "", 
                                          category: str = "", start_date: str = "", end_date: str = "") -> str:
    """获取巨潮资讯网-信息披露公告数据
    
    Args:
        symbol (str): 股票代码，例如："000001"
        market (str): 市场类型，可选："沪深京", "港股", "三板", "基金", "债券", "监管", "预披露"
        keyword (str): 关键词搜索，默认为空字符串
        category (str): 公告类别，可选：'年报', '半年报', '一季报', '三季报', '业绩预告', '权益分派', '董事会', '监事会', '股东大会', '日常经营', '公司治理', '中介报告', '首发', '增发', '股权激励', '配股', '解禁', '公司债', '可转债', '其他融资', '股权变动', '补充更正', '澄清致歉', '风险提示', '特别处理和退市', '退市整理期'
        start_date (str): 开始日期，格式："20230618"
        end_date (str): 结束日期，格式："20231219"
    
    Returns:
        str: 信息披露公告数据的JSON格式字符串，包含代码、简称、公告标题、公告时间、公告链接等信息
    """
    try:
        df = ak.stock_zh_a_disclosure_report_cninfo(symbol=symbol, market=market, keyword=keyword, 
                                                   category=category, start_date=start_date, end_date=end_date)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取信息披露公告数据失败: {str(e)}"

# ===================== 资金流向 ===================== #

@mcp.tool
def get_stock_lhb_detail_em(start_date: str, end_date: str) -> str:
    """获取东方财富网-数据中心-龙虎榜单-龙虎榜详情数据
    
    Args:
        start_date (str): 开始日期，格式："20220314"
        end_date (str): 结束日期，格式："20220315"
    
    Returns:
        str: 龙虎榜详情数据的JSON格式字符串，包含序号、代码、名称、上榜日、解读、收盘价、涨跌幅、龙虎榜净买额、龙虎榜买入额、龙虎榜卖出额、龙虎榜成交额、市场总成交额、净买额占总成交比、成交额占总成交比、换手率、流通市值、上榜原因、上榜后各日涨跌幅等信息
    """
    try:
        df = ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取龙虎榜详情数据失败: {str(e)}"

@mcp.tool
def get_stock_individual_fund_flow(stock: str, market: str) -> str:
    """获取东方财富网-数据中心-个股资金流向数据
    
    Args:
        stock (str): 股票代码，例如："000425" 或 "600094"
        market (str): 交易所代码，可选："sh"(上海证券交易所), "sz"(深证证券交易所), "bj"(北京证券交易所)
    
    Returns:
        str: 个股资金流向数据的JSON格式字符串，包含日期、收盘价、涨跌幅、主力净流入-净额、主力净流入-净占比、超大单净流入-净额、超大单净流入-净占比、大单净流入-净额、大单净流入-净占比、中单净流入-净额、中单净流入-净占比、小单净流入-净额、小单净流入-净占比等近100个交易日的资金流数据
    """
    try:
        df = ak.stock_individual_fund_flow(stock=stock, market=market)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取个股资金流向数据失败: {str(e)}"

# ===================== 新闻资讯 ===================== #

@mcp.tool
def get_stock_info_global_em() -> str:
    """获取东方财富-全球财经快讯数据
    
    Returns:
        str: 全球财经快讯数据的JSON格式字符串，包含标题、摘要、发布时间、链接等最近200条新闻数据
    """
    try:
        df = ak.stock_info_global_em()
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取全球财经快讯数据失败: {str(e)}"

@mcp.tool
def get_stock_info_global_futu() -> str:
    """获取富途牛牛-快讯数据
    
    Returns:
        str: 富途牛牛快讯数据的JSON格式字符串，包含标题、内容、发布时间、链接等最近50条新闻数据
    """
    try:
        df = ak.stock_info_global_futu()
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取富途牛牛快讯数据失败: {str(e)}"


# ===================== 辅助工具 ===================== #

@mcp.tool
def get_stock_info_a_code_name() -> str:
    """获取沪深京A股股票代码和股票简称数据
    
    Returns:
        str: A股股票代码和名称数据的JSON格式字符串，包含所有沪深京A股的股票代码(code)和股票简称(name)
    """
    try:
        df = ak.stock_info_a_code_name()
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取A股股票代码和名称数据失败: {str(e)}"

@mcp.tool
def get_tool_trade_date_hist_sina() -> str:
    """获取新浪财经-股票交易日历数据
    
    Returns:
        str: 股票交易日历数据的JSON格式字符串，包含从1990-12-19到2024-12-31之间的所有股票交易日数据
    """
    try:
        df = ak.tool_trade_date_hist_sina()
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取股票交易日历数据失败: {str(e)}"

def main():
    """Main entry point for the MCP server."""
    # mcp.run()
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")

if __name__ == "__main__":
    main()