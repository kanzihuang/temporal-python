# Python 项目创建与开发规则（temporal-python 适用）

## 1. 目录结构规范

```
your_project/
├── README.md
├── pyproject.toml / requirements.txt
├── poetry.lock
├── LICENSE
├── .gitignore
├── your_project/           # 主代码包（与项目同名）
│   ├── __init__.py
│   ├── module1.py
│   ├── module2/
│   │   └── __init__.py
│   └── ...
├── tests/                  # 测试目录
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── config/                 # 配置文件目录
│   └── config.yaml
└── scripts/                # 辅助脚本（可选）
```

## 2. 依赖管理
- 推荐使用 Poetry 管理依赖，禁止直接用 pip freeze 生成 requirements.txt。
- 依赖必须写在 pyproject.toml 中，开发依赖（如 pytest、mypy）用 --dev 标记。
- 锁文件（如 poetry.lock）必须提交到版本库。

## 3. 虚拟环境
- 每个项目必须使用独立的虚拟环境（如 .venv、Poetry 自动管理的 env）。
- 不允许在全局 Python 环境下开发和运行。

## 4. 代码规范
- 代码必须符合 PEP8 规范。
- 推荐使用 black 自动格式化，isort 排序 import，flake8/ruff 静态检查。
- 变量、函数、类、模块命名要有意义，遵循 snake_case、CamelCase 规范。
- 每个模块、类、函数必须有 docstring 注释。

## 5. 测试规范
- 测试代码必须与业务代码分离，放在 tests/ 目录下，结构与主包一致。
- 单元测试放在 tests/unit/，集成测试放在 tests/integration/。
- 测试用例必须覆盖主要业务逻辑，目标覆盖率建议 ≥ 80%。
- 测试必须可重复运行，不依赖外部环境（如真实数据库、外部 API），必要时用 mock。
- 推荐使用 pytest，并配置好 pytest.ini 或在 pyproject.toml 里统一管理。

## 6. Mock 和依赖隔离
- 测试中涉及外部依赖（如数据库、第三方 API、云服务等）必须使用 mock 或 fixture 隔离。
- 不允许测试用例直接操作生产环境资源。

## 7. 文档与说明
- 项目根目录必须有 README.md，说明项目简介、安装方法、用法、测试方法等。
- 重要模块、复杂逻辑要有详细注释和/或单独文档。
- 配置文件要有示例（如 config.example.yaml）。

## 8. 版本控制
- 必须使用 git 进行版本管理。
- .gitignore 要排除虚拟环境、pyc 文件、临时文件、敏感信息等。
- 代码提交前必须通过所有测试和静态检查。

## 9. 其他建议
- 重要变更建议写 CHANGELOG.md。
- 复杂项目建议加 Makefile 或 scripts/ 目录，统一常用命令。
- 生产环境配置与开发环境分离，敏感信息不入库。 