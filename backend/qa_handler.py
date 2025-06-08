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


def extract_comparison_entities_refined(query: str) -> list[str]:
    """
    通用化的对比实体提取函数：
    - 不再仅限于 iPhone，而是适配任意英文/数字/连字符/空格组合的实体
    - 仍使用关键词判断是否是对比问题
    """
    pattern = r"([a-zA-Z0-9\- ]{2,})"
    comparison_keywords = ["对比", "区别", "升级", "和...相比", "与...比较", "差异", "不同点"]
    query_lower = query.lower()
    is_likely_comparison = any(keyword in query for keyword in comparison_keywords) and \
                           ("和" in query or "与" in query or "跟" in query)
    if is_likely_comparison:
        found_entities = re.findall(pattern, query)
        normalized_entities = sorted(list(set([name.strip() for name in found_entities if len(name.strip()) > 1])))
        if len(normalized_entities) >= 2:
            logger.info(f"extract_comparison_entities_refined: 识别到对比实体: {normalized_entities} 从查询: '{query}'")
            return normalized_entities[:2]  # 只返回前两个实体
        else:
            logger.debug(f"extract_comparison_entities_refined: 未能提取到至少两个实体。找到: {normalized_entities}")
    else:
        logger.debug(f"extract_comparison_entities_refined: 查询 '{query}' 未被识别为对比性查询。")
    return []


def chunks_relevant_to_query(chunks: list[str], query: str, min_hits: int = 1) -> bool:
    """
    判断知识块内容是否能直接用于回答本问题（简单关键字匹配）
    """
    keywords = set(re.findall(r'\w+', query.lower()))
    hits = 0
    for chunk in chunks:
        content = chunk.lower()
        if any(word in content for word in keywords):
            hits += 1
    return hits >= min_hits


def generate_answer_from_llm(
    original_query: str,
    context_chunks: list[str],
    is_comparison: bool = False,
    allow_free_gen: bool = False
) -> dict:
    """
    调用 DeepSeek API 生成答案。
    - 提示词根据上下文情况动态调整，增强回答质量。
    """
    if not DEEPSEEK_API_KEY:
        logger.error("generate_answer_from_llm: DEEPSEEK_API_KEY 未配置。")
        return {"error": "AI 服务配置不完整 (API Key缺失)。"}

    context_str = "\n\n---\n\n".join(context_chunks)

    # === 优化后的 Prompt Instruction，细化对比 / 普通 / 自由生成场景
    if is_comparison:
        prompt_instruction = (
            "你是一个专业的电子产品对比分析师。请根据下方“参考信息”详细对比用户问题中提到的两款产品。"
            "重点列出它们在性能、功能、外观、特色等方面的差异。"
            "如果信息不足，请如实说明，不要编造内容。"
            "请以条理清晰的要点或编号列表形式总结。"
        )
    elif allow_free_gen:
        prompt_instruction = (
            "你是一个乐于助人的AI助手。如果下方“参考信息”为空或无用，请基于常识和推理自由回答用户问题。"
            "务必在回答开头加上：“【以下为AI自动生成，仅供参考】”。"
            "如果有“参考信息”，优先使用，答案应专业简洁、直接相关。"
        )
    else:
        prompt_instruction = (
            "你是一个专业的AI助手。请严格根据下方“参考信息”回答用户问题，确保答案准确、相关、简明扼要。"
            "如果信息不足，也请如实说明，不要编造内容。"
        )

    prompt_template = f"""{prompt_instruction}

参考信息：
---
{context_str}
---
用户问题：{original_query}

请给出您的详细、专业的回答：
"""

    logger.debug(f"generate_answer_from_llm: 发送给 LLM 的 Prompt:\n{prompt_template}\n")

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
                logger.info("generate_answer_from_llm: 成功获取到答案。")
                return {"answer": message_content.strip()}
            else:
                logger.warning("generate_answer_from_llm: DeepSeek API 返回了空的答案。")
                return {"error": "AI 服务返回了空的答案内容。"}
        else:
            logger.error(f"generate_answer_from_llm: DeepSeek API 响应格式不符合预期: {response_data}")
            return {"error": "AI 服务响应格式不正确。"}
    except requests.exceptions.Timeout:
        logger.error("generate_answer_from_llm: DeepSeek API 超时。")
        return {"error": "AI 服务请求超时，请稍后再试。"}
    except requests.exceptions.RequestException as e:
        logger.error(f"generate_answer_from_llm: DeepSeek API 请求错误: {e}", exc_info=True)
        return {"error": f"与 AI 服务通信时发生错误: {e}"}
    except Exception as e:
        logger.error(f"generate_answer_from_llm: 处理 LLM 响应或未知错误: {e}", exc_info=True)
        return {"error": f"处理 AI 服务响应时发生未知错误: {e}"}


def get_final_answer(query: str) -> dict:
    """
    核心对话入口：智能判断是否对比问题，是否有可用知识库，智能切换自由生成/基于知识的回答。
    """
    logger.info(f"get_final_answer: 开始处理查询: '{query}'")
    is_comparison = False

    # 先判断是否是对比问题
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

    # 如果知识块无用，则走自由生成
    can_rag = len(context_chunks) > 0 and chunks_relevant_to_query(context_chunks, query)
    if not can_rag:
        logger.info("get_final_answer: 知识块无用，直接让AI自由发挥并加标注。")
        llm_result = generate_answer_from_llm(query, [], is_comparison=is_comparison, allow_free_gen=True)
        if "error" in llm_result:
            return {"error": llm_result["error"]}
        answer = llm_result.get("answer", "")
        if not answer.strip().startswith("【以下为AI自动生成，仅供参考】"):
            answer = "【以下为AI自动生成，仅供参考】" + answer
        return {"answer": answer}

    # 有可用知识块则优先使用
    llm_result = generate_answer_from_llm(query, context_chunks, is_comparison=is_comparison)
    if "error" in llm_result:
        return {"error": llm_result["error"]}
    return {"answer": llm_result.get("answer", "【以下为AI自动生成，仅供参考】AI 未能生成有效的回答。")}
