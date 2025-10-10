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

@mcp.tool
def get_stock_szse_area_summary(date: str = "") -> str:
    """获取深圳证券交易所市场总貌-地区交易排序
    
    Args:
        date (str): 查询年月，格式："202203"，为空则查询最新月份数据
    
    Returns:
        str: 深交所地区交易排序数据的JSON格式字符串，包含各地区的总交易额、占市场比例、股票交易额、基金交易额、债券交易额等
    """
    try:
        if not date:
            # 如果没有指定日期，使用当前年月
            from datetime import datetime
            date = datetime.now().strftime("%Y%m")
        
        df = ak.stock_szse_area_summary(date=date)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取深交所地区交易排行失败: {str(e)}"

@mcp.tool
def get_stock_szse_sector_summary(symbol: str = "当月", date: str = "") -> str:
    """获取深圳证券交易所统计资料-股票行业成交数据
    
    Args:
        symbol (str): 统计周期，可选 "当月" 或 "当年"
        date (str): 查询年月，格式："202501"，为空则查询最新月份数据
    
    Returns:
        str: 深交所股票行业成交数据的JSON格式字符串，包含各行业的交易天数、成交金额、成交股数、成交笔数及占比等
    """
    try:
        if not date:
            # 如果没有指定日期，使用当前年月
            from datetime import datetime
            date = datetime.now().strftime("%Y%m")
        
        df = ak.stock_szse_sector_summary(symbol=symbol, date=date)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取深交所股票行业成交数据失败: {str(e)}"

@mcp.tool
def get_stock_sse_deal_daily(date: str = "") -> str:
    """获取上海证券交易所每日股票情况
    
    Args:
        date (str): 查询日期，格式："20250221"，为空则查询最新交易日数据，注意仅支持获取在20211227（包含）之后的数据
    
    Returns:
        str: 上交所每日股票情况数据的JSON格式字符串，包含挂牌数、市价总值、流通市值、成交金额、成交量、平均市盈率、换手率等
    """
    try:
        if not date:
            # 如果没有指定日期，使用今天
            from datetime import datetime
            date = datetime.now().strftime("%Y%m%d")
        
        df = ak.stock_sse_deal_daily(date=date)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取上交所每日股票情况失败: {str(e)}"

# ===================== 个股信息查询 ===================== #

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
def get_stock_bid_ask(symbol: str) -> str:
    """获取东方财富行情报价数据，包含买卖盘口信息
    
    Args:
        symbol (str): 股票代码，例如："000001"(平安银行)
    
    Returns:
        str: 行情报价数据的JSON格式字符串，包含五档买卖盘口、最新价、涨跌幅、成交量等信息
    """
    try:
        df = ak.stock_bid_ask_em(symbol=symbol)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取行情报价数据失败: {str(e)}"

@mcp.tool
def get_stock_a_hist(symbol: str, period: str = "daily", start_date: str = "", end_date: str = "", adjust: str = "") -> str:
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
def get_stock_intraday_em(symbol: str) -> str:
    """获取东方财富A股分时数据
    
    Args:
        symbol (str): 股票代码，例如："600000.SH"(浦发银行)
    
    Returns:
        str: A股分时数据的JSON格式字符串，包含时间、价格、成交量等分钟级数据
    """
    try:
        df = ak.stock_intraday_em(symbol=symbol)
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取A股分时数据失败: {str(e)}"

@mcp.tool
def get_stock_a_dividend_yield() -> str:
    """获取A股股息率数据（来自乐咕咕）
    
    Returns:
        str: A股股息率数据的JSON格式字符串，包含各股票的股息率信息
    """
    try:
        df = ak.stock_a_gxl_lg()
        return df.to_json(orient='records', force_ascii=False, indent=2)
    except Exception as e:
        return f"获取A股股息率数据失败: {str(e)}"

@mcp.tool
def get_stock_margin_data() -> str:
    """获取融资融券数据统计
    
    Returns:
        str: 融资融券数据的JSON格式字符串，包含融资融券账户统计信息
    """
    try:
        # 获取融资融券账户信息
        account_info = ak.stock_margin_account_info()
        # 获取融资融券比例数据
        margin_ratio = ak.stock_margin_ratio_pa()
        
        result = {
            "margin_account_info": account_info.to_dict('records') if not account_info.empty else [],
            "margin_ratio": margin_ratio.to_dict('records') if not margin_ratio.empty else []
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取融资融券数据失败: {str(e)}"

def main():
    """Main entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main()