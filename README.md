# 智能文档处理系统 (Intelligent Document System)

> **项目名称**：基于大语言模型的文档理解与多源数据融合系统  
> **竞赛类型**：企业服务 + 智能计算（应用类）  
> **主办单位**：金陵科技学院  

基于大语言模型的前后端分离文档理解与多源数据融合系统，提供一套从 Web 网页端到 Desktop 桌面端的一键部署与开箱即用能力。

## 核心问题与解决方案

### 问题
企业日常工作中，员工需要从大量格式不一、结构松散的非结构化文档中，人工阅读、理解并提取关键信息，再手动整理汇总到表格中。这一过程：
- 📋 重复性高、操作繁琐
- ⚠️ 容易因疲劳导致遗漏和错误
- ⏱️ 严重挤占应用于创造性工作的时间

### 解决方案
智能化系统自动处理非结构化文本，通过深度语义理解实现：
- 🤖 自动提取关键信息并结构化存储
- 📊 智能填写表格和数据库
- 🚀 显著提升工作效率（准确率 > 80%，响应时间 < 90 秒）

## 🌟 功能概览

- **双端融合体验**：支持作为标准 B/S 架构网页版运行，同时深度集成 `pywebview` 支持纯本地桌面级原生视窗与文件保存弹窗。
- **完善的账户与组织架构**：内置完整的 JWT 鉴权、基于角色的用户管理（RBAC）、团队（Team）协作以及基于 API Key 的无头调用。
- **✨ 文档智能解析与脱机抽取**：支持 `docx/xlsx/md/txt/pdf` 的结构化高精解析（基于 OCR 与 Docling 智能算法）。
  - 非结构化文档信息提取模块：自动识别、解析、抽取文档关键信息与实体数据
  - 多格式支持：Word、Excel、Markdown、纯文本、PDF
  - 高精准度：信息提取准确率 > 80%
- **复合知识库管理**：
  - **向量 RAG**：解析后分块写入 ChromaDB 本地向量库，纯本地存储断网也可用。
  - **图谱 RAG**：借助模型生成的实体与关系构建 Knowledge Graph 知识图谱联合检索。
- **智能对话 (支持多端同步)**：支持持久化聊天会话（数据库存储），在各个客户端数据无缝漫游。
- **📝 文档智能操作**：内置文档智能操作交互模块，支持自然语言指令自动执行：
  - 文档编辑与排版
  - 格式调整
  - 内容提取与转换
- **🔄 文档比对与加工**：内置文档比对（Doc Comparator）及智能操作引擎，快速比较多版本文档的异同并生成洞察。
- **📋 表格自定义数据填写**：表格自定义数据填写模块
  - 上传 `docx/xlsx` 模板，从知识库中精确检索数据
  - 利用大语言模型全自动回填生成
  - 原生桌面运行时可一键拉起桌面文件夹另存为
  - 平均准确率 > 80%，单表响应时间 < 90 秒
- **全链路追踪与集成**：提供详尽的操作审计日志（Audit Logs）管理以及事件回拨级 Webhook 分发。
- **🎬 一键 Markdown 转 PPT**：内置 Slidev 环境，支持将 Markdown 文本快速转换为精美的项目演示文稿。

## 🛠️ 技术栈

- **前端界面**：Vue 3 + Vite + Element Plus + Pinia (现代化工程化 SPA)
- **后端服务**：FastAPI + Uvicorn + SQLAlchemy + SQLite (高性能异步 REST API 与关系型数据库引擎)
- **跨端外壳**：PyWebView (连接 Web 生态与桌面 GUI 并互发消息的核心桥梁)
- **核心逻辑引擎**：LangChain + Docling + ChromaDB + PaddleOCR
- **知识库 Embedding 模型**：本地 BAAI/bge-small-zh-v1.5 (自带代码自愈自动下载与本地加载机制)
- **大语言模型引擎**：支持 OpenAI / DeepSeek / 智谱 GLM 等主流 API 及本地大模型接口
- **独立桌面打包**：PyInstaller (`.spec` 高级定制) + Inno Setup (自带 WebView2 环境检测与静默拉取)

## 技术指标 & 评价标准

| 指标 | 要求 | 说明 |
|------|------|------|
| **信息提取准确率** | > 80% | 文档解析与信息抽取的准确度 |
| **表格填写准确率** | 平均 > 80% | 自动填表的准确率（5 张表） |
| **单表响应时间** | < 90 秒 | 每个表格的平均处理时间 |
| **支持格式** | docx, xlsx, md, txt, pdf | 多格式文档处理能力 |
| **部署方式** | Web + 桌面 + API | 灵活部署支持 |
| **多人协作** | 支持 | 基于 Team 的团队功能 |

