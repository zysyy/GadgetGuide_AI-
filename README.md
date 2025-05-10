# GadgetGuide AI

## 项目简介

GadgetGuide AI 是一个基于自定义知识库的实用型电子产品问答与推荐系统。用户可以通过自然的语言提问，系统会根据已有的产品信息（如技术规格、评测等）给出相关的回答，并能够对不同产品进行特性对比。

本项目旨在探索和实践检索增强生成 (RAG) 技术在构建智能问答系统中的应用。目前主要聚焦于苹果产品作为示例知识库，未来可以扩展到更多品牌和产品。

**当前版本:** `v0.2.0-alpha` (功能增强预发布版)
* 后端核心RAG流程（包括对比问答）已实现并稳定工作。
* 前端Vue.js聊天界面已搭建，可与后端交互，并对AI的Markdown回答进行渲染。

## 主要功能与特性 (v0.2.0-alpha)

* **智能问答：** 用户可以通过Web聊天界面提问关于电子产品（当前主要为苹果产品）的信息。
* **基于知识库的回答：** 系统的回答主要基于用户提供的本地知识库文档。
* **✨ 产品信息对比：**
    * 系统能够理解并处理涉及多个产品对比的查询（例如“iPhone A 与 iPhone B 对比有何升级?”）。
    * 通过后端初步的实体识别和针对性的上下文分别检索策略，为大语言模型提供更均衡的对比信息。
    * 优化了针对对比查询的Prompt，引导模型生成结构化的对比答案。
* **动态知识库更新：**
    * 支持通过 API 端点 (`/upload-documents/`) 上传新的知识库文档。
    * 后端能够处理和索引多种格式的文档（目前已实现 `.txt` 和 `.pdf`）。
* **优化的文本处理：**
    * 后端文本分割器已从 `CharacterTextSplitter` 升级为 `RecursiveCharacterTextSplitter`，并配置了更适合技术文档的分割参数，旨在提高检索上下文的质量。
* **Web用户界面 (Vue.js)：**
    * 提供一个基础但功能完善的聊天界面与用户交互。
    * AI 回答中的 Markdown 格式（如加粗、列表、代码块等）能够正确渲染，提升了信息的可读性。
    * 优化了中文输入法环境下回车键可能导致消息意外发送的问题。
    * 初步应用了新的“科技感”配色主题，改善了视觉体验。
    * 包含初始欢迎消息、加载状态提示和错误信息反馈。

## 技术栈

* **后端：**
    * Python 3.9+ (建议通过 Conda 管理)
    * FastAPI: 高性能 Web 框架
    * LangChain: LLM 应用开发框架，用于编排 RAG 流程
    * Ollama (`bge-m3`): 本地运行的文本嵌入模型
    * FAISS: 高效的向量相似性搜索引擎
    * DeepSeek API: 用于生成最终答案的大语言模型
    * `python-dotenv`: 管理环境变量
    * `uvicorn`: ASGI 服务器
    * `pypdf`: 用于处理 PDF 文档
* **前端：**
    * Node.js LTS (例如 v22.x.x，建议通过 NVM 管理)
    * Vue.js 3 (使用 Vue CLI 创建)
    * Axios: 用于与后端 API 通信
    * Marked: Markdown 解析库
    * DOMPurify: HTML 清理库
* **开发与版本控制：**
    * Git & GitHub

