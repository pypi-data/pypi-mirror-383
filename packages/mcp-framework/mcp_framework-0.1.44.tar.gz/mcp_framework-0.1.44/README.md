# MCP Framework

一个强大且易用的 MCP (Model Context Protocol) 服务器开发框架，支持快速构建、部署和管理 MCP 服务器。

使用该框架开发的mcp_servers: https://github.com/leeoohoo/mcp_servers

## 🚀 特性

### 核心功能
- **简单易用**: 基于装饰器的 API 设计，快速定义工具和资源
- **类型安全**: 完整的类型注解支持，自动生成 JSON Schema
- **角色过滤**: 支持为工具指定角色，实现基于角色的工具过滤和访问控制
- **流式支持**: 内置流式响应支持，适合大数据量处理
- **配置管理**: 灵活的配置系统，支持多端口配置
- **自动构建**: 集成 PyInstaller 构建系统，一键生成可执行文件

### 高级特性
- **多平台支持**: Windows、macOS、Linux 跨平台构建
- **依赖管理**: 智能依赖分析和打包
- **热重载**: 开发模式下支持代码热重载
- **日志系统**: 完整的日志记录和调试支持
- **Web 界面**: 内置配置和测试 Web 界面

## 📦 安装

### 从 PyPI 安装

```bash
pip install mcp-framework
```

### 从源码安装

```bash
git clone https://github.com/your-repo/mcp_framework.git
cd mcp_framework
pip install -e .
```

## 🎯 快速开始

### 1. 创建基础服务器

```python
#!/usr/bin/env python3
import asyncio
from mcp_framework import EnhancedMCPServer, run_server_main
from mcp_framework.core.decorators import Required, Optional
from typing import Annotated


class MyMCPServer(EnhancedMCPServer):
    """我的第一个 MCP 服务器"""
    
    def __init__(self):
        super().__init__(
            name="MyMCPServer",
            version="1.0.0",
            description="我的第一个 MCP 服务器"
        )
    
    async def initialize(self):
        """初始化服务器"""
        self.logger.info("MyMCPServer 初始化完成")
    
    @property
    def setup_tools(self):
        """设置工具和资源"""
        
        # 使用装饰器定义工具
        @self.tool("计算两个数的和")
        async def add_numbers(
            a: Annotated[int, Required("第一个数字")],
            b: Annotated[int, Required("第二个数字")]
        ) -> int:
            """计算两个数字的和"""
            return a + b
        
        # 带角色的工具示例
        @self.tool("数据分析", role="analyst")
        async def analyze_data(
            data: Annotated[str, Required("要分析的数据")]
        ) -> str:
            """分析数据"""
            return f"分析结果: {data}"
        
        # 定义流式工具
        @self.streaming_tool("生成数字序列")
        async def generate_sequence(
            start: Annotated[int, Required("起始数字")],
            end: Annotated[int, Required("结束数字")]
        ):
            """生成数字序列"""
            for i in range(start, end + 1):
                yield f"数字: {i}"
                await asyncio.sleep(0.1)  # 模拟处理时间
        
        # 带角色的流式工具
        @self.streaming_tool("分析数据流", role="analyst")
        async def analyze_data_stream(
            data: Annotated[str, Required("要分析的数据")]
        ):
            """流式分析数据 - 仅限analyst角色"""
            steps = ["数据预处理", "特征提取", "模式识别", "结果生成"]
            for step in steps:
                yield f"{step}: {data}"
                await asyncio.sleep(0.5)
        
        # 定义资源
        @self.resource(
            uri="file://data.txt",
            name="示例数据",
            description="示例数据文件"
        )
        async def get_data():
            return {"content": "这是示例数据", "type": "text/plain"}


# 启动服务器
if __name__ == "__main__":
    server = MyMCPServer()
    run_server_main(
        server_instance=server,
        server_name="MyMCPServer",
        default_port=8080
    )
```

### 2. 运行服务器

```bash
python my_server.py --port 8080 --host localhost
```

## 🌐 Flask 项目集成

### 概述

MCP Framework 可以无缝集成到现有的 Flask 项目中，实现传统 REST API 和 AI 友好的 MCP 工具并存的架构。这种设计允许你的 Flask 应用同时为 Web 前端和 AI 代理提供服务。

### 集成特点

- **双重接口设计**: 同一业务逻辑支持 REST API 和 MCP 工具两种访问方式
- **代码复用**: 核心业务逻辑只需实现一次
- **架构清晰**: 服务层、路由层分离，易于维护
- **AI 友好**: 自动为 AI 代理提供工具接口
- **向后兼容**: 不影响现有 Flask 应用

### 项目结构

```
flask_project/
├── app/
│   ├── __init__.py              # Flask应用工厂
│   ├── mcp_config.py            # MCP服务器配置
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py      # 用户服务 + MCP工具
│   │   └── product_service.py   # 产品服务 + MCP工具
│   └── routes/
│       ├── __init__.py
│       └── api.py               # Flask REST API路由
├── run.py                       # 主启动文件
├── requirements.txt             # 项目依赖
└── README.md                    # 项目说明
```

### 集成步骤

#### 1. 安装依赖

```bash
pip install mcp-framework flask
```

#### 2. 创建 MCP 配置文件

创建 `app/mcp_config.py`：

```python
#!/usr/bin/env python3
from mcp_framework import EnhancedMCPServer
from typing import Annotated
from mcp_framework.core.decorators import Required

class FlaskIntegratedMCPServer(EnhancedMCPServer):
    """Flask集成的MCP服务器"""
    
    def __init__(self, user_service=None, product_service=None):
        super().__init__(
            name="flask-integrated-mcp-server",
            version="1.0.0",
            description="Flask应用集成的MCP服务器"
        )
        self.user_service = user_service
        self.product_service = product_service
    
    async def initialize(self):
        """初始化服务器"""
        self.logger.info("Flask集成MCP服务器初始化完成")
    
    def set_services(self, user_service, product_service):
        """设置服务实例"""
        self.user_service = user_service
        self.product_service = product_service
```

