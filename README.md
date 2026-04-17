# 智能文档处理系统 (Intelligent Document System)

基于大语言模型的前后端分离文档理解与多源数据融合系统，提供一套从 Web 网页端到 Desktop 桌面端的一键部署与开箱即用能力。

## 🌟 功能概览

- **双端融合体验**：支持作为标准 B/S 架构网页版运行，同时深度集成 `pywebview` 支持纯本地桌面级原生视窗与文件保存弹窗。
- **完善的账户与组织架构**：内置完整的 JWT 鉴权、基于角色的用户管理（RBAC）、团队（Team）协作以及基于 API Key 的无头调用。
- **文档智能解析与脱机抽取**：支持 `docx/xlsx/md/txt/pdf` 的结构化高精解析（基于 OCR 与 Docling 洗稿算法）。
- **复合知识库管理**：
  - **向量 RAG**：解析后分块写入 ChromaDB 本地向量库，纯本地存储断网也可用。
  - **图谱 RAG**：借助模型生成的实体与关系构建 Knowledge Graph 知识图谱联合检索。
- **智能对话 (支持多端同步)**：支持持久化聊天会话（数据库存储），在各个客户端数据无缝漫游。
- **文档比对与加工**：内置文档比对（Doc Comparator）及智能操作引擎，快速比较多版本文档的异同并生成洞察。
- **模板表格自动填写**：上传 `docx/xlsx` 模板，从知识库中精确检索数据并利用大语言模型全自动回填生成，原生桌面运行时可一键拉起桌面文件夹另存为。
- **全链路追踪与集成**：提供详尽的操作审计日志（Audit Logs）管理以及事件回拨级 Webhook 分发。
- **一键 Markdown 转 PPT**：内置 Slidev 环境，支持将 Markdown 文本快速转换为精美的项目演示文稿。

## 🛠️ 技术栈

- **前端界面**：Vue 3 + Vite + Element Plus + Pinia (现代化工程化 SPA)
- **后端服务**：FastAPI + Uvicorn + SQLAlchemy + SQLite (高性能异步 REST API 与关系型数据库引擎)
- **跨端外壳**：PyWebView (连接 Web 生态与桌面 GUI 并互发消息的核心桥梁)
- **核心逻辑引擎**：LangChain + Docling + ChromaDB + PaddleOCR
- **知识库 Embedding 模型**：本地 BAAI/bge-small-zh-v1.5 (自带代码自愈自动下载与本地加载机制)
- **大语言模型引擎**：支持 OpenAI / DeepSeek / 智谱 GLM 等主流 API 及本地大模型接口
- **独立桌面打包**：PyInstaller (`.spec` 高级定制) + Inno Setup (自带 WebView2 环境检测与静默拉取)

## 📁 项目结构

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

### 1. 基础环境配置
在根目录下将 `.env.example` 复制为 `.env`，并在此文件中填入您的主线大模型（如 Deepseek 或 OpenAI）的 `LLM_API_KEY`。

### 2. 启动全栈体系 (Web/桌面融合)
系统支持自动识别运行环境。如果运行的是本地脚本，它会同时启动 FastAPI 作为核心并在后台建立 GUI WebView 视窗。

```bash
conda activate intelligent-algorithm
pip install -r requirements.txt
cd frontend
yarn install
yarn build
cd ..
python main.py
```
> **🌐 Web 访问**：由于 FastAPI 默认运行在 `0.0.0.0:8000` 或随机闲置端口（视 `main.py` 配置而定），您也可以随时在局域网其它端访问 `http://localhost:8000`（或当前绑定端口）。
> **🤖 模型机制说明**：首次跑入库逻辑时，若检测到外层 `data/models/bge-small-zh-v1.5` 脱机模型不存在，底座将会触发自愈防御机制，自动从 Huggingface 官网拉取完整模型权重到该目录，请保持网络通畅。

## 📦 一键自动化打包发布 (生产分发)

由于我们的系统深度集成了大量底层向量 C++ 库，为方便最终客户（无技术背景人员）一键入驻体验，我们使用 `PyInstaller` 搭配 `Inno Setup` 将所有环境和库进行极致压缩缝合。

在项目根目录（确保已安装 `yarn`、`pyinstaller` 以及电脑中安装了 `Inno Setup 6`），只需一键执行：
```bash
python scripts\build.py
```

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
