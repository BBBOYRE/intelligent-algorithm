# 智能文档处理系统 (Intelligent Document System)

基于大语言模型的前后端分离文档理解与多源数据融合系统，提供一键脱机部署与开箱即用能力。

## 🌟 功能概览

- **文档上传与解析**：支持 `docx/xlsx/md/txt`，基于 Docling 进行结构化清洗。
- **本地知识库入库**：解析后分块写入 ChromaDB 本地向量库，纯本地存储，断网亦可使用。
- **智能问答**：基于知识库 RAG 检索的交互式问答。
- **模板表格自动填写**：上传 `docx/xlsx` 模板，从知识库中精确检索数据并利用大语言模型全自动回填生成。
- **一键 Markdown 转 PPT**：内置 Slidev 环境，支持将 Markdown 文本快速转换为精美的项目演示文稿。

## 🛠️ 技术栈

- **前端界面**：Vue 3 + Vite + Element Plus (现代化工程化 SPA)
- **后端服务**：FastAPI + Uvicorn (高性能异步 REST API)
- **核心逻辑引擎**：LangChain + Docling + ChromaDB
- **知识库 Embedding 模型**：本地 BAAI/bge-small-zh-v1.5 (自带代码自愈自动下载与本地加载机制)
- **大语言模型引擎**：支持 OpenAI / DeepSeek / 智谱 GLM 等主流 API 及本地大模型接口
- **独立桌面打包**：PyInstaller (`.spec` 高级定制) + Inno Setup (自带 WebView2 环境检测与静默拉取)

## 📁 项目结构

```text
intelligent-algorithm/
├── frontend/             # Vue 3 前端源码目录
├── server/               # FastAPI 后端路由控制器
├── core/                 # 核心 RAG、Agent、文档解析与表格填充引擎
├── utils/                # 文件工具类
├── data/                 # 运行时动态及静态数据 (模型文件、向量库、上传文件保留处)
├── scripts/              # 自动化构建打包脚本中心 (build.py, app.spec, installer.iss)
├── slidev/               # 项目演示文稿 (Markdown转PPT功能模块)
├── config.py             # 后端全局参数与路径映射配置
├── main.py               # FastAPI 后端主入口点
├── .env                  # 模型 API 密钥及环境配置核心点
└── requirements.txt      # Python 后端依赖清单
```

## 🚀 快速开始 (开发模式)

### 1. 基础环境配置
在根目录下将 `.env.example` 复制为 `.env`，并在此文件中填入您的主线大模型（如 Deepseek 或 OpenAI）的 `LLM_API_KEY`。

### 2. 启动 FastAPI 后端服务
```bash
conda activate intelligent-algorithm
pip install -r requirements.txt
python main.py
```
> 后端服务默认将启动运行在 `http://localhost:8000`。
> **🤖 模型机制说明**：首次跑入库逻辑时，若检测到外层 `data/models/bge-small-zh-v1.5` 脱机模型不存在，底座将会触发自愈防御机制，自动从 Huggingface 官网拉取完整模型权重到该目录，请保持网络通畅。

### 3. 启动 Vue 前端服务
重新打开一个终端环境并进入 `frontend`：
```bash
cd frontend
yarn install
yarn dev
```
前端启动后，直接按照控制台提示在浏览器中打开提供的本地端口链接即可体验完整功能。

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