#### 3. 创建服务层

创建 `app/services/user_service.py`：

```python
#!/usr/bin/env python3
import time
from typing import Dict, List, Any, Annotated
from mcp_framework.core.decorators import Required

class UserService:
    """用户服务类"""
    
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.users_db = {}  # 模拟数据库
        self._init_sample_data()
        self._register_mcp_tools()
    
    def _init_sample_data(self):
        """初始化示例数据"""
        self.users_db = {
            1: {"id": 1, "name": "张三", "email": "zhang@example.com", "role": "admin"},
            2: {"id": 2, "name": "李四", "email": "li@example.com", "role": "user"}
        }
    
    def _register_mcp_tools(self):
        """注册MCP工具"""
        
        @self.mcp_server.tool("获取用户信息")
        async def get_user_info(
            user_id: Annotated[int, Required("用户ID，必须是正整数")]
        ) -> Dict[str, Any]:
            """根据用户ID获取用户详细信息"""
            user = self.get_user_by_id(user_id)
            if user:
                return {
                    "success": True,
                    "user": user,
                    "timestamp": time.time()
                }
            else:
                return {
                    "success": False,
                    "error": f"用户 {user_id} 不存在",
                    "timestamp": time.time()
                }
        
        @self.mcp_server.tool("获取所有用户")
        async def get_all_users() -> Dict[str, Any]:
            """获取所有用户列表"""
            return {
                "success": True,
                "users": list(self.users_db.values()),
                "total": len(self.users_db),
                "timestamp": time.time()
            }
    
    # Flask服务方法（非MCP工具）
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Flask路由使用的方法"""
        return self.users_db.get(user_id)
    
    def get_all_users_list(self) -> List[Dict[str, Any]]:
        """Flask路由使用的方法"""
        return list(self.users_db.values())
```

#### 4. 创建 Flask 应用工厂

创建 `app/__init__.py`：

```python
#!/usr/bin/env python3
from flask import Flask
from .mcp_config import FlaskIntegratedMCPServer
from .services.user_service import UserService
from .services.product_service import ProductService
from .routes.api import api_bp

def create_app():
    """Flask应用工厂"""
    app = Flask(__name__)
    
    # 创建MCP服务器实例
    mcp_server = FlaskIntegratedMCPServer()
    
    # 创建服务实例
    user_service = UserService(mcp_server)
    product_service = ProductService(mcp_server)
    
    # 设置服务到MCP服务器
    mcp_server.set_services(user_service, product_service)
    
    # 将服务实例添加到Flask应用上下文
    app.user_service = user_service
    app.product_service = product_service
    app.mcp_server = mcp_server
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            "message": "Flask + MCP Framework 集成示例",
            "flask_api": "http://localhost:5001/api",
            "mcp_server": "http://localhost:8080",
            "endpoints": {
                "users": "/api/users",
                "products": "/api/products",
                "mcp_tools": "http://localhost:8080/tools/list"
            }
        }
    
    return app
```

#### 5. 创建 Flask 路由

创建 `app/routes/api.py`：

```python
#!/usr/bin/env python3
from flask import Blueprint, jsonify, request, current_app

api_bp = Blueprint('api', __name__)

@api_bp.route('/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    users = current_app.user_service.get_all_users_list()
    return jsonify({"users": users, "total": len(users)})

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = current_app.user_service.get_user_by_id(user_id)
    if user:
        return jsonify({"user": user})
    else:
        return jsonify({"error": "用户不存在"}), 404

@api_bp.route('/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    category = request.args.get('category', 'all')
    if category == 'all':
        products = current_app.product_service.get_all_products()
    else:
        products = [p for p in current_app.product_service.get_all_products() 
                   if p.get('category') == category]
    return jsonify({"products": products, "total": len(products)})
```

#### 6. 创建启动文件

创建 `run.py`：

```python
#!/usr/bin/env python3
import threading
import time
from app import create_app
from mcp_framework import run_server_main

def run_flask_app():
    """运行Flask应用"""
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

def run_mcp_server():
    """运行MCP服务器"""
    app = create_app()
    mcp_server = app.mcp_server
    
    run_server_main(
        server_instance=mcp_server,
        server_name="flask-integrated-mcp-server",
        default_port=8080
    )

if __name__ == "__main__":
    print("启动 Flask + MCP 集成服务...")
    
    # 在单独线程中启动Flask应用
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # 等待Flask启动
    time.sleep(2)
    print("Flask API 已启动: http://localhost:5001")
    
    # 在主线程中启动MCP服务器
    print("启动 MCP 服务器: http://localhost:8080")
    run_mcp_server()
```

### 使用示例

#### Flask REST API 调用

```bash
# 获取所有用户
curl http://localhost:5001/api/users

# 获取单个用户
curl http://localhost:5001/api/users/1

# 获取产品列表
curl http://localhost:5001/api/products

# 按分类获取产品
curl "http://localhost:5001/api/products?category=electronics"
```

#### MCP 工具调用

```bash
# 获取可用工具列表
curl http://localhost:8080/tools/list

# 调用用户相关工具
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_user_info", "arguments": {"user_id": 1}}}'

# 调用产品相关工具
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_products_list", "arguments": {"category": "electronics"}}}'
```

### 集成优势

