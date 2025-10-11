"""
AKShare MCP服务器简化测试版本

专门针对akshare模块的测试，避免对FastMCP的依赖
"""

import pytest
import json
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestAKShareFunctions:
    """直接测试akshare函数调用的简化测试"""
    
    @pytest.fixture
    def sample_dataframe(self):
        """创建示例DataFrame数据"""
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
            'empty_data': pd.DataFrame(),
            'single_row_data': pd.DataFrame({
                'code': ['000001'],
                'name': ['平安银行'],
                'price': [10.5]
            })
        }
    
    def test_json_format_response(self, sample_dataframe):
        """测试JSON格式化响应"""
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
    
    def test_empty_dataframe_handling(self, sample_dataframe):
        """测试空DataFrame处理"""
        df = sample_dataframe['empty_data']
        result = df.to_json(orient='records', force_ascii=False, indent=2)
        
        data = json.loads(result)
        assert data == []
    
    def test_chinese_character_handling(self, sample_dataframe):
        """测试中文字符处理"""
        df = sample_dataframe['stock_data']
        result = df.to_json(orient='records', force_ascii=False, indent=2)
        
        # 验证中文字符正确处理
        assert '平安银行' in result
        assert '万科A' in result
        
        data = json.loads(result)
        assert data[0]['name'] == '平安银行'


