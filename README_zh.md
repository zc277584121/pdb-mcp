# PDB MCP Server

一个基于模型上下文协议（Model Context Protocol，MCP）的 Python 调试服务器，使用 pdb 调试器。允许你通过 MCP 工具调试 Python 脚本。

## 功能特性

- **启动调试会话**：使用 pdb 以调试模式启动 Python 脚本
- **启动 Pytest 调试会话**：运行 pytest，在测试失败时自动进入 pdb
- **执行 PDB 命令**：发送命令来控制调试会话
- **自动检测 Python 解释器**：自动使用虚拟环境中的 Python
- **模块化架构**：清晰的模块分离，包含会话管理和服务器模块

## 安装

```bash
pip install -e .
```

## 使用方法

### 作为 MCP 服务器

运行服务器：

```bash
pdb-mcp
```

服务器提供三个工具：

#### 1. `start_debug`

启动 Python 脚本的调试会话。

**参数：**
- `script_path`（必需）：要调试的 Python 脚本路径
- `python_path`（必需）：用于调试项目的 Python 解释器路径
- `working_directory`（必需）：运行命令的目录（应该是项目目录）
- `args`（可选）：传递给脚本的命令行参数
- `timeout`（可选）：在没有新输出时等待的秒数（默认：5.0）。只要有新输出，就会继续等待。
- `env`（可选）：为调试会话设置的环境变量（例如，{"DEBUG": "1"}）

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
- `args`（必需）：在 'pytest --pdb' 之后传递的参数。可以包括测试路径、过滤器和 pytest 选项（例如，"tests/test_example.py -v"、"-k test_login"、"-x test_auth.py"）
- `python_path`（必需）：用于调试项目的 Python 解释器路径
- `working_directory`（必需）：运行命令的目录（应该是项目目录）
- `timeout`（可选）：在没有新输出时等待的秒数（默认：10.0）。只要有新输出，就会继续等待。
- `env`（可选）：为调试会话设置的环境变量（例如，{"DEBUG": "1"}）

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
- `timeout`（可选）：在没有新输出时等待的秒数（默认：5.0）

**可用命令：**
- `n` (next)：执行下一行（不进入函数内部）
- `s` (step)：执行下一行（进入函数内部）
- `b <line>`：在指定行设置断点（例如，`b 10`）
- `b <file>:<line>`：在其他文件中设置断点（例如，`b utils.py:5`）
- `l` (list)：显示当前行周围的代码
- `p <var>`：打印变量值（例如，`p user_name`）
- `c` (continue)：继续执行直到下一个断点
- `q` (quit)：退出调试会话
- `h` (help)：显示所有命令的帮助
- `r` (return)：执行直到当前函数返回
- `w` (where)：显示调用栈
- `cl <breakpoint>`：清除断点
- `a` (args)：打印当前函数的参数

**示例：**
```json
{
  "command": "n"
}
```

## 测试

### 基本脚本调试

提供了一个示例测试脚本：`test_script.py`

运行自动化测试：
```bash
uv run python test_mcp_client.py
```

示例调试工作流：
1. 启动调试：使用 `script_path = "test_script.py"` 调用 `start_debug`
2. 单步执行：使用 `command = "n"` 调用 `execute_pdb_command`
3. 查看代码：使用 `command = "l"` 调用 `execute_pdb_command`
4. 打印变量：使用 `command = "p num"` 调用 `execute_pdb_command`
5. 继续执行：使用 `command = "c"` 调用 `execute_pdb_command`
6. 退出：使用 `command = "q"` 调用 `execute_pdb_command`

### Pytest 调试

提供了一个示例测试文件：`test_example.py`

运行 pytest 调试测试：
```bash
uv run python test_pytest_client.py
```

测试将：
1. 使用 `-x --pdb` 标志运行 pytest
2. 在第一个失败的测试处停止
3. 在断言失败时进入 pdb
4. 允许你检查变量和调试

## 配置

要与 Claude Desktop 或其他 MCP 客户端一起使用，请将以下内容添加到配置文件中（例如，`claude_desktop_config.json`）：

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

将 `/path/to/pdb-mcp` 替换为此项目的实际路径。

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
- 自动从虚拟环境检测 Python 解释器

### Python 解释器配置

`python_path` 参数指定**客户端项目**的 Python 解释器（不是服务器的环境）：

- **必需参数**：代理应提供项目的 Python 解释器路径
- **典型值**：
  - `.venv/bin/python` 或 `venv/bin/python`（用于虚拟环境）
  - `/usr/bin/python3`（用于系统 Python）
  - conda 或其他环境的自定义路径
- **回退**：如果未提供或为空，则回退到 `"python"` 命令（使用系统 PATH）

**注意：** 服务器不使用自己的 Python（`sys.executable`），因为 MCP 服务器可能运行在与被调试的客户端项目不同的环境中。

### 工作目录配置

`start_debug` 和 `start_pytest_debug` 都需要 `working_directory` 参数：

- **必需参数**：应该是项目的根目录或包含脚本的目录
- **目的**：确保脚本在正确的目录上下文中运行
- **使用场景**：
  - 使用相对文件路径的脚本
  - 具有特定目录结构要求的项目
  - 从项目根目录加载配置文件
- **代理集成**：代理（如 Claude）通常知道项目目录并应提供它

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

- **单一超时参数**：在没有新输出时等待的时间
- **无总时间限制**：只要有新输出，服务器就会继续等待
- **自适应**：快速命令快速返回，慢速命令获得所需的时间
- **用户可配置**：所有工具都接受 `timeout` 参数

**工作原理：**
1. 服务器每 0.1 秒持续检查输出
2. 每次新输出到达时，空闲计时器重置
3. 当没有新输出超过 `timeout` 秒时，返回
4. 无论脚本运行多长时间，只要它持续产生输出，服务器就会等待

**默认超时值：**
- `start_debug`：5.0 秒（pdb 通常启动很快）
- `start_pytest_debug`：10.0 秒（测试可能产生输出较慢）
- `execute_pdb_command`：5.0 秒（大多数命令很快）

**示例：** 一个运行 10 秒但每 0.5 秒打印一次的脚本，使用 `timeout=3.0` 可以正常工作，因为空闲时间永远不会超过 3 秒。

## 许可证

详见 LICENSE 文件。
