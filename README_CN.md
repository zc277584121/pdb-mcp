# PDB MCP 服务器

[![PyPI version](https://badge.fury.io/py/pdb-mcp.svg)](https://badge.fury.io/py/pdb-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于模型上下文协议（MCP）的 Python 调试服务器，使用 pdb 进行调试，同时作为 **Claude Code 插件** 提供调试最佳实践指导。

## 功能特性

- **启动调试会话**：使用 pdb 在调试模式下启动 Python 脚本
- **启动 Pytest 调试会话**：运行 pytest，在测试失败时自动进入 pdb
- **执行 PDB 命令**：发送命令控制调试会话
- **自动检测 Python 解释器**：自动使用虚拟环境中的 Python
- **模块化架构**：会话模块和服务器模块职责清晰分离
- **Claude Code 插件**：内置 Skills，教导 Claude 结构化的调试工作流和最佳实践

## 安装

### 从 PyPI 安装

```bash
pip install pdb-mcp
```

### 使用 uv 安装（推荐）⚡️

[`uvx`](https://docs.astral.sh/uv/concepts/tools/) 会自动安装包并运行命令。

```bash
uvx pdb-mcp
```

### 开发环境安装

```bash
pip install -e .
```

## 使用方法

### 作为 MCP 服务器运行

启动服务器：

```bash
pdb-mcp
```

服务器提供三个工具：

#### 1. `start_debug`

为 Python 脚本启动调试会话。

**参数：**
- `script_path`（必需）：要调试的 Python 脚本路径
- `python_path`（必需）：被调试项目的 Python 解释器路径
- `working_directory`（必需）：运行命令的目录（应为项目目录）
- `args`（可选）：传递给脚本的命令行参数
- `timeout`（可选）：无新输出时等待的超时时间（秒），默认为 5.0。只要有新输出就会持续等待。
- `env`（可选）：为调试会话设置的环境变量（例如 {"DEBUG": "1"}）

**示例：**
```json
{
  "script_path": "test_script.py",
  "python_path": "/path/to/python",
  "working_directory": "/path/to/project",
  "env": {"DEBUG": "1"}
}
```

#### 2. `start_pytest_debug`

启动 pytest 调试会话，在测试失败时自动进入 pdb。

**参数：**
- `args`（必需）：传递给 'pytest --pdb' 之后的参数。可以包含测试路径、过滤器和 pytest 选项（例如 "tests/test_example.py -v"、"-k test_login"、"-x test_auth.py"）
- `python_path`（必需）：被调试项目的 Python 解释器路径
- `working_directory`（必需）：运行命令的目录（应为项目目录）
- `timeout`（可选）：无新输出时等待的超时时间（秒），默认为 10.0。只要有新输出就会持续等待。
- `env`（可选）：为调试会话设置的环境变量（例如 {"DEBUG": "1"}）

**示例：**
```json
{
  "args": "tests/test_example.py -v",
  "python_path": "/path/to/python",
  "working_directory": "/path/to/project",
  "env": {"DEBUG": "1"}
}
```

#### 3. `execute_pdb_command`

在活动的调试会话中执行 pdb 命令。

**参数：**
- `command`（必需）：要执行的 pdb 命令
- `timeout`（可选）：无新输出时等待的超时时间（秒），默认为 5.0

**可用命令：**
- `n`（next）：执行下一行（不进入函数）
- `s`（step）：执行下一行（进入函数）
- `b <行号>`：在指定行设置断点（例如 `b 10`）
- `b <文件>:<行号>`：在其他文件中设置断点（例如 `b utils.py:5`）
- `l`（list）：显示当前行附近的代码
- `p <变量>`：打印变量值（例如 `p user_name`）
- `c`（continue）：继续执行直到下一个断点
- `q`（quit）：退出调试会话
- `h`（help）：显示所有命令的帮助
- `r`（return）：执行直到当前函数返回
- `w`（where）：显示调用栈
- `cl <断点>`：清除断点
- `a`（args）：打印当前函数的参数

**示例：**
```json
{
  "command": "n"
}
```

## 测试

### 基本脚本调试

项目提供了示例测试脚本：`test_script.py`

运行自动化测试：
```bash
uv run python test_mcp_client.py
```

调试工作流示例：
1. 启动调试：`start_debug`，设置 `script_path = "test_script.py"`
2. 单步执行：`execute_pdb_command`，设置 `command = "n"`
3. 查看代码：`execute_pdb_command`，设置 `command = "l"`
4. 打印变量：`execute_pdb_command`，设置 `command = "p num"`
5. 继续执行：`execute_pdb_command`，设置 `command = "c"`
6. 退出：`execute_pdb_command`，设置 `command = "q"`

### Pytest 调试

项目提供了示例测试文件：`test_example.py`

运行 pytest 调试测试：
```bash
uv run python test_pytest_client.py
```

测试将会：
1. 使用 `-x --pdb` 标志运行 pytest
2. 在第一个失败的测试处停止
3. 在断言失败处进入 pdb
4. 允许您检查变量并进行调试

## 配置

要与 Claude Desktop 或其他 MCP 客户端一起使用，请添加到您的配置文件（例如 `claude_desktop_config.json`）：

### 使用 uvx（推荐）

```json
{
  "mcpServers": {
    "pdb-debugger": {
      "command": "uvx",
      "args": ["--from", "pdb-mcp", "pdb-mcp"]
    }
  }
}
```

### 使用本地开发版本

```json
{
  "mcpServers": {
    "pdb-debugger": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/pdb-mcp",
        "run",
        "pdb-mcp"
      ]
    }
  }
}
```

请将 `/path/to/pdb-mcp` 替换为本项目的实际路径。

## 架构

### 项目结构

```
src/pdb_mcp/
├── __init__.py      # 入口点和主函数
├── session.py       # PdbSession 类，用于管理 pdb 进程
└── server.py        # MCP 服务器和工具定义
```

### 会话管理

`PdbSession` 类维护一个持久的 pdb 进程：
- 使用 `subprocess.Popen` 启动带有目标脚本的 pdb
- 通过 stdin/stdout 管道进行通信
- 后台线程异步读取输出
- 在命令执行之间维护调试会话状态
- 自动检测虚拟环境中的 Python 解释器

### Python 解释器配置

`python_path` 参数指定**客户端项目**（而非服务器环境）的 Python 解释器：

- **必需参数**：代理应提供项目的 Python 解释器路径
- **典型值**：
  - `.venv/bin/python` 或 `venv/bin/python` 用于虚拟环境
  - `/usr/bin/python3` 用于系统 Python
  - 自定义路径用于 conda 或其他环境
- **回退机制**：如果未提供或为空，将回退到 `"python"` 命令（使用系统 PATH）

**注意：** 服务器不会使用自己的 Python（`sys.executable`），因为 MCP 服务器运行的环境可能与被调试的客户端项目环境不同。

### 工作目录配置

`start_debug` 和 `start_pytest_debug` 都需要 `working_directory` 参数：

- **必需参数**：应为项目的根目录或包含脚本的目录
- **用途**：确保脚本在正确的目录上下文中运行
- **使用场景**：
  - 使用相对文件路径的脚本
  - 具有特定目录结构要求的项目
  - 从项目根目录加载配置文件
- **代理集成**：代理（如 Claude）通常知道项目目录，应该提供它

**示例：**
```json
{
  "script_path": "src/main.py",
  "working_directory": "/home/user/myproject"
}
```

这相当于运行：
```bash
cd /home/user/myproject && python -m pdb src/main.py
```

### 智能输出等待

服务器使用智能输出等待机制：

- **单一超时参数**：无新输出时等待的时间
- **无总时间限制**：只要有新输出，服务器就会持续等待
- **自适应**：快速命令快速返回，慢速命令获得所需的时间
- **用户可配置**：所有工具都接受 `timeout` 参数

**工作原理：**
1. 服务器每 0.1 秒检查一次输出
2. 每次有新输出到达时，空闲计时器重置
3. 当无新输出持续 `timeout` 秒时返回
4. 无论脚本运行多长时间，只要持续产生输出，服务器就会等待

**默认超时值：**
- `start_debug`：5.0 秒（pdb 通常启动很快）
- `start_pytest_debug`：10.0 秒（测试可能产生输出较慢）
- `execute_pdb_command`：5.0 秒（大多数命令很快）

**示例：** 一个运行 10 秒但每 0.5 秒打印一次的脚本，使用 `timeout=3.0` 也能正常工作，因为空闲时间从未超过 3 秒。

## Claude Code 插件

本项目同时也是一个 **Claude Code 插件**，以 Skills 的形式提供调试最佳实践。安装为插件后，Claude 会自动获得结构化的调试指导。

### 插件安装

```bash
# 安装为 Claude Code 插件
claude plugin add /path/to/pdb-mcp
```

或本地测试：
```bash
claude --plugin-dir /path/to/pdb-mcp
```

### 包含的 Skills

#### PDB 调试最佳实践
调试 Python 脚本时自动激活。指导 Claude：
- 在启动调试会话**之前**先分析代码并规划断点
- 根据问题类型在关键位置设置断点
- 在每个断点处遵循系统化的调查模式
- 针对不同调试场景使用高效的 pdb 命令

#### Pytest 调试最佳实践
调试测试失败时自动激活。指导 Claude：
- 根据失败类型选择正确的调试模式（`--pdb` 或 `--trace`）
- 在调试前先缩小到具体的失败测试
- 通过调用栈导航找到应用代码中的根本原因
- 处理常见的 pytest 模式（fixtures、参数化测试、mock）

### 插件结构

```
pdb-mcp/
├── .claude-plugin/
│   └── plugin.json              # 插件清单
├── .mcp.json                    # MCP 服务器配置
├── skills/
│   ├── pdb-debugging/
│   │   ├── SKILL.md             # 核心调试最佳实践
│   │   └── references/
│   │       ├── debugging-workflows.md    # 详细工作流
│   │       └── pdb-commands-cheatsheet.md # 命令速查表
│   └── pytest-debugging/
│       ├── SKILL.md             # Pytest 调试最佳实践
│       └── references/
│           └── pytest-debug-patterns.md  # 高级调试模式
└── src/pdb_mcp/                 # MCP 服务器源代码
```

## 许可证

详见 LICENSE 文件。