1. **代码复用**: 同一业务逻辑支持多种访问方式
2. **架构清晰**: 服务层、路由层分离，职责明确
3. **易于扩展**: 新增功能只需在服务层实现
4. **AI 友好**: 自动为 AI 代理提供工具接口
5. **向后兼容**: 不影响现有 Flask 应用的功能
6. **双重服务**: Web 应用和 AI 代理可以共享同一套业务逻辑

### 注意事项

1. **端口管理**: 确保 Flask 和 MCP 服务器使用不同端口
2. **线程安全**: 注意共享数据的线程安全性
3. **错误处理**: 在生产环境中完善错误处理机制
4. **性能优化**: 根据需要添加缓存和连接池
5. **安全考虑**: 在生产环境中添加认证和授权

### 完整示例

完整的 Flask 集成示例项目可以在 `flask_project_structure_example/` 目录中找到，包含了完整的项目结构、配置文件和详细的使用说明。

## 📚 详细文档

### 装饰器 API

#### 工具装饰器

```python
# 使用 @property 装饰器定义工具
@property
def setup_tools(self):
    # 基础工具
    @self.tool("工具描述")
    async def my_tool(param1: str, param2: int) -> str:
        return f"处理结果: {param1} - {param2}"
    
    # 单角色工具
    @self.tool("规划任务", role="planner")
    async def plan_task(task: str) -> str:
        return f"任务规划: {task}"
    
    # 多角色工具（支持数组格式）
    @self.tool("执行任务", role=["executor", "manager"])
    async def execute_task(task: str) -> str:
        return f"执行任务: {task}"
    
    @self.tool("审核任务", role=["manager", "supervisor", "admin"])
    async def review_task(task: str) -> str:
        return f"审核任务: {task}"
    
    # 通用工具（无角色限制）
    @self.tool("获取状态")
    async def get_status() -> str:
        return "服务器运行正常"
    
    # 流式工具
    @self.streaming_tool("流式工具描述")
    async def my_streaming_tool(query: str):
        for i in range(10):
            yield f"处理步骤 {i}: {query}"
            await asyncio.sleep(0.1)
    
    # 单角色流式工具
    @self.streaming_tool("分析数据流", role="analyst")
    async def analyze_data_stream(data: str):
        for step in ["预处理", "分析", "总结"]:
            yield f"{step}: {data}"
            await asyncio.sleep(0.5)
    
    # 多角色流式工具
    @self.streaming_tool("监控进度", role=["manager", "supervisor"])
    async def monitor_progress(project: str):
        for stage in ["初始化", "执行中", "完成"]:
            yield f"项目 {project} - {stage}"
            await asyncio.sleep(0.3)
```

#### 角色过滤功能

框架支持为工具指定角色（role），实现基于角色的工具过滤和访问控制：

**装饰器参数**：
- `role`: 可选参数，支持以下格式：
  - 单个角色：`role="planner"`
  - 多个角色：`role=["executor", "manager"]`
  - 不指定 `role` 的工具为通用工具，对所有角色可见

**角色配置示例**：
```python
# 单角色工具
@self.tool("规划任务", role="planner")
async def plan_task(task: str):
    return f"任务规划: {task}"

# 多角色工具 - executor和manager都可以使用
@self.tool("执行任务", role=["executor", "manager"])
async def execute_task(task: str):
    return f"执行任务: {task}"

# 通用工具 - 所有角色都可以使用
@self.tool("获取状态")
async def get_status():
    return "服务器运行正常"
```

**API 调用**：
```bash
# HTTP API - 获取所有工具
curl http://localhost:8080/tools/list

# HTTP API - 获取特定角色的工具
curl "http://localhost:8080/tools/list?role=planner"

# MCP 协议 - 获取特定角色的工具
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"role": "executor"}}' \
  http://localhost:8080/mcp
```

**过滤规则**：
- 指定角色时：返回包含该角色的工具 + 通用工具（无角色）
  - 单角色工具：`role="planner"` 只对 planner 角色可见
  - 多角色工具：`role=["executor", "manager"]` 对 executor 和 manager 角色都可见
  - 通用工具：无 `role` 参数的工具对所有角色可见
- 不指定角色时：返回所有工具
- 支持 HTTP API 和 MCP 协议两种调用方式

**示例场景**：
```python
# 假设有以下工具配置：
@self.tool("规划任务", role="planner")           # 只有 planner 可见
@self.tool("执行任务", role=["executor", "manager"])  # executor 和 manager 可见
@self.tool("获取状态")                          # 所有角色可见

# 当请求 role="executor" 时，返回：
# - 执行任务（因为 executor 在角色列表中）
# - 获取状态（通用工具）

# 当请求 role="manager" 时，返回：
# - 执行任务（因为 manager 在角色列表中）
# - 获取状态（通用工具）
```

#### 参数类型注解

```python
from typing import List, Optional, AsyncGenerator
from typing_extensions import Annotated
from mcp_framework.core.decorators import (
    Required as R,
    Optional as O,
    IntRange,
    ServerParam,
    StringParam,
    BooleanParam,
    PathParam
)

# 使用 @property 装饰器定义
@property
def setup_tools(self):
    # 流式工具参数示例
    @self.streaming_tool(description="📖 **File Line Range Reader** - 流式读取文件指定行范围")
    async def read_file_lines(
        file_path: Annotated[str, R("文件路径（支持相对和绝对路径）")],
        start_line: Annotated[int, IntRange("起始行号（1-based）", min_val=1)],
        end_line: Annotated[int, IntRange("结束行号（1-based，包含）", min_val=1)]
    ) -> AsyncGenerator[str, None]:
        """流式读取文件指定行范围"""
        # 实现代码...
        yield "result"
    
    # 搜索工具参数示例
    @self.tool(description="🔍 **Content Search** - 搜索文件内容")
    async def search_files(
        query_text: Annotated[str, R("搜索关键词")],
        limit: Annotated[int, O("最大结果数量", default=50, minimum=1)] = 50,
        case_sensitive: Annotated[bool, O("是否区分大小写", default=False)] = False,
        file_extensions: Annotated[Optional[List[str]], O("文件扩展名列表，如 ['.py', '.js']")] = None
    ) -> dict:
        """搜索文件内容"""
        return {"results": []}
```

