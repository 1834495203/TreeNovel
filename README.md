# InteractNovel - 互动小说平台

ReactNovel是一个基于AI的互动小说平台，支持多角色扮演、场景管理和图可视化。玩家可以创建和管理角色，在不同的场景中进行对话，体验沉浸式的故事体验。

## ✨ 特性

- 🎭 **多角色对话系统**：支持创建和管理多个AI角色，每个角色都有独特的性格和背景
- 🗺️ **场景管理**：创建嵌套的场景结构，支持主场景和子场景
- 📊 **场景关系图**：使用图可视化展示场景之间的关系
- 💬 **实时聊天**：在场景中与多个角色进行互动对话
- 🔧 **FastAPI后端**：高性能的Python Web API
- 🎨 **Vue 3前端**：现代化的用户界面，支持TypeScript
- 🗄️ **Neo4j图数据库**：灵活的场景和角色关系存储

## 🏗️ 技术栈

### 后端
- **FastAPI** - Python Web框架
- **Neo4j** - 图数据库
- **Langchain** - AI对话引擎
- **Peewee** - 数据库ORM

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速的前端构建工具
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端
- **Cytoscape.js** - 图可视化库

## 📋 前提条件

在开始之前，请确保您已安装：

- **Python 3.10+**
- **Node.js 20.19.0+ 或 22.12.0+**
- **Neo4j数据库**
- **API密钥** (如 DeepSeek API Key)

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd TreeNovel
```

### 2. 后端设置

#### 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
# ...其他API
```

在 `mapper/config` 目录创建 `.env` 文件：

```env
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YOUR_PASSWORLD
NEO4J_HOST=localhost
NEO4J_PORT=7687

SQLITE_URL=database.db
```

运行 `entity/BaseModel.py` 创建数据库。数据库目录为 `mapper/config`

#### 启动Neo4j数据库

下载 neo4j desktop 2, 确保Neo4j数据库正在运行，默认配置：
- URL: `bolt://localhost:7687`
- 用户名: `neo4j`
- 密码: `YOUR_PASSWORLD`

#### 启动后端服务器

```bash
python Start.py
```

服务器将在 `http://localhost:8000` 启动

### 3. 前端设置

进入前端目录：

```bash
cd frontend/frontend
```

#### 安装依赖

```bash
npm install
```

#### 启动开发服务器

```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

## 📚 使用指南

### 角色管理

1. 点击导航栏中的"角色管理"
2. 创建新角色并设置其属性和性格

### 场景管理

1. 点击"场景关系图"创建新场景
2. 设置场景名称、描述和属性
3. 建立场景之间的父子关系

### 场景关系图

1. 点击"场景关系图"查看所有场景的可视化图
2. 不同颜色表示不同类型的场景：
   - 蓝色：主场景
   - 绿色：根场景
   - 灰色：普通场景
3. 点击场景节点进入对话

### 场景聊天

1. 从场景关系图中选择一个场景
2. 与该场景中的任意角色进行对话

## 📁 项目结构

```
InteractNovel/
├── backend/
│   ├── controller/          # 控制器层
│   ├── service/            # 业务逻辑层
│   ├── mapper/             # 数据访问层
│   ├── entity/             # 数据模型
│   ├── core/               # 核心功能
│   │   ├── chat/           # 聊天引擎
│   │   ├── GroupAgentEngine.py
│   │   └── PrepareChatHistory.py
│   └── utils/              # 工具类
├── frontend/frontend/
│   ├── src/
│   │   ├── views/          # Vue视图组件
│   │   ├── components/     # Vue组件
│   │   ├── api/            # API接口
│   │   └── beans/          # 数据模型
│   ├── public/             # 静态资源
│   └── package.json        # 前端依赖
├── config/                 # 配置文件
├── Start.py               # 服务器启动脚本
└── requirements.txt       # Python依赖
```

### 主要API端点

#### 角色管理
- `GET /api/characters` - 获取所有角色
- `POST /api/characters` - 创建新角色
- `PUT /api/characters/{id}` - 更新角色
- `DELETE /api/characters/{id}` - 删除角色

#### 场景管理
- `GET /api/scenes` - 获取所有场景
- `POST /api/scenes` - 创建新场景
- `PUT /api/scenes/{id}` - 更新场景
- `DELETE /api/scenes/{id}` - 删除场景
- `GET /api/scenes/graph` - 获取场景关系图

#### 聊天功能
- `POST /api/chat` - 发送聊天消息
- `GET /api/conversations` - 获取对话历史

## 🛠️ 开发指南

### 后端开发

#### 添加新API端点

1. 在 `controller/` 目录下创建控制器
2. 在 `service/` 目录下实现业务逻辑
3. 在 `mapper/` 目录下实现数据访问

### 前端开发

#### 添加新页面

1. 在 `src/views/` 目录下创建Vue组件
2. 在路由配置中注册新路由

#### 添加新组件

1. 在 `src/components/` 目录下创建Vue组件
2. 在父组件中引入并使用

## 📝 配置说明

### 端口配置

- 后端服务器: `8000`
- 前端开发服务器: `5173`
- Neo4j数据库: `7687`

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献

欢迎提交Pull Request和Issue！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至: 1834495203@qq.com

---

**InteractNovel** - 让故事因对话而生动 ✨
