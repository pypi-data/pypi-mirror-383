# AKShare MCP 测试指南

## 测试状态

✅ **测试已修复并可以正常运行**

项目现在包含一个功能完整的测试套件，能够验证AKShare MCP服务器的基本功能。

## 快速开始

### 1. 检查测试环境
```bash
python3 scripts/run_tests.py check
```

### 2. 运行所有测试
```bash
python3 scripts/run_tests.py all
```

### 3. 运行特定类型的测试
```bash
# 运行单元测试
python3 scripts/run_tests.py unit

# 运行参数验证测试
python3 scripts/run_tests.py validation

# 运行集成测试
python3 scripts/run_tests.py integration

# 运行回归测试
python3 scripts/run_tests.py regression
```

### 4. 运行覆盖率测试
```bash
python3 scripts/run_tests.py coverage
```

## 测试覆盖范围

### ✅ 已实现的测试

1. **基础功能测试** (`tests/test_basic.py`)
   - 模块导入测试
   - 函数数量统计（验证29个工具函数）
   - pandas和akshare可用性测试
   - 函数文档完整性检查
   - JSON响应格式验证

2. **数据处理测试** (`tests/test_server_simple.py::TestAKShareFunctions`)
   - JSON格式化测试
   - 空DataFrame处理测试
   - 中文字符处理测试

3. **函数签名测试** (`tests/test_server_simple.py::TestFunctionSignatures`)
   - 函数文档字符串验证
   - 函数基本属性检查

4. **数据验证测试** (`tests/test_server_simple.py::TestDataValidation`)
   - JSON序列化测试
   - 数值数据类型验证
   - 数据完整性检查

### ⚠️ 已知限制

1. **装饰器包装问题**：由于FastMCP装饰器包装，无法直接调用函数进行完整测试
2. **依赖测试**：需要网络连接才能进行完整的akshare集成测试
3. **Mock限制**：部分高级功能的mock测试需要进一步完善

## 每次添加新工具后的回归测试流程

### 步骤 1: 检查当前测试状态
```bash
python3 scripts/run_tests.py check
```

### 步骤 2: 运行回归测试
```bash
python3 scripts/run_tests.py all
```

### 步骤 3: 验证新工具函数
```bash
# 检查函数是否被正确识别
python3 -c "
import sys
sys.path.insert(0, 'src')
import akshare_mcp.server as server_module
functions = [name for name in dir(server_module) if name.startswith('get_')]
print(f'当前函数数量: {len(functions)}')
"
```

### 步骤 4: 运行覆盖率测试（可选）
```bash
python3 scripts/run_tests.py coverage
```

## 测试结果解读

### 成功输出示例
```
============================= test session starts ==============================
collected 12 items

tests/test_basic.py::test_module_import PASSED [  8%]
tests/test_basic.py::test_basic_function_count PASSED [ 16%]
tests/test_basic.py::test_pandas_availability PASSED [ 25%]
...
============================= 12 passed in 0.97s ==============================
✓ 测试完成
```

### 失败处理
如果测试失败，系统会：
1. 显示具体的错误信息
2. 提供失败用例的详细信息
3. 返回非零退出码

## 测试文件说明

```
tests/
├── test_basic.py              # 基础功能测试 ✅
├── test_server_simple.py      # 简化的服务器测试 ✅
├── test_server.py             # 完整的服务器测试（部分功能）
├── test_validation.py         # 参数验证测试
└── conftest.py               # pytest配置
```

## 持续集成

项目配置了GitHub Actions自动测试，每次提交时都会：
- 检查测试环境
- 运行所有可用测试
- 验证代码覆盖率
- 检查代码格式和风格

## 故障排除

### 常见问题

1. **ImportError**: 检查Python路径设置
2. **ModuleNotFoundError**: 确认依赖包已安装
3. **FunctionTool not callable**: 这是正常的，因为函数被装饰器包装

### 解决方案

1. **重新安装依赖**:
```bash
pip install -r requirements-dev.txt
```

2. **检查Python环境**:
```bash
python3 -c "import sys; print(sys.path)"
```

3. **验证模块导入**:
```bash
python3 -c "import sys; sys.path.insert(0, 'src'); import akshare_mcp.server"
```

## 下一步计划

1. 完善Mock测试，覆盖更多边界情况
2. 添加性能测试
3. 实现端到端集成测试
4. 添加API文档生成和验证测试

---

**测试状态**: ✅ 可用  
**覆盖率**: 基础功能覆盖良好  
**回归能力**: ✅ 可以检测基础功能的回归问题