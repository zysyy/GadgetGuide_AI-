# backend/qa_handler.py
import requests # 用于发送 HTTP 请求
import os       # 用于访问环境变量

from langchain_ollama import OllamaEmbeddings
from .knowledge_base_processor import load_faiss_index
# 从 config.py 导入配置
from .config import OLLAMA_EMBEDDING_MODEL, DEEPSEEK_API_KEY # 确保 DEEPSEEK_API_KEY 被正确导入

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL_NAME = "deepseek-chat" # 或者您想使用的其他 DeepSeek 模型

# 在模块加载时尝试加载 FAISS 索引
vector_db = load_faiss_index()

def reload_vector_db():
    """重新加载 FAISS 索引，用于索引更新后。"""
    global vector_db
    vector_db = load_faiss_index()
    if vector_db:
        print("qa_handler: FAISS 索引已重新加载。")
    else:
        print("qa_handler: FAISS 索引重新加载失败或索引为空。")
    return vector_db

def retrieve_context(query: str) -> dict: # 添加返回类型提示
    """
    根据用户查询从 FAISS 索引中检索相关上下文。
    返回一个包含 'retrieved_chunks' 列表或 'error'/'message' 键的字典。
    """
    if vector_db is None:
        print("qa_handler.retrieve_context: 知识库索引未加载。")
        return {"error": "知识库索引未加载，请先处理知识库文档。"}

    try:
        print(f"qa_handler.retrieve_context: 正在为查询 '{query}' 检索上下文...")
        results = vector_db.similarity_search(query, k=3) # k=3 表示返回3个最相关的片段
        
        if not results:
            print(f"qa_handler.retrieve_context: 未能为查询 '{query}' 找到相关信息。")
            return {"message": "未能从知识库中找到相关信息。", "retrieved_chunks": []}

        retrieved_chunks = [doc.page_content for doc in results]
        print(f"qa_handler.retrieve_context: 为查询 '{query}' 检索到 {len(retrieved_chunks)} 个相关片段。")
        return {"retrieved_chunks": retrieved_chunks}
    except Exception as e:
        print(f"qa_handler.retrieve_context: 检索上下文时出错: {e}")
        return {"error": f"检索上下文时出错: {e}"}

def generate_answer_from_llm(query: str, context_chunks: list[str]) -> dict: # 添加类型提示
    """
    使用检索到的上下文和用户查询，调用 DeepSeek API 生成答案。
    返回一个包含 'answer' 或 'error' 键的字典。
    """
    if not DEEPSEEK_API_KEY:
        print("qa_handler.generate_answer_from_llm: DEEPSEEK_API_KEY 未配置。")
        return {"error": "AI 服务配置不完整 (API Key缺失)。"}

    # 1. 构建 Prompt
    context_str = "\n\n---\n\n".join(context_chunks) # 将上下文片段用分隔符连接起来
    
    prompt_template = f"""
你是一个乐于助人的AI助手，专门负责根据提供的产品信息来回答用户的问题。请严格根据下面提供的“参考信息”来回答用户的问题。
答案应尽可能简洁、准确，并直接与参考信息相关。
如果参考信息中没有足够的内容来回答问题，请明确告知用户“根据我目前掌握的关于您所咨询产品的信息，无法回答您关于‘{query}’的具体问题”，不要编造答案。
请不要提及你是基于“参考信息”作答的，直接给出答案即可。

参考信息：
---
{context_str}
---

用户问题：{query}

请给出您的回答：
"""
    print(f"\nqa_handler.generate_answer_from_llm: 发送给 LLM 的 Prompt (为了调试，实际部署时可移除或记录到日志)：\n{prompt_template}\n")


    # 2. 构建请求头和请求体
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEEPSEEK_MODEL_NAME,
        "messages": [
            # 可以选择加入一个 system message 来设定角色，但我们这里把所有指示都放在了 user message 的 prompt_template 中
            # {"role": "system", "content": "你是一个乐于助人的AI助手，专门负责根据提供的产品信息来回答用户的问题。"},
            {"role": "user", "content": prompt_template}
        ],
        "max_tokens": 1000,  # 根据需要调整，确保答案不会太长而被截断
        "temperature": 0.7, # 0.0-1.0，值越低答案越确定和保守，值越高越有创造性。对于问答，可以低一些。
        # "stream": False # 如果需要流式输出，可以设为 True 并相应处理响应
    }

    # 3. 发送请求到 DeepSeek API
    try:
        print(f"qa_handler.generate_answer_from_llm: 正在调用 DeepSeek API (模型: {DEEPSEEK_MODEL_NAME})...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60) # 设置超时
        response.raise_for_status()  # 如果请求失败 (状态码 4xx 或 5xx)，则抛出 HTTPError

        response_data = response.json()
        
        # 4. 解析并返回答案
        if response_data.get("choices") and len(response_data["choices"]) > 0:
            answer = response_data["choices"][0].get("message", {}).get("content", "")
            if answer:
                print(f"qa_handler.generate_answer_from_llm: 从 DeepSeek API 获取到答案。")
                return {"answer": answer.strip()}
            else:
                print("qa_handler.generate_answer_from_llm: DeepSeek API 返回了空的答案内容。")
                return {"error": "AI 服务返回了空的答案。"}
        else:
            print(f"qa_handler.generate_answer_from_llm: DeepSeek API 响应格式不符合预期: {response_data}")
            return {"error": "AI 服务响应格式不正确。"}

    except requests.exceptions.Timeout:
        print(f"qa_handler.generate_answer_from_llm: 调用 DeepSeek API 超时。")
        return {"error": "AI 服务请求超时，请稍后再试。"}
    except requests.exceptions.RequestException as e:
        print(f"qa_handler.generate_answer_from_llm: 调用 DeepSeek API 时发生网络错误: {e}")
        return {"error": f"与 AI 服务通信时发生网络错误: {e}"}
    except Exception as e:
        print(f"qa_handler.generate_answer_from_llm: 处理 LLM 响应时发生未知错误: {e}")
        return {"error": f"处理 AI 服务响应时发生未知错误: {e}"}


def get_final_answer(query: str) -> dict:
    """
    完整的 RAG 流程：检索上下文 -> LLM 生成答案。
    返回一个包含 'answer' 或 'error'/'message' 键的字典。
    """
    print(f"\nqa_handler.get_final_answer: 开始处理查询: '{query}'")
    context_result = retrieve_context(query)

    if "error" in context_result:
        return {"error": context_result["error"]}
    
    if not context_result.get("retrieved_chunks"):
        # 如果没有检索到任何相关信息，可以直接返回提示用户，或者让 LLM 来回复（取决于产品设计）
        # 为了更可控，我们这里直接返回
        print(f"qa_handler.get_final_answer: 未检索到上下文，将直接告知用户。")
        # 或者，也可以让LLM根据“无信息”的情况来回答，但需要调整prompt
        # return generate_answer_from_llm(query, []) 
        return {"answer": f"抱歉，根据我目前掌握的关于您所咨询产品的信息，暂时无法回答您关于“{query}”的问题。您可以尝试换个问法或咨询其他方面的信息。"}


    # 如果检索到上下文，则交给 LLM 生成答案
    llm_result = generate_answer_from_llm(query, context_result["retrieved_chunks"])
    
    if "error" in llm_result:
        return {"error": llm_result["error"]}
    
    return {"answer": llm_result.get("answer", "抱歉，AI 未能生成有效的回答。")}