#### 资源装饰器

```python
import json

# 使用 @property 装饰器定义
@property
def setup_tools(self):
    @self.resource(
        uri="file://config.json",
        name="配置文件",
        description="服务器配置文件",
        mime_type="application/json"
    )
    async def get_config():
        return {
            "content": json.dumps({"setting1": "value1"}),
            "type": "application/json"
        }
```

### 服务器配置

#### 配置参数定义

```python
from mcp_framework.core.decorators import (
    ServerParam,
    StringParam,
    SelectParam,
    BooleanParam,
    PathParam
)
from typing import Annotated

# 使用 @property 装饰器定义
@property
def setup_server_params(self):
    @self.decorators.server_param("api_key")
    async def api_key_param(
        param: Annotated[str, StringParam(
            display_name="API 密钥",
            description="用于访问外部服务的 API 密钥",
            placeholder="请输入 API 密钥"
        )]
    ):
        """API 密钥参数"""
        pass
    
    @self.decorators.server_param("model_type")
    async def model_param(
        param: Annotated[str, SelectParam(
            display_name="模型类型",
            description="选择要使用的 AI 模型",
            options=["gpt-3.5-turbo", "gpt-4", "claude-3"]
        )]
    ):
        """模型类型参数"""
        pass
    
    @self.decorators.server_param("project_root")
    async def project_root_param(
        param: Annotated[str, PathParam(
            display_name="项目根目录",
            description="服务器操作的根目录路径，留空使用当前目录",
            required=False,
            placeholder="/path/to/project"
        )]
    ):
        """项目根目录参数"""
        pass
    
    @self.decorators.server_param("max_file_size")
    async def max_file_size_param(
        param: Annotated[int, ServerParam(
            display_name="最大文件大小 (MB)",
            description="允许读取的最大文件大小，单位MB",
            param_type="integer",
            default_value=10,
            required=False
        )]
    ):
        """最大文件大小参数"""
        pass
    
    @self.decorators.server_param("enable_hidden_files")
    async def enable_hidden_files_param(
        param: Annotated[bool, BooleanParam(
            display_name="启用隐藏文件",
            description="是否允许访问以点(.)开头的隐藏文件",
            default_value=False,
            required=False
        )]
    ):
        """启用隐藏文件参数
        
        这个装饰器的作用：
        1. 定义一个名为 'enable_hidden_files' 的服务器配置参数
        2. 参数类型为布尔值（BooleanParam）
        3. 在Web配置界面中显示为"启用隐藏文件"选项
        4. 用户可以通过配置界面或配置文件设置此参数
        5. 在工具函数中可通过 self.get_config_value("enable_hidden_files") 获取值
        
        参数说明：
        - display_name: 在配置界面显示的友好名称
        - description: 参数的详细说明
        - default_value: 默认值（False表示默认不启用隐藏文件）
        - required: 是否为必需参数（False表示可选）
        """
        pass
```

#### 配置使用

```python
from mcp_framework.core.decorators import Required
from typing import Annotated

# 在 setup_tools 方法中定义
@property
def setup_tools(self):
    @self.tool("使用配置的工具")
    async def configured_tool(query: Annotated[str, Required("查询内容")]):
        # 获取配置值
        api_key = self.get_config_value("api_key")
        model_type = self.get_config_value("model_type", "gpt-3.5-turbo")
        enable_hidden = self.get_config_value("enable_hidden_files", False)
        
        # 使用配置进行处理
        result = f"使用 {model_type} 处理查询: {query}"
        if enable_hidden:
            result += " (包含隐藏文件)"
        return result
```

#### 服务器参数装饰器详解

服务器参数装饰器 `@self.decorators.server_param()` 是 MCP Framework 的核心功能之一，它允许你为服务器定义可配置的参数。

**工作原理：**

1. **参数定义阶段**：使用装饰器定义参数的元数据（名称、类型、默认值等）
2. **配置收集阶段**：框架自动生成配置界面，用户可以设置参数值
3. **运行时使用**：在工具函数中通过 `self.get_config_value()` 获取用户设置的值

**完整示例：**

```python
# 1. 定义参数（在 setup_server_params 方法中）
@property
def setup_server_params(self):
    @self.decorators.server_param("enable_hidden_files")
async def enable_hidden_files_param(
    param: Annotated[bool, BooleanParam(
        display_name="启用隐藏文件",
        description="是否允许访问以点(.)开头的隐藏文件",
        default_value=False,
        required=False
    )]
):
    """定义是否启用隐藏文件的配置参数"""
    pass

# 2. 在工具中使用参数
@self.tool("列出文件")
async def list_files(directory: Annotated[str, Required("目录路径")]):
    # 获取用户配置的参数值
    show_hidden = self.get_config_value("enable_hidden_files", False)
    
    files = []
    for file in os.listdir(directory):
        # 根据配置决定是否包含隐藏文件
        if not show_hidden and file.startswith('.'):
            continue
        files.append(file)
    
    return {"files": files, "show_hidden": show_hidden}
```

**参数类型支持：**

- `StringParam`: 字符串参数
- `BooleanParam`: 布尔参数
- `SelectParam`: 选择参数（下拉菜单）
- `PathParam`: 路径参数
- `ServerParam`: 通用参数（可指定类型）