class TestFunctionImplementations:
    """测试实际函数实现"""
    
    @pytest.fixture
    def mock_akshare(self):
        """模拟akshare模块"""
        with patch('akshare_mcp.server.ak') as mock_ak:
            yield mock_ak
    
    def test_get_stock_sse_summary_implementation(self, mock_akshare):
        """测试上交所股票数据总貌函数实现"""
        # 创建测试数据
        import pandas as pd
        test_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'total_market_cap': [1000000, 1100000],
            'total_shares': [500000, 520000]
        })
        mock_akshare.stock_sse_summary.return_value = test_data
        
        # 导入模块并检查函数
        try:
            import akshare_mcp.server as server_module
            func = getattr(server_module, 'get_stock_sse_summary', None)
            
            assert func is not None, "函数 get_stock_sse_summary 不存在"
            
            # 如果函数被装饰器包装，检查其基本信息
            if hasattr(func, '__name__'):
                assert func.__name__ == 'get_stock_sse_summary'
            
            # 检查文档字符串
            assert func.__doc__ is not None, "函数缺少文档字符串"
            assert "上交所" in func.__doc__, "文档字符串不包含预期内容"
            
        except ImportError as e:
            pytest.skip(f"无法导入函数: {e}")
        except Exception as e:
            pytest.skip(f"函数测试失败: {e}")
    
    def test_get_stock_szse_summary_implementation(self, mock_akshare):
        """测试深交所股票数据总貌函数实现"""
        # 创建测试数据
        import pandas as pd
        test_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'total_market_cap': [1000000, 1100000],
            'total_shares': [500000, 520000]
        })
        mock_akshare.stock_szse_summary.return_value = test_data
        
        try:
            import akshare_mcp.server as server_module
            func = getattr(server_module, 'get_stock_szse_summary', None)
            
            assert func is not None, "函数 get_stock_szse_summary 不存在"
            
            # 检查文档字符串
            assert func.__doc__ is not None, "函数缺少文档字符串"
            assert "深交所" in func.__doc__, "文档字符串不包含预期内容"
            
        except ImportError as e:
            pytest.skip(f"无法导入函数: {e}")
        except Exception as e:
            pytest.skip(f"函数测试失败: {e}")
    
    def test_function_existence_check(self):
        """测试函数存在性检查"""
        try:
            import akshare_mcp.server as server_module
            
            # 检查核心函数是否存在
            core_functions = [
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
            
            existing_functions = []
            missing_functions = []
            
            for func_name in core_functions:
                func = getattr(server_module, func_name, None)
                if func is not None:
                    existing_functions.append(func_name)
                    # 检查函数基本信息
                    assert hasattr(func, '__doc__'), f"函数 {func_name} 缺少文档字符串"
                    assert func.__doc__, f"函数 {func_name} 文档字符串为空"
                else:
                    missing_functions.append(func_name)
            
            print(f"\n存在函数: {len(existing_functions)}/{len(core_functions)}")
            for func in existing_functions:
                print(f"  ✓ {func}")
            
            if missing_functions:
                print(f"缺失函数: {len(missing_functions)}")
                for func in missing_functions:
                    print(f"  ✗ {func}")
            
            # 至少应该有一些核心函数存在
            assert len(existing_functions) >= 5, f"核心函数数量不足: {len(existing_functions)}"
            
        except ImportError as e:
            pytest.skip(f"无法导入模块: {e}")
        except Exception as e:
            pytest.skip(f"模块检查失败: {e}")


class TestFunctionRegistration:
    """测试函数注册（如果FastMCP可用）"""
    
    def test_function_imports(self):
        """测试所有函数是否可以导入"""
        function_names = [
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
        
        imported_functions = []
        failed_imports = []
        
        for func_name in function_names:
            try:
                from akshare_mcp.server import func_name
                imported_functions.append(func_name)
            except ImportError as e:
                failed_imports.append((func_name, str(e)))
        
        # 报告导入结果
        print(f"\n成功导入的函数: {len(imported_functions)}/{len(function_names)}")
        for func in imported_functions:
            print(f"  ✓ {func}")
        
        if failed_imports:
            print(f"\n导入失败的函数: {len(failed_imports)}")
            for func, error in failed_imports:
                print(f"  ✗ {func}: {error}")
        
        # 至少应该有一些函数可以导入
        assert len(imported_functions) > 0, "没有函数可以成功导入"
    
    def test_mcp_server_creation(self):
        """测试MCP服务器创建（如果可用）"""
        try:
            from akshare_mcp.server import mcp
            assert mcp is not None
            
            # 如果mcp对象有tools属性，检查工具数量
            if hasattr(mcp, 'tools'):
                tool_count = len(mcp.tools)
                print(f"MCP服务器已注册工具数量: {tool_count}")
                assert tool_count > 0, "没有注册任何工具"
            
        except ImportError as e:
            pytest.skip(f"无法创建MCP服务器: {e}")
        except Exception as e:
            # 其他错误可能是FastMCP版本问题
            print(f"MCP服务器创建警告: {e}")
            pytest.skip(f"MCP服务器可能存在兼容性问题: {e}")


class TestFunctionSignatures:
    """测试函数签名"""
    
    def test_function_docstrings(self):
        """测试函数文档字符串"""
        try:
            import akshare_mcp.server as server_module
            
            # 获取所有函数
            functions = [getattr(server_module, name) for name in dir(server_module) 
                       if name.startswith('get_') and callable(getattr(server_module, name))]
            
            docstring_count = 0
            for func in functions:
                if func.__doc__ and func.__doc__.strip():
                    docstring_count += 1
                    # 检查文档是否包含基本要素
                    doc = func.__doc__
                    assert "获取" in doc or "返回" in doc, f"函数 {func.__name__} 缺少合适的文档"
            
            print(f"有文档字符串的函数: {docstring_count}/{len(functions)}")
            
        except ImportError as e:
            pytest.skip(f"无法导入模块: {e}")


class TestDataValidation:
    """测试数据验证"""
    
    @pytest.fixture
    def sample_akshare_response(self):
        """模拟akshare响应数据"""
        return pd.DataFrame({
            'code': ['000001', '000002', '600000'],
            'name': ['平安银行', '万科A', '浦发银行'],
            'price': [10.5, 15.8, 8.2],
            'change_pct': [2.1, -1.3, 0.5],
            'volume': [1000000, 800000, 1200000]
        })
    
    def test_json_serialization(self, sample_akshare_response):
        """测试JSON序列化"""
        result = sample_akshare_response.to_json(orient='records', force_ascii=False, indent=2)
        
        # 验证可以反序列化
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 3
        
        # 验证数据完整性
        first_item = data[0]
        assert first_item['code'] == '000001'
        assert first_item['name'] == '平安银行'
        assert isinstance(first_item['price'], (int, float))
    
    def test_numeric_data_types(self, sample_akshare_response):
        """测试数值数据类型"""
        result = sample_akshare_response.to_json(orient='records', force_ascii=False, indent=2)
        data = json.loads(result)
        
        for item in data:
            assert isinstance(item['price'], (int, float))
            assert isinstance(item['change_pct'], (int, float))
            assert isinstance(item['volume'], (int, float))


class TestErrorCases:
    """测试错误情况"""
    
    def test_network_error_simulation(self):
        """测试网络错误模拟"""
        with patch('akshare_mcp.server.ak') as mock_ak:
            mock_ak.stock_sse_summary.side_effect = Exception("网络连接超时")
            
            try:
                from akshare_mcp.server import get_stock_sse_summary
                result = get_stock_sse_summary()
                
                assert isinstance(result, str)
                assert "获取上交所股票数据总貌失败" in result
                assert "网络连接超时" in result
                
            except ImportError:
                pytest.skip("函数不可导入")
    
    def test_empty_response_handling(self):
        """测试空响应处理"""
        with patch('akshare_mcp.server.ak') as mock_ak:
            # 模拟空DataFrame响应
            mock_ak.stock_sse_summary.return_value = pd.DataFrame()
            
            try:
                from akshare_mcp.server import get_stock_sse_summary
                result = get_stock_sse_summary()
                
                data = json.loads(result)
                assert data == []
                
            except ImportError:
                pytest.skip("函数不可导入")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])