## 项目结构
```
/GadgetGuide_AI_Project  (项目根目录)
├── backend/          # 后端 FastAPI 应用
│   ├── main.py       # FastAPI 应用主文件与 API 路由
│   ├── knowledge_base_processor.py # 知识库处理模块
│   ├── qa_handler.py # 问答逻辑处理模块
│   ├── schemas.py    # Pydantic 模型 (可选)
│   ├── config.py     # 配置信息
│   ├── uploads/      # 存放知识库源文档 (请将文档放于此处)
│   ├── faiss_index/  # 存放生成的 FAISS 索引 (自动生成)
│   ├── .env          # 环境变量文件 (需手动创建)
│   └── requirements.txt # Python 依赖
│
├── frontend/         # 前端 Vue.js 应用
│   ├── public/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── assets/     # 存放全局静态资源如 theme.css
│   │   │   └── css/
│   │   │       └── theme.css
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

* **Python:** 3.9 或更高版本 (通过 Conda 管理)。
* **Node.js:** LTS 版本 (例如 v22.x.x，通过 NVM 管理)。
* **Ollama:** 已安装并正在运行，且已拉取 `bge-m3` 模型 (`ollama pull bge-m3`)。
* **DeepSeek API Key:** 准备好您的有效 DeepSeek API 密钥。

### 2. 后端设置与启动

1.  **克隆仓库/准备项目文件。**
    ```bash
    git clone https://github.com/zysyy/GadgetGuide_AI-.git
    ```
2.  **Conda 环境：**
    ```bash
    conda activate aihomework # (或您使用的环境名)
    ```
3.  **安装 Python 依赖：**
    进入 `backend` 目录：
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
4.  **创建并配置 `.env` 文件：**
    在 `backend` 目录下创建 `.env` 文件，内容为：
    ```env
    DEEPSEEK_API_KEY="your_actual_deepseek_api_key"
    ```
5.  **准备知识库源文件：**
    将您的 `.txt`, `.pdf` 等文档放入 `backend/uploads/` 目录。
6.  **启动后端 FastAPI 服务器：**
    确保您位于项目**根目录** (`GadgetGuide_AI_Project`)，运行：
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    服务器将运行在 `http://127.0.0.1:8000`。

7.  **构建知识库索引：**
    * **方式一 (推荐，更灵活)：** 后端启动后，使用 API 测试工具 (如 Postman 或 FastAPI 的 `/docs` 页面) 向 `POST /upload-documents/` 端点上传您在 `backend/uploads/` 目录中准备好的文件。
    * **方式二 (快速测试)：** 确保 `backend/main.py` 中的 `/build_index_from_sample` 端点内 `sample_files` 列表包含了您 `backend/uploads/` 目录下想要索引的准确文件名，然后通过 API 测试工具或浏览器（如果临时改为GET）发送 POST 请求到 `http://127.0.0.1:8000/build_index_from_sample`。
    观察后端终端日志确认索引成功创建。

### 3. 前端设置与启动

1.  **安装 Node.js 依赖：**
    打开新的终端窗口，进入 `frontend` 目录：
    ```bash
    cd GadgetGuide_AI_Project/frontend # (确保路径正确)
    npm install # 或 yarn install
    ```
2.  **（如果尚未创建）创建全局样式文件：**
    确保 `frontend/src/assets/css/theme.css` 文件存在，并包含您定义的 CSS 变量和全局样式。
3.  **（如果尚未导入）在 `frontend/src/main.js` 中导入全局样式：**
    ```javascript
    // frontend/src/main.js
    import { createApp } from 'vue'
    import App from './App.vue'
    import './assets/css/theme.css' // 确保路径正确

    createApp(App).mount('#app')
    ```
4.  **启动前端开发服务器：**
    ```bash
    npm run serve # 或 yarn serve
    ```
    前端应用通常运行在 `http://localhost:8080`。

5.  **访问应用：**
    在浏览器中打开前端地址 (例如 `http://localhost:8080`)。

## API 端点 (通过 FastAPI `/docs` 查看详情)

* `POST /ask`: 核心问答接口。
* `POST /upload-documents/`: 上传新文档以更新知识库。
* `POST /build_index_from_sample`: 基于预设文件列表构建/重建索引。
* `POST /retrieve_context`: (调试用) 仅检索并返回上下文。

## 未来工作 (TODO)

* 进一步完善前端的知识库文档上传界面和用户体验。
* 根据更多测试结果，持续优化 Prompt Engineering 和答案的相关性、准确性。
* 探索更高级的检索策略（如元数据过滤、结果重排序）以应对更复杂的场景。
* 增强错误处理和日志记录。
* （可选）实现用户注册登录和聊天历史保存功能。

---

作者：The_Riddler
日期：2025年5月10日 