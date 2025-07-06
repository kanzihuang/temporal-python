# 单元测试规范

本项目遵循标准的Python单元测试规范，使用pytest作为测试框架。

## 测试结构

```
tests/
├── conftest.py              # pytest配置和共享fixtures
├── unit/                    # 单元测试
│   ├── test_schemas.py      # 数据模型测试
│   ├── test_config.py       # 配置模块测试
│   ├── test_vmware_service.py # VMware服务测试
│   ├── test_vm_activities.py # 活动测试
│   └── test_vm_workflows.py # 工作流测试
├── integration/             # 集成测试
│   └── test_vm_creation_integration.py # VM创建集成测试
└── README.md               # 测试文档
```

## 测试规范

### 1. 命名规范

- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头
- 使用描述性的测试名称

### 2. 测试覆盖范围

#### 单元测试
- **数据验证**: 测试Pydantic模型的验证逻辑
- **边界条件**: 测试最小值和最大值
- **错误处理**: 测试异常情况
- **配置加载**: 测试配置文件解析
- **服务方法**: 测试各个服务方法的功能

#### 集成测试
- **端到端流程**: 测试从工作流到活动的完整流程
- **数据流**: 验证数据在组件间的正确传递
- **错误传播**: 测试错误在组件间的传播
- **并发处理**: 测试并发执行场景

### 3. 测试原则

#### AAA模式 (Arrange-Act-Assert)
```python
def test_example():
    # Arrange - 准备测试数据
    request = VMRequest(vm_name="test", num_cpus=2, memory_gb=4, disk_size_gb=40)
    
    # Act - 执行被测试的方法
    result = service.create_vm(request)
    
    # Assert - 验证结果
    assert result == "test"
```

#### 测试隔离
- 每个测试独立运行
- 使用mock避免外部依赖
- 清理测试数据

#### 测试数据管理
- 使用fixtures提供测试数据
- 避免硬编码测试数据
- 使用有意义的测试数据

### 4. Mock使用规范

```python
# 模拟外部服务
@patch('module.external_service')
def test_with_mock(self, mock_service):
    mock_service.return_value = "expected_result"
    # 测试逻辑
```

### 5. 异步测试

```python
async def test_async_function():
    result = await async_function()
    assert result == "expected"
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行单元测试
```bash
pytest tests/unit/
```

### 运行集成测试
```bash
pytest tests/integration/
```

### 运行特定测试文件
```bash
pytest tests/unit/test_schemas.py
```

### 运行特定测试方法
```bash
pytest tests/unit/test_schemas.py::TestVMRequest::test_valid_vm_request
```

### 生成覆盖率报告
```bash
pytest --cov=temporal_python --cov-report=html
```

### 运行测试并显示详细输出
```bash
pytest -v
```

### 运行测试并显示打印输出
```bash
pytest -s
```

## 测试覆盖率

目标覆盖率：
- 单元测试: > 90%
- 集成测试: > 80%
- 总体覆盖率: > 85%

## 持续集成

测试在以下情况下自动运行：
- 代码提交
- Pull Request
- 发布前

## 测试维护

### 添加新测试
1. 确定测试类型（单元/集成）
2. 选择合适的测试文件
3. 遵循命名规范
4. 使用适当的fixtures
5. 确保测试独立性

### 更新测试
- 当功能变更时更新相关测试
- 保持测试与代码同步
- 删除过时的测试

### 测试文档
- 为复杂的测试添加注释
- 说明测试的目的和场景
- 记录测试的特殊要求

## 最佳实践

1. **测试驱动开发**: 先写测试，再写代码
2. **小步测试**: 每个测试只验证一个功能点
3. **可读性**: 测试代码应该清晰易懂
4. **可维护性**: 测试应该易于维护和更新
5. **性能**: 测试应该快速执行
6. **可靠性**: 测试应该稳定可靠，不产生假阳性或假阴性

## 常见问题

### Q: 如何处理外部依赖？
A: 使用mock模拟外部服务，避免真实的网络调用或数据库操作。

### Q: 如何测试异步代码？
A: 使用async/await语法，pytest支持异步测试。

### Q: 如何测试异常情况？
A: 使用pytest.raises()上下文管理器。

### Q: 如何共享测试数据？
A: 使用pytest fixtures在测试间共享数据。

### Q: 如何测试私有方法？
A: 通常只测试公共接口，私有方法通过公共接口间接测试。 