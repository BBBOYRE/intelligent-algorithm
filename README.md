# intelligent-algorithm

基于大语言模型的文档理解与多源数据融合系统。

## 功能概览

- 文档上传与解析：支持 `docx/xlsx/md/txt`
- 知识库入库：解析后分块写入 ChromaDB
- 智能问答：基于知识库检索的对话问答
- 模板表格自动填写：支持 `docx/xlsx` 模板

## 项目结构

```text
intelligent-algorithm/
├── app.py
├── config.py
├── requirements.txt
├── start.bat
├── core/
│   ├── agent.py
│   ├── document_parser.py
│   ├── knowledge_base.py
│   ├── llm_factory.py
│   ├── retriever.py
│   └── table_filler.py
├── utils/
│   ├── file_utils.py
│   ├── schema.py
│   └── template_parser.py
└── pages/
    ├── 1_📄_文档上传.py
    ├── 2_💬_智能问答.py
    └── 3_📊_表格填写.py
```

## 快速开始

1. 创建虚拟环境并激活

```bash
python -m venv venv
venv\Scripts\activate
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量

```bash
copy .env.example .env
```

编辑 `.env` 中的 LLM 和 Embedding 参数。

4. 启动

```bash
streamlit run app.py
```

或直接使用 Windows 脚本：

```bash
start.bat
```

## 配置说明

- `LLM_PROVIDER`: `deepseek` / `qwen` / `ollama` / `openai`
- `EMBEDDING_PROVIDER`: `local` / `openai` / `dashscope`
- `CHROMA_PERSIST_DIR`: ChromaDB 本地持久化目录
- `RETRIEVAL_TOP_K`: 检索返回条数

## 运行流程建议

1. 先在“文档上传与解析”页面上传原始文档并入库
2. 在“智能问答”页面进行内容查询
3. 在“模板表格自动填写”页面上传模板并下载填写结果

## 如何测试

### 1. 启动前检查

1. 确认已进入项目目录并激活环境

```bash
cd "d:\Desktop\school file\智能算法\intelligent-algorithm"
conda activate intelligent-algorithm
```

2. 确认 `.env` 已配置（至少包含可用的 LLM 配置）

```bash
LLM_PROVIDER=deepseek
LLM_API_KEY=你的真实Key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

3. 启动应用

```bash
streamlit run app.py --server.port 8501
```

### 2. 使用样例数据测试

项目已内置测试数据目录：

- 源文档目录：`sample_data/source_docs`
- 模板目录：`sample_data/templates`

推荐按下面顺序测试：

1. 打开“文档上传与解析”页面，上传 `sample_data/source_docs` 下全部文件并点击“开始解析并入库”
2. 打开“智能问答”页面，输入问题，例如：
	 - `公司法定代表人是谁？`
	 - `2025Q4净利润是多少？`
	 - `客户拜访记录中的下一步计划是什么？`
3. 打开“模板表格自动填写”页面，上传 `sample_data/templates` 下模板并执行自动填写
4. 下载生成结果，核对字段是否回填成功

### 3. 回归测试建议（改 Bug 后）

每次修复后，建议至少做以下回归：

1. 文档上传能成功入库，且知识库分块数有增长
2. 智能问答页不报错，能够返回中文回答
3. Word 模板可填写并可下载
4. Excel 模板可填写并可下载

### 4. 常见问题

- 启动时报 `File does not exist: app.py`
	- 原因：当前目录不对
	- 处理：先 `cd` 到项目根目录再启动

- 问答时报 API 错误
	- 原因：`.env` 中 Key/模型配置不正确
	- 处理：检查 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`

- 填表结果为空或全是 `N/A`
	- 原因：知识库未入库或检索上下文不足
	- 处理：先上传更多源文档，再进行填写
