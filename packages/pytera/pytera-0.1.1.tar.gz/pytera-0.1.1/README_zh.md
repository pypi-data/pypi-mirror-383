# PyTera

[![PyPI version](https://badge.fury.io/py/pytera.svg)](https://pypi.org/project/pytera/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytera.svg)](https://pypi.org/project/pytera/)
[![License](https://img.shields.io/pypi/l/pytera.svg)](https://github.com/un4gt/pytera/blob/main/LICENSE)
[![CI](https://github.com/un4gt/pytera/actions/workflows/ci.yml/badge.svg)](https://github.com/un4gt/pytera/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/un4gt/pytera/branch/main/graph/badge.svg)](https://codecov.io/gh/un4gt/pytera)

一个快速、原生 Python 模板引擎，由 Rust 的 Tera 库提供支持。PyTera 通过 PyO3 绑定将 Tera 模板的强大功能和性能带到 Python 应用程序中。

## 特性

- 🚀 **高性能**：Rust 驱动的模板引擎，具有零拷贝操作
- 🐍 **Python 原生**：与 Python 数据类型和工作流无缝集成
- 📝 **Tera 兼容**：完全支持 Tera 模板语法和功能
- 🔧 **易于集成**：与 Flask、FastAPI 和其他 Web 框架配合使用的简单 API
- 🛡️ **类型安全**：全面的类型提示和错误处理
- 📚 **丰富功能**：变量、条件语句、循环、过滤器、继承等

## 安装

从 PyPI 安装 PyTera：

```bash
pip install pytera
```

或使用 uv：

```bash
uv add pytera
```

### 系统要求

- Python 3.8+
- Rust 工具链（从源码构建时需要）

## 快速开始

```python
from pytera import PyTera

# 使用模板目录初始化
tera = PyTera("templates/*.html")

# 渲染模板
result = tera.render_template("hello.html", {"name": "World"})
print(result)  # Hello World!
```

## 使用示例

### 基本变量

```python
from pytera import PyTera

tera = PyTera("templates/*.html")
result = tera.render_template("basic_variables.html", {
    "name": "Alice",
    "age": 30
})
# 输出：Hello Alice! You are 30 years old.
```

### 条件语句

```python
user = {"name": "Bob", "is_admin": True}
result = tera.render_template("conditionals.html", {"user": user})
# 输出：Welcome, Administrator Bob!
```

### 循环

```python
items = [
    {"name": "Apple", "price": 1.50},
    {"name": "Banana", "price": 0.75},
    {"name": "Cherry", "price": 2.25},
]
result = tera.render_template("loops.html", {"items": items})
```

### 过滤器

```python
data = {
    "text": "hello world",
    "missing": None,
    "list": ["apple", "banana", "cherry", "date"],
}
result = tera.render_template("filters.html", data)
```

### 模板继承

```python
# base.html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    <h1>My Website</h1>
    {% block content %}{% endblock %}
</body>
</html>

# child.html
{% extends "base.html" %}

{% block title %}Home Page{% endblock %}

{% block content %}
<h2>Welcome to {{ site_name }}</h2>
<p>Hello, {{ user.name }}!</p>
{% endblock %}
```

### Flask 集成

```python
from flask import Flask
from pytera import PyTera

app = Flask(__name__)
tera = PyTera("templates/*.html")

@app.route("/")
def index():
    return tera.render_template(
        "page.html",
        {"site_name": "My Site", "user": {"name": "David"}}
    )

if __name__ == "__main__":
    app.run()
```

## API 参考

### PyTera 类

#### `__init__(glob: str)`

使用模板 glob 模式初始化 PyTera。

**参数：**
- `glob` (str): 模板文件的 glob 模式（例如 `"templates/**/*.html"`）

**异常：**
- `ValueError`: glob 模式无效或模板配置错误
- `RuntimeError`: 模板解析失败或继承问题
- `UnicodeDecodeError`: UTF-8 解码错误
- `OSError`: 文件 I/O 错误

#### `render_template(template: str, kwargs: Optional[Mapping[str, Any]] = None) -> str`

使用给定上下文渲染模板。

**参数：**
- `template` (str): 模板名称/键
- `kwargs` (Optional[Mapping[str, Any]]): 上下文字典

**返回：**
- `str`: 渲染后的模板内容

**异常：**
- `ValueError`: 上下文键无效或配置错误
- `RuntimeError`: 模板渲染错误
- `UnicodeDecodeError`: 编码错误
- `OSError`: 文件 I/O 错误

#### `templates() -> list[str]`

获取已加载模板名称列表。

**返回：**
- `list[str]`: 模板名称列表

## 模板语法

PyTera 支持完整的 Tera 模板语法：

### 变量
```
{{ variable }}
{{ user.name }}
```

### 条件语句
```
{% if condition %}
内容在这里
{% elif other_condition %}
其他内容
{% else %}
默认内容
{% endif %}
```

### 循环
```
{% for item in items %}
{{ item.name }}: {{ item.price }}
{% endfor %}
```

### 过滤器
```
{{ text | upper }}
{{ number | round(precision=2) }}
{{ list | slice(start=1, end=3) | join(sep=", ") }}
```

### 模板继承
```
<!-- base.html -->
{% block content %}{% endblock %}

<!-- child.html -->
{% extends "base.html" %}
{% block content %}子内容{% endblock %}
```

## 错误处理

PyTera 为常见问题提供详细的错误信息：

- **模板未找到**：请求不存在的模板时
- **无效上下文**：上下文键不是字符串时
- **解析错误**：模板中的语法错误
- **继承问题**：循环依赖或缺少父模板

## 性能

PyTera 专为高性能而设计：

- Rust 中的零拷贝字符串操作
- 高效的模板编译和缓存
- 通过 PyO3 最小化 Python 开销

## 开发

### 从源码构建

```bash
# 克隆仓库
git clone https://github.com/un4gt/pytera.git
cd pytera

# 安装开发依赖
uv sync --dev

# 构建包
maturin develop

# 运行测试
pytest
```

### 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率运行
pytest --cov=pytera --cov-report=html
```

### 代码质量

```bash
# 格式化代码
cargo fmt
black src/

# 检查代码
cargo clippy
flake8 src/
```

## 贡献

我们欢迎贡献！请查看我们的[贡献指南](CONTRIBUTING.md)了解详情。

1. Fork 本仓库
2. 创建功能分支
3. 进行更改
4. 添加测试
5. 提交拉取请求

### 开发环境设置

```bash
# 安装开发依赖
uv sync --dev

# 安装 pre-commit 钩子
pre-commit install

# 构建和测试
maturin develop
pytest
```

## 许可证

PyTera 使用 MIT 许可证。详见 [LICENSE](LICENSE)。

## 致谢

- [Tera](https://tera.netlify.app/) - Rust 模板引擎
- [PyO3](https://pyo3.rs/) - Rust 的 Python 绑定
- [Maturin](https://www.maturin.rs/) - Python 扩展构建工具

## 更新日志

版本历史请见 [CHANGELOG.md](CHANGELOG.md)。</content>