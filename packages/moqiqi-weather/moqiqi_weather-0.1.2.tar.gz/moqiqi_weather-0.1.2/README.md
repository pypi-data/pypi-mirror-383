# MCP Calculator - 天气查询服务

一个基于MCP（Model Context Protocol）的天气查询服务，提供实时天气信息获取功能。

## 功能特性

- 🌤️ 实时天气查询
- 🌍 支持全球城市查询
- 🔍 支持中英文城市名称
- ⚡ 基于FastMCP框架，响应迅速
- 🛠️ 标准MCP协议，易于集成

## 安装

### 环境要求

- Python >= 3.10
- pip 或 uv 包管理器

### 安装步骤

1. 克隆项目到本地：
```bash
git clone <repository-url>
cd mcp-calculator
```

2. 安装依赖：
```bash
# 使用 pip
pip install -e .

# 或使用 uv
uv sync
```

## 使用方法

### 作为MCP服务器运行

```bash
# 直接运行
python -m mcp_calculator_kel

# 或使用安装的脚本
mcp_calculator_kel
```

### 在AI助手中使用

此服务可以通过MCP协议与支持MCP的AI助手集成，提供天气查询功能。

## API文档

### weather工具

获取指定城市的实时天气信息。

**参数：**
- `city` (str, 可选): 城市名称，支持中文或英文。默认为"Beijing"

**返回值：**
- 返回格式化的天气信息字符串

**示例：**
```python
# 查询北京天气
weather("Beijing")

# 查询上海天气
weather("上海")

# 查询纽约天气
weather("New York")
```

## 项目结构

```
mcp-calculator/
├── src/
│   └── mcp_calculator_kel/
│       ├── __init__.py      # 主入口点
│       ├── __main__.py      # 模块运行入口
│       └── server.py        # MCP服务器实现
├── main.py                  # 简单测试脚本
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

## 技术栈

- **FastMCP**: 用于构建MCP服务器的框架
- **requests**: HTTP请求库，用于获取天气数据
- **wttr.in**: 天气数据源API

## 开发

### 本地开发

1. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

2. 运行测试：
```bash
python -m pytest
```

### 构建和发布

```bash
# 构建包
python -m build

# 发布到PyPI
python -m twine upload dist/*
```

## 配置

项目使用wttr.in作为天气数据源，无需API密钥。该服务提供简洁的天气信息格式。

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 更新日志

### v0.1.2
- 初始版本发布
- 支持基本的天气查询功能
- 集成MCP协议支持

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意**: 此项目虽然名为"calculator"，但实际提供的是天气查询服务。项目名称可能需要在未来版本中更新以更好地反映其功能。
