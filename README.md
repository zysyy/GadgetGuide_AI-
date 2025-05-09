# GadgetGuide AI

## 项目简介

GadgetGuide AI 是一个基于自定义知识库的实用型电子产品问答与推荐系统。用户可以通过自然的语言提问，系统会根据已有的产品信息（如技术规格、评测等）给出相关的回答，甚至可以进行简单的产品对比和推荐。

本项目旨在探索和实践检索增强生成 (RAG) 技术在构建智能问答系统中的应用。目前主要聚焦于苹果产品作为示例知识库，未来可以扩展到更多品牌和产品。

**当前版本:** v0.1.0-alpha (预发布) - 核心RAG问答功能已实现，包含Web界面。

## 主要功能

* **智能问答：** 用户可以通过聊天界面提问关于电子产品（当前主要为苹果产品）的信息。
* **基于知识库的回答：** 系统的回答主要基于用户提供的本地知识库文档。
* **多文档格式支持：** 后端能够处理和索引多种格式的文档（目前已实现 `.txt` 和 `.pdf`）。
* **动态知识库更新：** 支持通过 API 上传新文档来扩展或更新知识库。
* **产品信息对比（初步）：** 能够根据知识库内容，对相似产品进行简单的特性对比。
* **Web用户界面：** 提供一个基础的 Vue.js 构建的聊天界面与用户交互。

## 技术栈

* **后端：**
    * Python 3.9+
    * FastAPI: 高性能 Web 框架
    * LangChain: LLM 应用开发框架，用于编排 RAG 流程
    * Ollama (`bge-m3`): 本地运行的文本嵌入模型
    * FAISS: 高效的向量相似性搜索引擎
    * DeepSeek API: 用于生成最终答案的大语言模型
    * `python-dotenv`: 管理环境变量
    * `uvicorn`: ASGI 服务器
* **前端：**
    * Vue.js 3 (使用 Vue CLI 创建)
    * Axios: 用于与后端 API 通信
    * Marked: Markdown 解析库，用于渲染 AI 回答
    * DOMPurify: HTML 清理库，防止 XSS
* **开发环境管理：**
    * Conda: 管理 Python 环境
    * NVM: 管理 Node.js 版本
    * Git & GitHub: 版本控制与代码托管

## 项目结构
```
/GadgetGuide_AI_Project  (项目根目录)
├── backend/          # 后端 FastAPI 应用
│   ├── main.py       # FastAPI 应用主文件与 API 路由
│   ├── knowledge_base_processor.py # 知识库处理模块
│   ├── qa_handler.py # 问答逻辑处理模块
│   ├── schemas.py    # Pydantic 模型
│   ├── config.py     # 配置信息
│   ├── uploads/      # 存放上传的知识库源文档 (请将文档放于此处)
│   ├── faiss_index/  # 存放生成的 FAISS 索引 (自动生成)
│   ├── .env          # 环境变量文件 (需手动创建)
│   └── requirements.txt # Python 依赖
│
├── frontend/         # 前端 Vue.js 应用
│   ├── public/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── components/
│   │       └── ChatInterface.vue
│   ├── package.json
│   └── ...           (其他 Vue 项目文件)
│
├── .gitignore        # Git 忽略规则
└── README.md         # 本文件
```
## 环境搭建与运行指南

### 1. 先决条件

* **Python:** 3.9 或更高版本 (建议通过 Conda 管理)
* **Node.js:** LTS 版本 (例如 v22.x.x，建议通过 NVM 管理)
* **Ollama:** 已安装并正在运行，且已拉取所需的嵌入模型 (例如 `bge-m3`)。
    * 运行 Ollama 服务 (通常在后台自动运行，或手动执行 `ollama serve`)
    * 拉取模型: `ollama pull bge-m3`
* **DeepSeek API Key:** 您需要一个有效的 DeepSeek API 密钥。

### 2. 后端设置与启动

1.  **克隆仓库 (如果您是从GitHub获取)：**
    ```bash
    git clone [仓库地址]
    cd GadgetGuide_AI_Project
    ```
2.  **创建并配置 Conda 环境：**
    ```bash
    conda create -n aihomework python=3.9 -y # (如果 'aihomework' 环境已存在且满足要求，则直接激活)
    conda activate aihomework
    ```
3.  **安装 Python 依赖：**
    进入 `backend` 目录，然后安装 `requirements.txt` 中的依赖。
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
4.  **创建 `.env` 文件：**
    在 `backend` 目录下创建一个名为 `.env` 的文件，并填入您的 DeepSeek API 密钥：
    ```env
    DEEPSEEK_API_KEY="your_actual_deepseek_api_key"
    ```
5.  **准备知识库源文件：**
    将您的知识库文档（例如 `iPhone 15 Pro - 技术规格 - 官方 Apple 支持 (中国).pdf`, `iPhone 16 Pro - Tech Specs - Apple Support.pdf`, `sample_apple_info.txt` 等）放入 `backend/uploads/` 目录下。
6.  **启动后端 FastAPI 服务器：**
    确保您当前位于项目**根目录** (`GadgetGuide_AI_Project`)，然后运行：
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    服务器将运行在 `http://127.0.0.1:8000`。

7.  **首次构建知识库索引：**
    后端服务器启动后，打开浏览器或 API 测试工具 (如 Postman)，向以下地址发送一个 **POST** 请求 (无需请求体)：
    `http://127.0.0.1:8000/build_index_from_sample`
    * **注意：** `/build_index_from_sample` 端点目前会处理 `backend/main.py` 中 `sample_files` 列表指定的文件。请确保该列表与您 `backend/uploads/` 目录中的文件名一致。
    * 或者，您也可以使用 `/upload-documents/` 端点通过 FastAPI 的 `/docs` 页面上传文件来构建索引。
    观察后端服务器的终端日志，确认索引是否成功创建。

### 3. 前端设置与启动

1.  **安装 Node.js 依赖：**
    打开一个新的终端窗口，进入 `frontend` 目录，然后运行：
    ```bash
    cd ../frontend # 如果您当前在 backend 目录
    # 或者 cd GadgetGuide_AI_Project/frontend (从其他位置)
    npm install # 或者 yarn install
    ```
2.  **启动前端开发服务器：**
    ```bash
    npm run serve # 或者 yarn serve
    ```
    前端应用通常会运行在 `http://localhost:8080` (请留意终端输出的具体端口)。

3.  **访问应用：**
    在浏览器中打开前端应用的地址 (例如 `http://localhost:8080`)，您应该能看到 "GadgetGuide AI" 的聊天界面，并可以开始提问。

## API 端点说明 (部分)

* `POST /ask`: 接收用户查询 (`query` 表单参数)，返回 AI 生成的答案。
* `POST /upload-documents/`: 接收上传的文件 (`files` 参数)，用于更新知识库。
* `POST /build_index_from_sample`: （临时）基于预设文件列表构建知识库索引。
* `POST /retrieve_context`: （调试用）接收查询，返回检索到的上下文片段。

完整的 API 文档可以在后端服务启动后通过访问 `http://127.0.0.1:8000/docs` (Swagger UI) 或 `http://127.0.0.1:8000/redoc` 查看。

## 未来工作 (TODO)

* 完善前端的知识库文档上传界面。
* 进一步优化 Prompt Engineering 和答案的准确性。
* 考虑更高级的检索策略（如元数据过滤、重排序）以处理更复杂的查询和知识库。
* 增强错误处理和用户体验。
* （可选）实现用户注册登录和聊天历史保存功能。

---

作者：The_Riddler
日期：2025年5月9日 