**配置文件生成：**

框架会自动生成配置文件（如 `server_port_8080_config.json`），用户的设置会保存在其中：

```json
{
  "enable_hidden_files": true,
  "api_key": "your-api-key",
  "model_type": "gpt-4"
}
```

### 多端口配置

框架支持为不同端口创建独立的配置文件：

```bash
# 在不同端口启动服务器，会自动创建对应的配置文件
python server.py --port 8080  # 创建 server_port_8080_config.json
python server.py --port 8081  # 创建 server_port_8081_config.json
```

## 🔨 构建系统

框架集成了强大的构建系统，支持将 MCP 服务器打包为独立的可执行文件。

### 构建功能特性

- **自动发现**: 自动发现项目中的所有服务器脚本
- **依赖分析**: 智能分析和收集依赖包
- **多平台构建**: 支持 Windows、macOS、Linux
- **虚拟环境隔离**: 为每个服务器创建独立的构建环境
- **完整打包**: 生成包含所有依赖的分发包

### 使用构建系统

#### 1. 准备构建脚本

在项目根目录创建 `build.py`（或使用框架提供的构建脚本）：

```python
#!/usr/bin/env python3
from mcp_framework.build import MCPServerBuilder

if __name__ == "__main__":
    builder = MCPServerBuilder()
    builder.build_all()
```

#### 2. 构建命令

##### 使用 mcp-build 命令行工具（推荐）

框架提供了专门的 `mcp-build` 命令行工具，简化构建过程：

```bash
# 基础构建命令
mcp-build                           # 构建所有发现的服务器
mcp-build --server my_server.py     # 构建特定服务器
mcp-build --list                    # 列出所有可构建的服务器

# 构建选项
mcp-build --no-clean               # 跳过清理构建目录
mcp-build --no-test                # 跳过测试阶段
mcp-build --no-onefile             # 构建为目录而非单文件
mcp-build --include-source         # 在分发包中包含源代码
mcp-build --clean-only             # 只清理构建目录，不进行构建

# 组合使用
mcp-build --server weather_server.py --no-test --include-source
```

**mcp-build 命令详细说明：**

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--server` | `-s` | 指定要构建的服务器脚本 | `mcp-build -s my_server.py` |
| `--list` | `-l` | 列出所有可构建的服务器 | `mcp-build -l` |
| `--no-clean` | | 跳过构建前的清理步骤 | `mcp-build --no-clean` |
| `--no-test` | | 跳过构建后的测试验证 | `mcp-build --no-test` |
| `--no-onefile` | | 构建为目录而非单个可执行文件 | `mcp-build --no-onefile` |
| `--include-source` | | 在分发包中包含源代码 | `mcp-build --include-source` |
| `--clean-only` | | 只清理构建目录，不执行构建 | `mcp-build --clean-only` |

**构建流程说明：**

1. **发现阶段**: 自动扫描项目目录，发现所有 MCP 服务器脚本
2. **清理阶段**: 清理之前的构建文件（可通过 `--no-clean` 跳过）
3. **依赖分析**: 分析每个服务器的依赖包，包括：
   - 通用依赖 (`requirements.txt`)
   - 服务器特定依赖 (`{server_name}_requirements.txt`)
   - 代码中导入的本地模块
4. **构建阶段**: 使用 PyInstaller 构建可执行文件
5. **测试阶段**: 验证构建的可执行文件能正常启动（可通过 `--no-test` 跳过）
6. **打包阶段**: 创建包含所有必要文件的分发包

##### 使用 Python 脚本构建（传统方式）

```bash
# 构建所有服务器
python build.py

# 构建特定服务器
python build.py --server my_server.py

# 列出所有可构建的服务器
python build.py --list

# 只清理构建目录
python build.py --clean-only

# 跳过测试
python build.py --no-test

# 包含源代码
python build.py --include-source
```

#### 3. 构建输出

构建完成后，会在 `dist/` 目录生成分发包：

```
dist/
├── my-server-macos-arm64-20241201_143022.tar.gz
├── weather-server-macos-arm64-20241201_143025.tar.gz
└── ...
```

每个分发包包含：
- 可执行文件
- 完整的 requirements.txt
- 启动脚本（start.sh / start.bat）
- README 和许可证文件
- 源代码（如果指定 --include-source）

### 跨平台构建

框架支持跨平台构建，可以在一个平台上构建其他平台的可执行文件：

#### 使用 mcp-build 进行跨平台构建

```bash
# 构建所有平台版本（需要 Docker）
mcp-build --platform all

# 构建特定平台
mcp-build --platform windows      # 构建 Windows 版本
mcp-build --platform linux        # 构建 Linux 版本
mcp-build --platform native       # 构建当前平台版本

# 跨平台构建特定服务器
mcp-build --platform windows --server my_server.py

# 检查 Docker 环境
mcp-build --check-docker
```

#### 跨平台构建要求

- **Docker Desktop**: 用于跨平台构建（Windows 和 Linux）
- **本地构建**: 不需要 Docker，只构建当前平台

#### 便捷脚本

框架还提供了便捷的构建脚本：

```bash
# 使用跨平台构建脚本
python build_cross_platform.py --platform all

# 使用 Windows 构建脚本（仅限 Windows 构建）
./build_windows.sh