## 项目结构

```text
intelligent-algorithm/
├── frontend/                 # Vue 3 前端源码目录
│   ├── src/api/              # HTTP 请求拦截器及各业务通信层
│   ├── src/views/            # 路由视图 (知识库、聊天、团队、表格自动填充)
│   └── src/stores/           # Pinia 全局状态控制 (认证流水线与对话漫游)
├── server/                   # FastAPI 后端路由及服务层
│   ├── auth/                 # 鉴权机制 (JWT、密文密码与权限依赖)
│   ├── models/               # SQLAlchemy 数据模型 (User, Team, Chat, Webhook...)
│   ├── routes/               # API 控制器 (分发聊天、表格、审计、API Keys 动作)
│   ├── middleware/           # 请求全局切面处理 (如审计日志拦截记录)
│   ├── tasks/                # 异步任务或离线并发任务队列管理
│   └── database.py           # 数据库引擎和 Base 会话实例
├── core/                     # 核心大模型链路算法与 RAG 引擎
│   ├── agent.py              # 对话总控智能体
│   ├── doc_comparator.py     # 长文本与多源表格版式的智能比较器
│   ├── document_parser.py    # Docling 规则解析树提取
│   ├── knowledge_base.py     # 向量知识库 (ChromaDB)
│   ├── knowledge_graph.py    # 本地知识图谱映射模块
│   ├── ocr_engine.py         # 文档版面还原与识别引擎
│   └── table_filler.py       # 信息自动抽取回填框架
├── data/                     # 运行时动静态数据 (本地库、本地模型、产出生成文件)
├── scripts/                  # 自动化构建打包脚本中心 (build.py, app.spec, installer.iss)
├── slidev/                   # 项目演示文稿 (Markdown转PPT功能模块)
├── config.py                 # 后端全局参数与路径映射配置
├── main.py                   # FastAPI / PyWebView 桌面端与后端联合应用主入口
├── .env                      # 核心机密模型 API Key 及数据库环境配置存放处
└── requirements.txt          # Python 后端依赖清单
```

## 🚀 快速开始 (开发模式)

### 前置要求
- Python 3.8+
- Node.js 16+ & Yarn
- SQLite（自含）
- 大语言模型 API Key（OpenAI / DeepSeek / 智谱 GLM 等）

### 1. 克隆仓库与环境配置

```bash
# 克隆项目
git clone <your-repo-url>
cd intelligent-algorithm

# 创建 Python 环境
conda create -n intelligent-algorithm python=3.10
conda activate intelligent-algorithm

# 复制环境配置文件
cp .env.example .env
# 编辑 .env，填入你的 LLM API Key（如 DeepSeek、OpenAI）
# 参考内容：
# LLM_PROVIDER=deepseek  # 或 openai、glm-4
# LLM_API_KEY=your-api-key-here
# DATABASE_URL=sqlite:///./data/db/app.db
# AUTH_DISABLED=false  # 私有部署可改为 true
```

### 2. 安装 Python 后端依赖

```bash
pip install -r requirements.txt
```

> ⚠️ **首次启动自愈机制**：  
> 如检测到 `data/models/bge-small-zh-v1.5` 本地模型不存在，系统会自动从 HuggingFace 下载完整模型权重（约 400MB），请保持网络通畅。

### 3. 安装并构建前端

```bash
cd frontend
yarn install
yarn build
cd ..
```

### 4. 启动应用

#### 方式 A：Web 服务（浏览器访问）
```bash
# 仅启动后端 API 服务
python main.py --web-only
# 访问 http://localhost:8000
```

#### 方式 B：桌面应用（PyWebView）
```bash
# 启动完整桌面应用（集成 PyWebView）
python main.py
# 自动拉起原生窗口
```

#### 方式 C：开发模式（热重载）
```bash
# 终端 1：启动后端（自动 reload）
python main.py --dev

# 终端 2：启动前端开发服务器
cd frontend
yarn dev
# 访问 http://localhost:5173
```

> **🔧 开发提示**：  
> - 后端 API 运行在 `http://localhost:8000`
> - 前端开发服务器运行在 `http://localhost:5173`
> - 前端已配置代理规则，自动转发 `/api/*` 请求至后端

## 一键自动化打包发布 (生产分发)

由于我们的系统深度集成了大量底层向量 C++ 库，为方便最终客户（无技术背景人员）一键入驻体验，我们使用 `PyInstaller` 搭配 `Inno Setup` 将所有环境和库进行极致压缩缝合。

