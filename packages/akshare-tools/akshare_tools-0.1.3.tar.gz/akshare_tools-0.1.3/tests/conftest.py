"""
pytest配置文件
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture
def mock_akshare():
    """全局akshare模拟fixture"""
    from unittest.mock import MagicMock
    import akshare as ak
    
    # 这里可以添加通用的akshare模拟设置
    yield

@pytest.fixture(autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 在每个测试前执行
    yield
    # 在每个测试后执行清理