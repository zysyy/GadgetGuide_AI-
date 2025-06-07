# backend/qa_handler.py

import requests
import os
import re
import logging

from langchain_ollama import OllamaEmbeddings
from .knowledge_base_processor import load_faiss_index
from .config import OLLAMA_EMBEDDING_MODEL, DEEPSEEK_API_KEY

logger = logging.getLogger("gadgetguide_ai.qa")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL_NAME = "deepseek-chat"

vector_db = load_faiss_index()

def reload_vector_db():
    global vector_db
    vector_db = load_faiss_index()
    if vector_db:
        logger.info("FAISS 索引已在 qa_handler 中重新加载。")
    else:
        logger.warning("FAISS 索引在 qa_handler 中重新加载失败或索引为空。")
    return vector_db

def retrieve_context(query: str, k: int = 5, threshold: float = 0.65) -> dict:
    if vector_db is None:
        logger.warning(f"retrieve_context (query: '{query}', k:{k}): 知识库索引未加载。")
        return {"error": "知识库索引未加载，请先处理知识库文档。"}
    try:
        logger.info(f"retrieve_context: 正在为查询 '{query}' 检索上下文 (k={k}, 阈值={threshold})...")
        results = vector_db.similarity_search_with_score(query, k=k)
        filtered_chunks = [doc.page_content for doc, score in results if score >= threshold]
        logger.info(f"retrieve_context: 过滤后命中 {len(filtered_chunks)} 个片段（分数阈值 {threshold}）")
        return {"retrieved_chunks": filtered_chunks}
    except Exception as e:
        logger.error(f"retrieve_context: 检索上下文时出错 (查询: '{query}', k:{k}): {e}", exc_info=True)
        return {"error": f"检索上下文时出错: {e}"}

