"""
工具参数验证测试
"""

import pytest
from unittest.mock import patch
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from akshare_mcp.server import mcp


class TestParameterValidation:
    """参数验证测试"""
    
    @patch('akshare_mcp.server.ak.stock_szse_summary')
    def test_date_parameter_validation(self, mock_func):
        """测试日期参数验证"""
        import pandas as pd
        mock_func.return_value = pd.DataFrame({'test': [1]})
        
        tool = mcp.get_tool('get_stock_szse_summary')
        
        # 测试默认参数（空字符串）
        result = tool()
        mock_func.assert_called_once()
        args, kwargs = mock_func.call_args
        assert 'date' in kwargs
        assert kwargs['date'] is not None  # 应该被设置为当前日期
        
        # 测试自定义日期
        mock_func.reset_mock()
        result = tool('20240101')
        mock_func.assert_called_once_with(date='20240101')
    
    @patch('akshare_mcp.server.ak.stock_individual_spot_xq')
    def test_symbol_parameter_validation(self, mock_func):
        """测试股票代码参数验证"""
        import pandas as pd
        mock_func.return_value = pd.DataFrame({'test': [1]})
        
        tool = mcp.get_tool('get_stock_info_xueqiu')
        
        # 测试不同格式的股票代码
        test_symbols = ['SH601318', 'SZ000001', 'BJ688001']
        
        for symbol in test_symbols:
            mock_func.reset_mock()
            result = tool(symbol)
            mock_func.assert_called_once_with(symbol=symbol)
    
    @patch('akshare_mcp.server.ak.stock_zh_a_hist')
    def test_hist_parameters_validation(self, mock_func):
        """测试历史数据参数验证"""
        import pandas as pd
        mock_func.return_value = pd.DataFrame({'test': [1]})
        
        tool = mcp.get_tool('get_stock_a_hist')
        
        # 测试默认参数
        result = tool('000001')
        mock_func.assert_called_once()
        args, kwargs = mock_func.call_args
        assert kwargs['symbol'] == '000001'
        assert kwargs['period'] == 'daily'
        assert kwargs['adjust'] == ''
        
        # 测试自定义参数
        mock_func.reset_mock()
        result = tool('000001', 'weekly', '20240101', '20241231', 'qfq')
        mock_func.assert_called_once()
        args, kwargs = mock_func.call_args
        assert kwargs['symbol'] == '000001'
        assert kwargs['period'] == 'weekly'
        assert kwargs['start_date'] == '20240101'
        assert kwargs['end_date'] == '20241231'
        assert kwargs['adjust'] == 'qfq'
    
    @patch('akshare_mcp.server.ak.stock_zh_a_hist_min_em')
    def test_min_hist_parameters_validation(self, mock_func):
        """测试分时数据参数验证"""
        import pandas as pd
        mock_func.return_value = pd.DataFrame({'test': [1]})
        
        tool = mcp.get_tool('get_stock_zh_a_hist_min_em')
        
        # 测试默认参数
        result = tool('000001')
        mock_func.assert_called_once()
        args, kwargs = mock_func.call_args
        assert kwargs['symbol'] == '000001'
        assert kwargs['period'] == '5'
        assert kwargs['adjust'] == ''
        
        # 测试不同的时间周期
        valid_periods = ['1', '5', '15', '30', '60']
        for period in valid_periods:
            mock_func.reset_mock()
            result = tool('000001', period=period)
            args, kwargs = mock_func.call_args
            assert kwargs['period'] == period
    
    @patch('akshare_mcp.server.ak.stock_individual_fund_flow')
    def test_fund_flow_parameters_validation(self, mock_func):
        """测试资金流向参数验证"""
        import pandas as pd
        mock_func.return_value = pd.DataFrame({'test': [1]})
        
        tool = mcp.get_tool('get_stock_individual_fund_flow')
        
        # 测试不同的市场代码
        valid_markets = ['sh', 'sz', 'bj']
        for market in valid_markets:
            mock_func.reset_mock()
            result = tool('000001', market)
            args, kwargs = mock_func.call_args
            assert kwargs['market'] == market
    
    @patch('akshare_mcp.server.ak.stock_hot_deal_xq')
    def test_hot_rank_parameters_validation(self, mock_func):
        """测试热门股票参数验证"""
        import pandas as pd
        mock_func.return_value = pd.DataFrame({'test': [1]})
        
        tool = mcp.get_tool('get_stock_hot_deal_xq')
        
        # 测试默认参数
        result = tool()
        args, kwargs = mock_func.call_args
        assert kwargs['symbol'] == '最热门'
        
        # 测试不同的排行榜类型
        valid_symbols = ['最热门', '本周新增']
        for symbol in valid_symbols:
            mock_func.reset_mock()
            result = tool(symbol)
            args, kwargs = mock_func.call_args
            assert kwargs['symbol'] == symbol