# 使用 Docker Compose
docker-compose --profile build up build-windows
docker-compose --profile build up build-linux
```

### 依赖管理

构建系统支持多层依赖管理：

1. **通用依赖** (`requirements.txt`): 所有服务器共享的依赖
2. **特定依赖** (`{server_name}_requirements.txt`): 特定服务器的依赖
3. **自动分析**: 从代码中自动分析导入的包

示例文件结构：
```
project/
├── requirements.txt              # 通用依赖
├── weather_server.py
├── weather_server_requirements.txt  # weather_server 特定依赖
├── chat_server.py
├── chat_server_requirements.txt     # chat_server 特定依赖
├── build.py                      # 构建脚本
├── build_cross_platform.py      # 跨平台构建脚本
└── build_windows.sh              # Windows 构建便捷脚本
```

### 构建输出详解

构建完成后，分发包的详细结构：

```
dist/
├── my-server-macos-arm64-20241201_143022.tar.gz
│   ├── my-server                 # 可执行文件
│   ├── start.sh                  # Unix 启动脚本
│   ├── start.bat                 # Windows 启动脚本
│   ├── requirements.txt          # 依赖列表
│   ├── README.md                 # 使用说明
│   ├── LICENSE                   # 许可证文件
│   └── src/                      # 源代码（如果使用 --include-source）
├── my-server-windows-amd64-20241201_143025.zip
└── my-server-linux-x86_64-20241201_143028.tar.gz
```

**分发包特性：**

- **独立运行**: 包含所有必要的依赖，无需额外安装
- **跨平台**: 支持 Windows、macOS、Linux
- **便捷启动**: 提供启动脚本，简化运行过程
- **完整文档**: 包含 README 和许可证文件
- **源码可选**: 可选择是否包含源代码

### mcp-build 使用示例和最佳实践

#### 典型工作流程

```bash
# 1. 开发阶段：列出所有可构建的服务器
mcp-build --list

# 输出示例：
# 📋 Available server scripts:
#    - weather_server.py → Weather MCP Server
#    - chat_server.py → AI Chat Assistant
#    - file_manager.py → File Management Server

# 2. 测试构建：构建特定服务器（快速验证）
mcp-build --server weather_server.py --no-test

# 3. 完整构建：包含测试和源码
mcp-build --server weather_server.py --include-source

# 4. 生产构建：构建所有服务器
mcp-build

# 5. 跨平台发布：构建所有平台版本
mcp-build --platform all
```

#### 常见使用场景

**场景1：快速开发测试**
```bash
# 跳过测试，快速构建验证
mcp-build --server my_server.py --no-test --no-clean
```

**场景2：CI/CD 集成**
```bash
# 适合自动化构建的命令
mcp-build --no-test --include-source
```

**场景3：发布准备**
```bash
# 完整构建，包含所有验证
mcp-build --platform all --include-source
```

**场景4：调试构建问题**
```bash
# 只清理，不构建
mcp-build --clean-only

# 保留构建文件，便于调试
mcp-build --server my_server.py --no-clean
```

#### 构建优化建议

1. **依赖管理优化**
   ```bash
   # 为每个服务器创建特定的依赖文件
   # weather_server_requirements.txt
   requests>=2.28.0
   beautifulsoup4>=4.11.0
   
   # chat_server_requirements.txt  
   openai>=1.0.0
   langchain>=0.1.0
   ```

2. **构建性能优化**
   ```bash
   # 跳过不必要的步骤
   mcp-build --no-test --no-clean  # 开发阶段
   
   # 只构建变更的服务器
   mcp-build --server changed_server.py
   ```

3. **分发包优化**
   ```bash
   # 生产环境：不包含源码，减小包大小
   mcp-build
   
   # 开发分发：包含源码，便于调试
   mcp-build --include-source
   ```

#### 错误排查

**常见问题及解决方案：**

1. **Docker 不可用**
   ```bash
   # 检查 Docker 状态
   mcp-build --check-docker
   
   # 如果 Docker 不可用，只构建本地平台
   mcp-build --platform native
   ```

2. **依赖冲突**
   ```bash
   # 清理构建缓存
   mcp-build --clean-only
   
   # 重新构建
   mcp-build --server problematic_server.py
   ```

3. **构建失败**
   ```bash
   # 跳过测试，查看构建是否成功
   mcp-build --server my_server.py --no-test
   
   # 保留构建文件，手动检查
   mcp-build --server my_server.py --no-clean
   ```

#### 高级用法

**自定义构建脚本集成**
```python
#!/usr/bin/env python3
# custom_build.py
from mcp_framework.build import MCPServerBuilder
import subprocess

def custom_build():
    # 预处理
    print("🔧 Running custom pre-build steps...")
    
    # 使用 mcp-build
    result = subprocess.run([
        "mcp-build", 
        "--server", "my_server.py",
        "--include-source"
    ])
    
    if result.returncode == 0:
        print("✅ Build successful!")
        # 后处理
        print("📦 Running custom post-build steps...")
    else:
        print("❌ Build failed!")
        return False
    
    return True

if __name__ == "__main__":
    custom_build()
```

**批量构建脚本**
```bash
#!/bin/bash
# batch_build.sh

echo "🚀 Starting batch build process..."

# 构建开发版本
echo "📦 Building development versions..."
mcp-build --include-source

# 构建生产版本
echo "🏭 Building production versions..."
mcp-build --platform all

echo "✅ Batch build completed!"
echo "📁 Check dist/ directory for all packages"
ls -la dist/
```

## 🌐 Web 界面

框架提供内置的 Web 管理界面：

```python
from mcp_framework import EnhancedMCPServer
from mcp_framework.web import setup_web_interface

# 在服务器类中启用 Web 界面
class MyMCPServer(EnhancedMCPServer):
    def __init__(self):
        super().__init__(name="MyServer", version="1.0.0")
        # 启用 Web 界面
        setup_web_interface(self, port=8080)
```

访问 `http://localhost:8080/config` 进行配置管理。

