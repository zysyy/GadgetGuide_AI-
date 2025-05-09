from fastapi import FastAPI

app = FastAPI(title="GadgetGuide AI API") # 给您的 API 起个名字

@app.get("/")
async def read_root():
    """
    根路径，返回一个欢迎信息。
    """
    return {"message": "Welcome to GadgetGuide AI API!"}

@app.get("/test")
async def test_endpoint():
    """
    一个简单的测试端点。
    """
    return {"status": "API is working!"}

# 如果您想在直接运行 python main.py 时启动 uvicorn (主要用于开发)
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)uvicorn main:app --reload --port 8000