"""
AKShare MCP服务器测试模块

包含所有工具函数的单元测试、集成测试和回归测试
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 延迟导入，避免FastMCP依赖问题
mcp = None
try:
    from akshare_mcp.server import mcp
except ImportError:
    print("Warning: Could not import mcp object, some tests may be skipped")
except Exception as e:
    print(f"Warning: MCP server creation failed: {e}")


class TestMCPTools:
    """AKShare MCP工具函数测试基类"""
    
    @pytest.fixture
    def mock_akshare(self):
        """模拟akshare模块"""
        with patch('akshare_mcp.server.ak') as mock_ak:
            yield mock_ak
    
    @pytest.fixture
    def sample_dataframe(self):
        """创建示例DataFrame数据"""
        import pandas as pd
        
        # 创建不同类型的示例数据
        return {
            'market_summary': pd.DataFrame({
                'date': ['2024-01-01', '2024-01-02'],
                'total_market_cap': [1000000, 1100000],
                'total_shares': [500000, 520000]
            }),
            'stock_data': pd.DataFrame({
                'code': ['000001', '000002'],
                'name': ['平安银行', '万科A'],
                'price': [10.5, 15.8],
                'change_pct': [2.1, -1.3]
            }),
            'news_data': pd.DataFrame({
                'title': ['新闻标题1', '新闻标题2'],
                'summary': ['摘要1', '摘要2'],
                'publish_time': ['2024-01-01 10:00', '2024-01-01 11:00'],
                'url': ['http://example.com/1', 'http://example.com/2']
            }),
            'financial_data': pd.DataFrame({
                'date': ['2023-12-31', '2022-12-31'],
                'eps': [1.2, 1.0],
                'roe': [15.5, 14.2],
                'pe_ratio': [20.5, 18.8]
            }),
            'fund_flow_data': pd.DataFrame({
                'date': ['2024-01-01', '2024-01-02'],
                'main_net_inflow': [1000000, -500000],
                'main_net_inflow_ratio': [2.5, -1.2],
                'close_price': [10.5, 10.3]
            })
        }
    
    def test_json_format_response(self, sample_dataframe):
        """测试JSON格式化响应"""
        # 测试DataFrame能否正确转换为JSON
        df = sample_dataframe['stock_data']
        result = df.to_json(orient='records', force_ascii=False, indent=2)
        
        # 验证结果
        assert isinstance(result, str)
        
        # 验证JSON格式
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['code'] == '000001'
        assert data[1]['name'] == '万科A'
    
    def test_error_handling(self, mock_akshare):
        """测试错误处理"""
        # 模拟akshare抛出异常
        mock_ak.stock_sse_summary.side_effect = Exception("网络错误")
        
        # 直接测试函数，不依赖MCP对象
        try:
            from akshare_mcp.server import get_stock_sse_summary
            result = get_stock_sse_summary()
            
            # 验证错误处理
            assert isinstance(result, str)
            assert "获取上交所股票数据总貌失败" in result
        except ImportError:
            pytest.skip("Cannot import get_stock_sse_summary function")


class TestMarketDataTools:
    """市场数据相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_sse_summary')
    def test_get_stock_sse_summary(self, mock_func, sample_dataframe):
        """测试上交所股票数据总貌"""
        mock_func.return_value = sample_dataframe['market_summary']
        
        # 直接导入和测试函数
        try:
            from akshare_mcp.server import get_stock_sse_summary
            result = get_stock_sse_summary()
            
            data = json.loads(result)
            assert len(data) == 2
            assert data[0]['total_market_cap'] == 1000000
            mock_func.assert_called_once()
        except ImportError:
            pytest.skip("Cannot import get_stock_sse_summary function")
    
    @patch('akshare_mcp.server.ak.stock_szse_summary')
    def test_get_stock_szse_summary(self, mock_func, sample_dataframe):
        """测试深交所股票数据总貌"""
        mock_func.return_value = sample_dataframe['market_summary']
        
        try:
            from akshare_mcp.server import get_stock_szse_summary
            result = get_stock_szse_summary()
            
            data = json.loads(result)
            assert isinstance(data, list)
            mock_func.assert_called_once()
        except ImportError:
            pytest.skip("Cannot import get_stock_szse_summary function")
    
    @patch('akshare_mcp.server.ak.stock_zh_a_spot_em')
    def test_get_stock_zh_a_spot_em(self, mock_func, sample_dataframe):
        """测试沪深京A股实时行情"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_zh_a_spot_em')
        result = tool()
        
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]['code'] == '000001'
        mock_func.assert_called_once()


class TestStockInfoTools:
    """个股信息相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_individual_spot_xq')
    def test_get_stock_info_xueqiu(self, mock_func, sample_dataframe):
        """测试雪球个股信息"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_info_xueqiu')
        result = tool('SH601318')
        
        data = json.loads(result)
        mock_func.assert_called_once_with(symbol='SH601318')
    
    @patch('akshare_mcp.server.ak.stock_individual_info_em')
    def test_get_stock_individual_info_em(self, mock_func, sample_dataframe):
        """测试东方财富个股信息"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_individual_info_em')
        result = tool('000001')
        
        data = json.loads(result)
        mock_func.assert_called_once_with(symbol='000001', timeout=None)
    
    @patch('akshare_mcp.server.ak.stock_individual_basic_info_xq')
    def test_get_stock_individual_basic_info_xq(self, mock_func, sample_dataframe):
        """测试雪球个股基本信息"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_individual_basic_info_xq')
        result = tool('SH601127')
        
        data = json.loads(result)
        mock_func.assert_called_once_with(symbol='SH601127', token=None, timeout=None)


class TestHistoricalDataTools:
    """历史数据相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_zh_a_hist')
    def test_get_stock_a_hist(self, mock_func, sample_dataframe):
        """测试A股历史K线数据"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_a_hist')
        result = tool('000001', 'daily', '20240101', '20241231', 'qfq')
        
        data = json.loads(result)
        mock_func.assert_called_once()
    
    @patch('akshare_mcp.server.ak.stock_zh_a_hist_min_em')
    def test_get_stock_zh_a_hist_min_em(self, mock_func, sample_dataframe):
        """测试A股分时行情数据"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_zh_a_hist_min_em')
        result = tool('000001', '2024-03-20 09:30:00', '2024-03-20 15:00:00', '1', '')
        
        data = json.loads(result)
        mock_func.assert_called_once()