class TestErrorHandling:
    """错误处理测试"""
    
    @patch('akshare_mcp.server.ak.stock_sse_summary')
    def test_network_error_handling(self, mock_func):
        """测试网络错误处理"""
        mock_func.side_effect = Exception("网络连接失败")
        
        tool = mcp.get_tool('get_stock_sse_summary')
        result = tool()
        
        assert isinstance(result, str)
        assert "获取上交所股票数据总貌失败" in result
        assert "网络连接失败" in result
    
    @patch('akshare_mcp.server.ak.stock_info_a_code_name')
    def test_empty_result_handling(self, mock_func):
        """测试空结果处理"""
        import pandas as pd
        mock_func.return_value = pd.DataFrame()
        
        tool = mcp.get_tool('get_stock_info_a_code_name')
        result = tool()
        
        # 应该返回空数组的JSON字符串
        import json
        data = json.loads(result)
        assert data == []
    
    @patch('akshare_mcp.server.ak.stock_individual_spot_xq')
    def test_invalid_symbol_handling(self, mock_func):
        """测试无效股票代码处理"""
        import pandas as pd
        mock_func.side_effect = Exception("股票代码不存在")
        
        tool = mcp.get_tool('get_stock_info_xueqiu')
        result = tool('INVALID999')
        
        assert isinstance(result, str)
        assert "获取雪球个股信息失败" in result


class TestReturnFormatValidation:
    """返回格式验证测试"""
    
    @patch('akshare_mcp.server.ak.stock_zh_a_spot_em')
    def test_json_format_validation(self, mock_func):
        """测试JSON格式验证"""
        import pandas as pd
        test_data = pd.DataFrame({
            'code': ['000001', '000002'],
            'name': ['平安银行', '万科A'],
            'price': [10.5, 15.8]
        })
        mock_func.return_value = test_data
        
        tool = mcp.get_tool('get_stock_zh_a_spot_em')
        result = tool()
        
        # 验证返回的是有效JSON字符串
        import json
        data = json.loads(result)
        
        # 验证数据结构
        assert isinstance(data, list)
        assert len(data) == 2
        assert all(isinstance(record, dict) for record in data)
        
        # 验证具体字段
        first_record = data[0]
        assert 'code' in first_record
        assert 'name' in first_record
        assert 'price' in first_record
        assert first_record['code'] == '000001'
    
    @patch('akshare_mcp.server.ak.stock_financial_analysis_indicator')
    def test_numeric_data_format_validation(self, mock_func):
        """测试数值数据格式验证"""
        import pandas as pd
        test_data = pd.DataFrame({
            'date': ['2023-12-31', '2022-12-31'],
            'eps': [1.2, 1.0],
            'roe': [15.5, 14.2],
            'pe_ratio': [20.5, None]  # 包含空值
        })
        mock_func.return_value = test_data
        
        tool = mcp.get_tool('get_stock_financial_analysis_indicator')
        result = tool('600004', '2020')
        
        import json
        data = json.loads(result)
        
        # 验证数值数据正确处理
        first_record = data[0]
        assert isinstance(first_record['eps'], (int, float))
        assert first_record['eps'] == 1.2
        
        # 验证空值处理
        second_record = data[1]
        assert second_record['pe_ratio'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])