## 🔧 高级用法


### 中间件支持

框架提供了中间件系统，用于处理HTTP请求的预处理和后处理。中间件在请求到达具体处理函数之前或响应返回给客户端之前执行特定的逻辑。

#### 内置中间件

框架自动集成了以下核心中间件：

**1. CORS 中间件 (`cors_middleware`)**
- **功能**: 处理跨域资源共享
- **用途**: 允许Web界面从不同域名访问MCP服务器
- **自动配置**: 支持所有常见的HTTP方法和头部

**2. 错误处理中间件 (`error_middleware`)**
- **功能**: 统一处理和格式化错误响应
- **用途**: 捕获异常，记录日志，返回标准化的JSON错误格式
- **安全性**: 避免敏感信息泄露

**3. 日志中间件 (`logging_middleware`)**
- **功能**: 记录HTTP请求的访问日志
- **监控**: 记录请求方法、路径、响应状态码和处理时间
- **调试**: 便于问题排查和性能分析

#### 中间件工作流程

```
请求 → CORS中间件 → 错误处理中间件 → 日志中间件 → 路由处理 → 响应
```

#### 自定义中间件示例

#### 框架中间件实现

框架的中间件在 `MCPHTTPServer` 中自动配置：

```python
from mcp_framework.server.middleware import (
    cors_middleware,
    error_middleware, 
    logging_middleware
)

class MCPHTTPServer:
    def setup_middleware(self):
        """设置中间件"""
        self.app.middlewares.append(cors_middleware)
        self.app.middlewares.append(error_middleware)
        self.app.middlewares.append(logging_middleware)
```

#### 中间件应用场景

**1. 安全控制**
- 跨域资源共享 (CORS)
- 统一错误处理
- 请求日志记录

**2. 监控和调试**
- 请求响应时间统计
- 错误率监控
- 访问日志记录

**3. 自动化处理**
- 响应头标准化
- 错误格式统一
- 请求追踪

#### 使用示例

```python
from mcp_framework import EnhancedMCPServer, run_server_main

class MyMCPServer(EnhancedMCPServer):
    def __init__(self):
        super().__init__(
            name="MyServer", 
            version="1.0.0",
            description="支持内置中间件的MCP服务器"
        )
    
    async def initialize(self):
        """服务器初始化"""
        self.logger.info("服务器启动，内置中间件已自动配置")
        self.logger.info("CORS、错误处理、日志中间件已启用")
    
    @property
    def setup_tools(self):
        @self.tool("测试工具")
        async def test_tool(message: str) -> str:
            """测试中间件功能的工具"""
            return f"处理消息: {message}"

if __name__ == "__main__":
    server = MyMCPServer()
    run_server_main(
        server_instance=server,
        server_name="MyServer",
        default_port=8080
    )
```

#### 中间件效果验证

启动服务器后，可以通过以下方式验证中间件功能：

```bash
# 测试CORS中间件
curl -H "Origin: http://localhost:3000" http://localhost:8080/health

# 测试错误处理中间件
curl http://localhost:8080/nonexistent

# 查看日志中间件输出
# 在服务器日志中会看到请求记录
```

**注意事项：**
- 中间件在HTTP服务器层面自动配置，无需手动注册
- 所有MCP服务器实例都会自动获得这些中间件功能
- 中间件按照固定顺序执行：CORS → 错误处理 → 日志记录
- 当前版本不支持自定义中间件注册（未来版本可能会支持）
#### 中间件应用场景

**1. 安全控制**
- API密钥验证
- 请求频率限制
- IP白名单/黑名单

**2. 监控和调试**
- 请求响应时间统计
- 错误率监控
- 访问日志记录

**3. 数据处理**
- 请求数据预处理
- 响应数据格式化
- 内容压缩

**4. 缓存优化**
- 响应缓存
- 静态资源缓存
- 数据库查询缓存

#### 配置示例

```python
from mcp_framework import EnhancedMCPServer, run_server_main

class MyMCPServer(EnhancedMCPServer):
    def __init__(self):
        super().__init__(
            name="MyServer", 
            version="1.0.0",
            description="支持中间件的MCP服务器"
        )
    
    async def initialize(self):
        """服务器初始化"""
        self.logger.info("服务器启动，中间件已自动配置")
        self.logger.info("CORS、错误处理、日志中间件已启用")
    
    @property
    def setup_tools(self):
        @self.tool("测试工具")
        async def test_tool(message: str) -> str:
            """测试中间件功能的工具"""
            return f"处理消息: {message}"

if __name__ == "__main__":
    server = MyMCPServer()
    run_server_main(
        server_instance=server,
        server_name="MyServer",
        default_port=8080
    )
```

通过访问 `http://localhost:8080/health` 可以看到中间件的工作效果，包括CORS头部、访问日志和错误处理。

## 📖 示例项目

查看 `examples/` 目录中的完整示例：

- `examples/port_config_demo.py` - 端口配置演示
- `examples/weather_server.py` - 天气服务器示例
- `examples/file_manager.py` - 文件管理服务器
- `examples/ai_assistant.py` - AI 助手服务器

### 🧪 测试服务器开发模式

框架支持两种快速测试和原型开发的模式：

#### 方式一：直接装饰器模式（推荐）