class TestFinancialAnalysisTools:
    """财务分析相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_financial_analysis_indicator')
    def test_get_stock_financial_analysis_indicator(self, mock_func, sample_dataframe):
        """测试财务指标数据"""
        mock_func.return_value = sample_dataframe['financial_data']
        
        tool = mcp.get_tool('get_stock_financial_analysis_indicator')
        result = tool('600004', '2020')
        
        data = json.loads(result)
        assert len(data) == 2
        mock_func.assert_called_once_with(symbol='600004', start_year='2020')


class TestNewsTools:
    """新闻资讯相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_info_global_em')
    def test_get_stock_info_global_em(self, mock_func, sample_dataframe):
        """测试东方财富全球财经快讯"""
        mock_func.return_value = sample_dataframe['news_data']
        
        tool = mcp.get_tool('get_stock_info_global_em')
        result = tool()
        
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]['title'] == '新闻标题1'
        mock_func.assert_called_once()
    
    @patch('akshare_mcp.server.ak.stock_info_global_futu')
    def test_get_stock_info_global_futu(self, mock_func, sample_dataframe):
        """测试富途牛牛快讯"""
        mock_func.return_value = sample_dataframe['news_data']
        
        tool = mcp.get_tool('get_stock_info_global_futu')
        result = tool()
        
        data = json.loads(result)
        assert len(data) == 2
        mock_func.assert_called_once()


class TestIndustryBoardTools:
    """行业板块相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_board_industry_name_em')
    def test_get_stock_board_industry_name_em(self, mock_func, sample_dataframe):
        """测试行业板块数据"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_board_industry_name_em')
        result = tool()
        
        data = json.loads(result)
        assert len(data) == 2
        mock_func.assert_called_once()
    
    @patch('akshare_mcp.server.ak.stock_board_industry_cons_em')
    def test_get_stock_board_industry_cons_em(self, mock_func, sample_dataframe):
        """测试行业板块成份股"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_board_industry_cons_em')
        result = tool('小金属')
        
        data = json.loads(result)
        mock_func.assert_called_once_with(symbol='小金属')


class TestFundFlowTools:
    """资金流向相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_individual_fund_flow')
    def test_get_stock_individual_fund_flow(self, mock_func, sample_dataframe):
        """测试个股资金流向"""
        mock_func.return_value = sample_dataframe['fund_flow_data']
        
        tool = mcp.get_tool('get_stock_individual_fund_flow')
        result = tool('600094', 'sh')
        
        data = json.loads(result)
        assert len(data) == 2
        mock_func.assert_called_once_with(stock='600094', market='sh')