def generate_answer_from_llm(
    original_query: str,
    context_chunks: list[str],
    is_comparison: bool = False,
    allow_free_gen: bool = False
) -> dict:
    if not DEEPSEEK_API_KEY:
        logger.error("generate_answer_from_llm: DEEPSEEK_API_KEY 未配置。")
        return {"error": "AI 服务配置不完整 (API Key缺失)。"}

    context_str = "\n\n---\n\n".join(context_chunks)

    # ===== 对比查询
    if is_comparison:
        prompt_instruction = f"""
你是一个专业的电子产品对比助手。请严格根据下面提供的“参考信息”，清晰地对比用户问题中提到的两款产品（例如 iPhone 16 Pro 和 iPhone 15 Pro）在主要配置和特性上的具体升级点或不同之处。
请以要点或列表形式总结。如果信息不足，请如实说明，不要编造内容。
"""
    # ====== 自由发挥模式 ======
    elif allow_free_gen:
        prompt_instruction = f"""
你是一个乐于助人的AI助手。若下方没有“参考信息”，请基于常识与推理自由回答用户问题，且**务必在答案开头加一句：“【以下为AI自动生成，仅供参考】”**。
如果有“参考信息”则优先据此作答，无则自由发挥。
"""
    else:
        prompt_instruction = f"""
你是一个乐于助人的AI助手，专门负责根据提供的产品信息来回答用户的问题。请严格根据下面提供的“参考信息”来回答用户的问题。
答案应尽可能简洁、准确，并直接与参考信息相关。
请不要提及你是基于“参考信息”作答的，直接给出答案即可。
"""

    prompt_template = f"""{prompt_instruction}

参考信息：
---
{context_str}
---

用户问题：{original_query}

请给出您的回答：
"""
    logger.debug(f"generate_answer_from_llm: 发送给 LLM 的 Prompt (用户原始查询: '{original_query}', 是否对比: {is_comparison}, allow_free_gen: {allow_free_gen}):\n{prompt_template}\n")

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEEPSEEK_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt_template}],
        "max_tokens": 1500,
        "temperature": 0.3,
    }

    try:
        logger.info(f"generate_answer_from_llm: 正在调用 DeepSeek API (模型: {DEEPSEEK_MODEL_NAME})...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_data = response.json()

        if response_data.get("choices") and len(response_data["choices"]) > 0:
            message_content = response_data["choices"][0].get("message", {}).get("content", "")
            if message_content:
                logger.info(f"generate_answer_from_llm: 从 DeepSeek API 获取到答案。")
                return {"answer": message_content.strip()}
            else:
                logger.warning("generate_answer_from_llm: DeepSeek API 返回了空的答案内容 (choices[0].message.content 为空)。")
                return {"error": "AI 服务返回了空的答案内容。"}
        else:
            logger.error(f"generate_answer_from_llm: DeepSeek API 响应格式不符合预期 (缺少 choices 或 choices 为空): {response_data}")
            return {"error": "AI 服务响应格式不正确。"}
    except requests.exceptions.Timeout:
        logger.error(f"generate_answer_from_llm: 调用 DeepSeek API 超时。")
        return {"error": "AI 服务请求超时，请稍后再试。"}
    except requests.exceptions.RequestException as e:
        logger.error(f"generate_answer_from_llm: 调用 DeepSeek API 时发生网络或请求错误: {e}", exc_info=True)
        return {"error": f"与 AI 服务通信时发生错误: {e}"}
    except Exception as e:
        logger.error(f"generate_answer_from_llm: 处理 LLM 响应或未知错误: {e}", exc_info=True)
        return {"error": f"处理 AI 服务响应时发生未知错误: {e}"}

def extract_comparison_entities_refined(query: str) -> list[str]:
    query_lower = query.lower()
    entities = []
    pattern = r"(iphone\s*\d+\s*(?:pro|plus|max|mini|se)?|iphone\s*\d+)"
    comparison_keywords = ["对比", "区别", "升级", "和...相比", "与...比较"]
    is_likely_comparison = any(keyword in query for keyword in comparison_keywords) and \
                           ("和" in query or "与" in query or "跟" in query)
    if is_likely_comparison:
        found_iphones = re.findall(pattern, query_lower)
        normalized_iphones = sorted(list(set([name.replace(" ", "").strip() for name in found_iphones])))
        if len(normalized_iphones) >= 2:
            entities = normalized_iphones[:2]
            logger.info(f"extract_comparison_entities_refined: 识别到对比实体: {entities} 从查询: '{query}'")
        else:
            logger.debug(f"extract_comparison_entities_refined: 未能从对比性查询 '{query}' 中提取到至少两个不同的iPhone实体。找到: {normalized_iphones}")
    else:
        logger.debug(f"extract_comparison_entities_refined: 查询 '{query}' 未被识别为对比性查询。")
    return entities

def chunks_relevant_to_query(chunks: list[str], query: str, min_hits: int = 1) -> bool:
    """判断知识块内容是否能直接用于回答本问题。"""
    keywords = set(re.findall(r'\w+', query.lower()))
    hits = 0
    for chunk in chunks:
        content = chunk.lower()
        if any(word in content for word in keywords):
            hits += 1
    return hits >= min_hits

def get_final_answer(query: str) -> dict:
    logger.info(f"get_final_answer: 开始处理查询: '{query}'")
    is_comparison = False

    comparison_entities = extract_comparison_entities_refined(query)
    context_chunks = []
    if comparison_entities:
        is_comparison = True
        temp_context_set = set()
        k_per_entity = 5
        for entity_name in comparison_entities:
            entity_context_result = retrieve_context(entity_name, k=k_per_entity)
            if entity_context_result.get("retrieved_chunks"):
                for chunk in entity_context_result["retrieved_chunks"]:
                    temp_context_set.add(chunk)
        context_chunks = list(temp_context_set)
    else:
        context_result = retrieve_context(query, k=10)
        context_chunks = context_result.get("retrieved_chunks", [])

    # === 只要知识块不相关，一律自由发挥 ===
    can_rag = len(context_chunks) > 0 and chunks_relevant_to_query(context_chunks, query)
    if not can_rag:
        logger.info("get_final_answer: 知识块无用，直接让AI自由发挥并加标注")
        llm_result = generate_answer_from_llm(query, [], is_comparison=is_comparison, allow_free_gen=True)
        if "error" in llm_result:
            return {"error": llm_result["error"]}
        # 若AI忘记加标注，则手动补充
        answer = llm_result.get("answer", "")
        if not answer.strip().startswith("【以下为AI自动生成，仅供参考】"):
            answer = "【以下为AI自动生成，仅供参考】" + answer
        return {"answer": answer}
    
    # 有相关知识块才走RAG
    llm_result = generate_answer_from_llm(query, context_chunks, is_comparison=is_comparison)
    if "error" in llm_result:
        return {"error": llm_result["error"]}
    return {"answer": llm_result.get("answer", "【以下为AI自动生成，仅供参考】AI 未能生成有效的回答。")}
