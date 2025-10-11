"""
基础测试 - 验证基本功能
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_module_import():
    """测试模块导入"""
    try:
        import akshare_mcp.server
        assert True, "模块导入成功"
    except ImportError as e:
        pytest.fail(f"模块导入失败: {e}")

def test_basic_function_count():
    """测试基本函数数量"""
    try:
        import akshare_mcp.server as server_module
        
        # 获取所有以get_开头的函数（包括被装饰器包装的）
        functions = [name for name in dir(server_module) 
                   if name.startswith('get_') and hasattr(getattr(server_module, name), '__doc__')]
        
        print(f"\n发现的函数数量: {len(functions)}")
        for func in functions[:10]:  # 只显示前10个
            print(f"  - {func}")
        
        if len(functions) > 10:
            print(f"  ... 还有 {len(functions) - 10} 个函数")
        
        assert len(functions) > 0, "没有发现任何函数"
        assert len(functions) >= 20, f"函数数量不足: {len(functions)}"
        
    except ImportError as e:
        pytest.fail(f"无法导入模块: {e}")

def test_pandas_availability():
    """测试pandas可用性"""
    try:
        import pandas as pd
        
        # 创建简单DataFrame
        df = pd.DataFrame({
            'code': ['000001', '000002'],
            'name': ['平安银行', '万科A'],
            'price': [10.5, 15.8]
        })
        
        # 测试JSON转换
        result = df.to_json(orient='records', force_ascii=False, indent=2)
        assert isinstance(result, str)
        assert '平安银行' in result
        
        # 测试JSON解析
        import json
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]['code'] == '000001'
        
    except ImportError as e:
        pytest.fail(f"pandas不可用: {e}")

def test_akshare_availability():
    """测试akshare可用性"""
    try:
        import akshare as ak
        
        # 检查一些基本函数是否可用
        functions_to_check = [
            'stock_sse_summary',
            'stock_szse_summary',
            'stock_zh_a_spot_em',
            'stock_info_a_code_name'
        ]
        
        available_functions = []
        for func_name in functions_to_check:
            if hasattr(ak, func_name):
                available_functions.append(func_name)
        
        print(f"\nakshare可用函数: {len(available_functions)}/{len(functions_to_check)}")
        for func in available_functions:
            print(f"  ✓ {func}")
        
        assert len(available_functions) > 0, "没有可用的akshare函数"
        
    except ImportError as e:
        pytest.fail(f"akshare不可用: {e}")

def test_function_documentation():
    """测试函数文档"""
    try:
        import akshare_mcp.server as server_module
        
        # 获取前5个函数并检查文档
        functions = [name for name in dir(server_module) 
                   if name.startswith('get_') and callable(getattr(server_module, name))][:5]
        
        for func_name in functions:
            func = getattr(server_module, func_name)
            doc = func.__doc__
            
            assert doc is not None, f"函数 {func_name} 缺少文档字符串"
            assert len(doc.strip()) > 0, f"函数 {func_name} 文档字符串为空"
            assert "获取" in doc or "返回" in doc, f"函数 {func_name} 文档字符串格式不正确"
            
            print(f"✓ {func_name}: {doc[:50]}...")
        
    except ImportError as e:
        pytest.fail(f"无法导入模块: {e}")

def test_json_response_format():
    """测试JSON响应格式"""
    import pandas as pd
    import json
    
    # 创建示例数据
    df = pd.DataFrame({
        'code': ['000001', '000002', '600000'],
        'name': ['平安银行', '万科A', '浦发银行'],
        'price': [10.5, 15.8, 8.2],
        'change_pct': [2.1, -1.3, 0.5]
    })
    
    # 转换为JSON
    result = df.to_json(orient='records', force_ascii=False, indent=2)
    
    # 验证格式
    assert isinstance(result, str)
    
    # 验证JSON可解析
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 3
    
    # 验证数据内容
    first_item = data[0]
    assert first_item['code'] == '000001'
    assert first_item['name'] == '平安银行'
    assert isinstance(first_item['price'], (int, float))
    assert isinstance(first_item['change_pct'], (int, float))

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])