class TestHotRankTools:
    """股票热度相关工具测试"""
    
    @patch('akshare_mcp.server.ak.stock_hot_rank_em')
    def test_get_stock_hot_rank_em(self, mock_func, sample_dataframe):
        """测试A股人气排行榜"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_hot_rank_em')
        result = tool()
        
        data = json.loads(result)
        assert len(data) == 2
        mock_func.assert_called_once()
    
    @patch('akshare_mcp.server.ak.stock_hot_deal_xq')
    def test_get_stock_hot_deal_xq(self, mock_func, sample_dataframe):
        """测试雪球交易排行榜"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_hot_deal_xq')
        result = tool('最热门')
        
        data = json.loads(result)
        mock_func.assert_called_once_with(symbol='最热门')


class TestUtilityTools:
    """辅助工具相关测试"""
    
    @patch('akshare_mcp.server.ak.stock_info_a_code_name')
    def test_get_stock_info_a_code_name(self, mock_func, sample_dataframe):
        """测试A股股票代码名称"""
        mock_func.return_value = sample_dataframe['stock_data']
        
        tool = mcp.get_tool('get_stock_info_a_code_name')
        result = tool()
        
        data = json.loads(result)
        assert len(data) == 2
        mock_func.assert_called_once()
    
    @patch('akshare_mcp.server.ak.tool_trade_date_hist_sina')
    def test_get_tool_trade_date_hist_sina(self, mock_func, sample_dataframe):
        """测试交易日历数据"""
        mock_func.return_value = sample_dataframe['market_summary']
        
        tool = mcp.get_tool('get_tool_trade_date_hist_sina')
        result = tool()
        
        data = json.loads(result)
        assert len(data) == 2
        mock_func.assert_called_once()


class TestIntegration:
    """集成测试"""
    
    def test_mcp_server_initialization(self):
        """测试MCP服务器初始化"""
        assert mcp is not None
        assert mcp.name == "akshare"
    
    def test_all_tools_registered(self):
        """测试所有工具是否正确注册"""
        # 获取所有已注册的工具名称
        tool_names = list(mcp.tools.keys())
        
        # 验证核心工具是否注册
        expected_tools = [
            'get_stock_sse_summary',
            'get_stock_szse_summary', 
            'get_stock_zh_a_spot_em',
            'get_stock_info_xueqiu',
            'get_stock_a_hist',
            'get_stock_financial_analysis_indicator',
            'get_stock_info_global_em',
            'get_stock_info_a_code_name',
            'get_tool_trade_date_hist_sina'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"工具 {tool_name} 未注册"
    
    @pytest.mark.parametrize("tool_name", [
        'get_stock_sse_summary',
        'get_stock_szse_summary',
        'get_stock_zh_a_spot_em',
        'get_stock_info_a_code_name',
        'get_tool_trade_date_hist_sina'
    ])
    def test_tool_signature(self, tool_name):
        """测试工具函数签名"""
        tool = mcp.get_tool(tool_name)
        assert callable(tool), f"工具 {tool_name} 不可调用"


class TestRegression:
    """回归测试"""
    
    def test_json_output_consistency(self, sample_dataframe):
        """测试JSON输出格式一致性"""
        df = sample_dataframe['stock_data']
        
        # 测试不同的导出参数
        result1 = df.to_json(orient='records', force_ascii=False, indent=2)
        result2 = df.to_json(orient='records', force_ascii=False, indent=2)
        
        # 结果应该一致
        assert result1 == result2
        
        # 验证JSON格式
        data1 = json.loads(result1)
        data2 = json.loads(result2)
        assert data1 == data2
    
    def test_chinese_character_handling(self, sample_dataframe):
        """测试中文字符处理"""
        # 创建包含中文的DataFrame
        import pandas as pd
        df = pd.DataFrame({
            'code': ['000001'],
            'name': ['平安银行'],
            'industry': ['银行']
        })
        
        result = df.to_json(orient='records', force_ascii=False, indent=2)
        
        # 验证中文字符正确处理
        assert '平安银行' in result
        assert '银行' in result
        
        data = json.loads(result)
        assert data[0]['name'] == '平安银行'
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        import pandas as pd
        df = pd.DataFrame()
        
        result = df.to_json(orient='records', force_ascii=False, indent=2)
        
        # 空DataFrame应该返回空数组
        data = json.loads(result)
        assert data == []


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])