```python
#!/usr/bin/env python3
from mcp_framework import EnhancedMCPServer, run_server_main
from mcp_framework.core.decorators import Required
from typing_extensions import Annotated

# 直接创建服务器实例
server = EnhancedMCPServer(
    name="multi-role-test-server",
    version="1.0.0",
    description="测试多角色功能的MCP服务器"
)

# 直接使用装饰器，无需setup_tools包装
@server.tool("规划任务", role="planner")
async def plan_task(task: Annotated[str, Required("要规划的任务")]):
    """规划任务 - 仅限planner角色"""
    return f"任务规划: {task}\n步骤: 1.分析需求 2.制定计划 3.分配资源"

@server.tool("执行任务", role=["executor", "manager"])
async def execute_task(task: Annotated[str, Required("要执行的任务")]):
    """执行任务 - executor和manager角色都可以使用"""
    return f"正在执行任务: {task}\n状态: 进行中\n预计完成时间: 30分钟"

@server.tool("获取状态")
async def get_status():
    """获取服务器状态 - 所有角色都可以使用"""
    return "服务器运行正常，所有功能可用"

if __name__ == "__main__":
    print(f"启动多角色测试服务器...")
    print(f"测试角色过滤:")
    print(f"- 获取planner角色工具: curl 'http://localhost:8080/tools/list?role=planner'")
    print(f"- 获取executor角色工具: curl 'http://localhost:8080/tools/list?role=executor'")
    
    run_server_main(
        server_instance=server,
        server_name="MultiRoleTestServer",
        default_port=8080
    )
```

#### 方式二：setup_tools包装模式（兼容性）

```python
#!/usr/bin/env python3
from mcp_framework import EnhancedMCPServer, run_server_main
from mcp_framework.core.decorators import Required
from typing_extensions import Annotated

# 直接创建服务器实例
server = EnhancedMCPServer(
    name="multi-role-test-server",
    version="1.0.0",
    description="测试多角色功能的MCP服务器"
)

@property
def setup_tools(self):
    # 单角色工具
    @self.tool("规划任务", role="planner")
    async def plan_task(task: Annotated[str, Required("要规划的任务")]):
        """规划任务 - 仅限planner角色"""
        return f"任务规划: {task}\n步骤: 1.分析需求 2.制定计划 3.分配资源"
    
    # 多角色工具 - 使用数组
    @self.tool("执行任务", role=["executor", "manager"])
    async def execute_task(task: Annotated[str, Required("要执行的任务")]):
        """执行任务 - executor和manager角色都可以使用"""
        return f"正在执行任务: {task}\n状态: 进行中\n预计完成时间: 30分钟"
    
    # 通用工具（无角色限制）
    @self.tool("获取状态")
    async def get_status():
        """获取服务器状态 - 所有角色都可以使用"""
        return "服务器运行正常，所有功能可用"

# 绑定setup_tools方法到服务器
server.setup_tools = setup_tools.__get__(server, EnhancedMCPServer)

if __name__ == "__main__":
    print(f"启动多角色测试服务器...")
    print(f"测试角色过滤:")
    print(f"- 获取planner角色工具: curl 'http://localhost:8080/tools/list?role=planner'")
    print(f"- 获取executor角色工具: curl 'http://localhost:8080/tools/list?role=executor'")
    
    run_server_main(
        server_instance=server,
        server_name="MultiRoleTestServer",
        default_port=8080
    )
```

#### 测试服务器开发模式特点

**适用场景：**
- 🧪 **快速原型开发**: 测试新功能和概念验证
- 🔍 **功能验证**: 验证特定功能（如多角色支持）
- 📊 **性能测试**: 创建专门的测试服务器
- 🎯 **单一功能演示**: 专注展示某个特定功能

**开发模式对比：**

| 特性 | 类继承模式 | 直接装饰器模式 | setup_tools模式 |
|------|------------|----------------|------------------|
| **代码结构** | 继承 `EnhancedMCPServer` | 直接实例化+装饰器 | 实例化+方法绑定 |
| **工具定义** | 在类内部使用 `@property` | 直接使用 `@server.tool` | 外部定义后绑定 |
| **适用场景** | 生产环境、复杂应用 | 测试、原型、演示 | 兼容性需求 |
| **代码复用** | 高（可继承扩展） | 低（独立脚本） | 低（独立脚本） |
| **开发速度** | 中等 | 最快 | 快速 |
| **维护性** | 高 | 中等 | 中等 |
| **推荐程度** | 生产环境首选 | 测试开发首选 | 兼容性场景 |

**使用建议：**
- ✅ **生产环境**: 使用类继承模式，便于维护和扩展
- ✅ **快速测试**: 使用直接装饰器模式，代码最简洁
- ✅ **功能演示**: 使用直接装饰器模式，代码直观易懂
- ✅ **学习框架**: 从直接装饰器模式开始，理解框架基本概念
- ✅ **兼容性需求**: 使用setup_tools模式，保持与旧版本兼容

**测试角色过滤功能：**

```bash
# 启动测试服务器
python test_multi_role_server.py

# 测试不同角色的工具过滤
curl 'http://localhost:8080/tools/list?role=planner' | jq
curl 'http://localhost:8080/tools/list?role=executor' | jq
curl 'http://localhost:8080/tools/list?role=manager' | jq

# 获取所有工具
curl 'http://localhost:8080/tools/list' | jq
```

这种开发模式特别适合快速验证框架功能、创建演示脚本或进行功能测试。

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息。

## 🆘 支持

- 📚 [文档](https://mcp-framework.readthedocs.io/)
- 🐛 [问题反馈](https://github.com/your-repo/mcp_framework/issues)
- 💬 [讨论区](https://github.com/your-repo/mcp_framework/discussions)
- 📧 [邮件支持](mailto:support@mcpframework.com)

## 🗺️ 路线图

- [ ] 插件系统
- [ ] 图形化配置界面
- [ ] 集群部署支持
- [ ] 性能监控面板
- [ ] Docker 容器化支持
- [ ] 云原生部署模板

---

**MCP Framework** - 让 MCP 服务器开发变得简单而强大！ 🚀