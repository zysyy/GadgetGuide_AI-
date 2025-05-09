/qasystem_project             # 项目根目录
    ├── backend/                  # 所有后端代码存放于此
    │   ├── main.py               # FastAPI 应用实例和主要的 API 路由
    │   ├── knowledge_base_processor.py # 知识库加载、处理、索引模块
    │   ├── qa_handler.py         # 问答逻辑处理模块
    │   ├── schemas.py            # Pydantic 模型 (用于数据校验和序列化，FastAPI常用)
    │   ├── config.py             # 配置信息 (如 API 密钥的加载逻辑)
    │   │
    │   ├── uploads/              # 存放上传的知识库文档 (这个目录需要创建)
    │   ├── faiss_index/          # 存放FAISS索引文件 (这个目录需要创建)
    │   │
    │   ├── .env                  # 存放环境变量，如 DEEPSEEK_API_KEY (重要：此文件不应提交到git)
    │   └── requirements.txt      # Python 依赖包列表
    │
    ├── frontend/                 # 前端代码目录 (您之后用 Vue CLI 创建项目时会生成)
    │   └── ...
    │
    ├── .gitignore                # 指定 Git 应忽略的文件和目录
    └── README.md                 # 项目说明文件