在项目根目录（确保已安装 `yarn`、`pyinstaller` 以及电脑中安装了 `Inno Setup 6`），只需一键执行：
```bash
python scripts\build.py
```
建议先进入 `intelligent-algorithm` conda 环境后再执行，以确保 Python 依赖与 PyInstaller 使用的是同一环境。

该打包构建脚本会自动替你打理一切底层脏活：
1. **前端打包**：执行 `yarn build` 将 Vue 代码静态化至 `dist`。
2. **后端编译**：调用 `pyinstaller scripts/app.spec`，将所有 Python 底层依赖（如 Docling 等）强行收集抽离至 `build/dist/IntelligentDocSystem/_internal` 仓库中。
3. **安全资产抽离**：为了让客户能够看见环境配置和保证引擎读取本地模型，脚本自动化将 `.env` 配置和数百兆的 `data/models` 模型平滑拷贝剥离到主程序根目录结构中。
4. **生成桌面安装包**：在 `iscc scripts\installer.iss` 阶段完毕后，一键生成带有自动判断电脑基础环境与解压还原策略的 `Install_IntelligentDocSystem.exe` 最终发行文件，它存放在 `build/Installer` 文件夹中。

## 📊 项目演示文稿 (Slidev PPT)

本项目内置集成了基于 **Slidev** 的 Markdown 转 PPT 功能，方便快速制作和更新项目汇报。

**启动演示与编辑环境**：
```bash
cd slidev
yarn dev
```
启动后访问 `http://localhost:3030`，修改 `slidev/slides.md` 将实时生效。

**导出幻灯片为 PDF**：
```bash
cd slidev
yarn export
```

## 🤔 常见问题 (FAQ)

### Q1：运行 `python main.py` 时提示找不到模型怎么办？
**A**：系统会自动从 HuggingFace 下载 `bge-small-zh-v1.5` 模型（约 400MB）。请确保：
- 网络连接正常
- `data/models/` 目录有写权限
- 磁盘空间充足（> 1GB）

### Q2：如何配置不同的大语言模型（LLM）？
**A**：编辑 `.env` 文件，修改 `LLM_PROVIDER` 和 `LLM_API_KEY`：
```env
# 使用 OpenAI
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxx

# 或使用 DeepSeek
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-xxx

# 或使用智谱 GLM
LLM_PROVIDER=glm-4
LLM_API_KEY=xxx
```

### Q3：支持私有部署吗？可以不要身份认证吗？
**A**：支持。在 `.env` 中设置：
```env
AUTH_DISABLED=true      # 禁用身份认证
DEPLOYMENT_MODE=private # 私有部署模式
```

### Q4：前端和后端分离部署的方法？
**A**：
1. **后端独立部署**：`python main.py --web-only`
2. **前端单独构建**：`cd frontend && yarn build`
3. **前端代码配置**：编辑 `frontend/src/api/http.js`，修改 API 基地址指向后端服务器

### Q5：如何在团队中使用？支持多用户吗？
**A**：完全支持。系统内置：
- JWT 身份认证与会话管理
- 基于 Role 的权限控制（RBAC）
- Team 级别的协作隔离
- API Key 无头调用

### Q6：表格填写的准确率如何保证？
**A**：系统通过以下机制保证准确率 > 80%：
- 多层级信息检索（向量 RAG + 知识图谱）
- 大语言模型深度语义理解
- 上下文感知的数据映射
- 支持人工审核与反馈调整

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下流程：

1. **Fork 项目**：`git clone <your-fork-url>`
2. **创建分支**：`git checkout -b feature/your-feature`
3. **提交更改**：
   ```bash
   git add .
   git commit -m "feat: describe your changes clearly"
   git push origin feature/your-feature
   ```
4. **提交 Pull Request**：描述你的改动与测试结果
5. **代码审查**：维护者会进行审查与反馈

### 贡献方向
- 🐛 **Bug 修复**：发现 Issue 并提交 PR
- ✨ **新功能**：增强现有模块或新增高价值功能
- 📚 **文档改进**：更新 README、API 文档或注释
- 🧪 **测试覆盖**：增加单元测试或集成测试
- 🎨 **UI/UX 优化**：改进前端设计与用户体验


## 🙏 致谢

感谢以下开源项目与技术的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Python Web 框架
- [Vue 3](https://vuejs.org/) - 渐进式 JavaScript 框架
- [LangChain](https://python.langchain.com/) - LLM 应用开发框架
- [Docling](https://github.com/DS4SD/docling) - 文档解析引擎
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [PyWebView](https://pywebview.flowrl.com/) - 桌面 GUI 框架
- [Slidev](https://sli.dev/) - Markdown 演示框架

---


