# backend/qa_handler.py
import requests
import os
import re
import logging # 确保 logging 已导入

from langchain_ollama import OllamaEmbeddings
from .knowledge_base_processor import load_faiss_index
from .config import OLLAMA_EMBEDDING_MODEL, DEEPSEEK_API_KEY

# 获取 logger 实例 (与 main.py 和其他模块一致或作为子 logger)
logger = logging.getLogger("gadgetguide_ai.qa")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL_NAME = "deepseek-chat"

# 在模块加载时尝试加载 FAISS 索引
vector_db = load_faiss_index() # load_faiss_index 内部应已有日志

def reload_vector_db():
    """重新加载 FAISS 索引，用于索引更新后。"""
    global vector_db # 明确使用全局变量
    vector_db = load_faiss_index()
    if vector_db:
        logger.info("FAISS 索引已在 qa_handler 中重新加载。")
    else:
        logger.warning("FAISS 索引在 qa_handler 中重新加载失败或索引为空。")
    return vector_db

def retrieve_context(query: str, k: int = 5) -> dict: # 默认 k=5 用于单个实体检索
    """
    根据用户查询从 FAISS 索引中检索相关上下文。
    返回一个包含 'retrieved_chunks' 列表或 'error'/'message' 键的字典。
    """
    if vector_db is None:
        logger.warning(f"retrieve_context (query: '{query}', k:{k}): 知识库索引未加载。")
        return {"error": "知识库索引未加载，请先处理知识库文档。"}

    try:
        logger.info(f"retrieve_context: 正在为查询 '{query}' 检索上下文 (k={k})...")
        results = vector_db.similarity_search(query, k=k)
        
        if not results:
            logger.info(f"retrieve_context: 未能为查询 '{query}' (k={k}) 找到相关信息。")
            return {"message": "未能从知识库中找到相关信息。", "retrieved_chunks": []}

        retrieved_chunks = [doc.page_content for doc in results]
        logger.info(f"retrieve_context: 为查询 '{query}' (k={k}) 检索到 {len(retrieved_chunks)} 个 ({len(results)} docs) 相关片段。")
        return {"retrieved_chunks": retrieved_chunks}
    except Exception as e:
        logger.error(f"retrieve_context: 检索上下文时出错 (查询: '{query}', k:{k}): {e}", exc_info=True)
        return {"error": f"检索上下文时出错: {e}"}

def generate_answer_from_llm(original_query: str, context_chunks: list[str], is_comparison: bool = False) -> dict:
    """
    使用检索到的上下文和用户查询，调用 DeepSeek API 生成答案。
    is_comparison: 标志是否为对比性查询，用于微调Prompt。
    """
    if not DEEPSEEK_API_KEY:
        logger.error("generate_answer_from_llm: DEEPSEEK_API_KEY 未配置。")
        return {"error": "AI 服务配置不完整 (API Key缺失)。"}

    context_str = "\n\n---\n\n".join(context_chunks) # 将上下文片段用更明显的分隔符连接起来
    
    if is_comparison:
        # 这个 Prompt 您之前测试效果不错，可以继续使用或微调
        prompt_instruction = f"""
你是一个专业的电子产品对比助手。请严格根据下面提供的“参考信息”，清晰地对比用户问题中提到的两款产品（例如 iPhone 16 Pro 和 iPhone 15 Pro）在主要配置和特性上的具体升级点或不同之处。
请以要点或列表形式（例如使用1., 2., 3.或项目符号）进行总结。
如果参考信息中包含了双方在某个方面的具体参数，请尽量指出。
如果对于某些方面，参考信息只提到了其中一款产品的新特性而没有另一款的对应信息，你可以指出这是一款产品的新特性，或者说明另一款产品未提及该信息。
如果参考信息不足以进行全面的对比，或者无法明确判断哪些是“升级”，请总结你已知的、可对比的信息，并可以补充说“更详细或其他方面的对比信息目前无法从参考资料中提供”。
请不要编造“参考信息”中没有的内容。请不要在回答的开头说“根据参考信息...”，直接开始对比即可。
"""
    else:
        prompt_instruction = f"""
你是一个乐于助人的AI助手，专门负责根据提供的产品信息来回答用户的问题。请严格根据下面提供的“参考信息”来回答用户的问题。
答案应尽可能简洁、准确，并直接与参考信息相关。
如果参考信息中没有足够的内容来回答问题，请明确告知用户“根据我目前掌握的关于您所咨询产品的信息，无法回答您关于‘{original_query}’的具体问题”，不要编造答案。
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
    # 对于可能非常长的Prompt，使用 DEBUG 级别更合适，避免淹没 INFO 级别的日志
    logger.debug(f"generate_answer_from_llm: 发送给 LLM 的 Prompt (用户原始查询: '{original_query}', 是否对比: {is_comparison}):\n{prompt_template}\n")

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEEPSEEK_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt_template}],
        "max_tokens": 1500, 
        "temperature": 0.3, # 保持较低的温度以获取事实性回答
    }

    try:
        logger.info(f"generate_answer_from_llm: 正在调用 DeepSeek API (模型: {DEEPSEEK_MODEL_NAME})...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60) # 保持60秒超时
        response.raise_for_status()  # 检查 HTTP 错误 (4xx 或 5xx)
        response_data = response.json()
        
        if response_data.get("choices") and len(response_data["choices"]) > 0:
            message_content = response_data["choices"][0].get("message", {}).get("content", "")
            if message_content: # 即使是空字符串也认为是有回答，但通常LLM不会返回纯空
                logger.info(f"generate_answer_from_llm: 从 DeepSeek API 获取到答案。")
                return {"answer": message_content.strip()} # strip() 去除首尾空白
            else:
                logger.warning("generate_answer_from_llm: DeepSeek API 返回了空的答案内容 (choices[0].message.content 为空)。")
                return {"error": "AI 服务返回了空的答案内容。"}
        else:
            logger.error(f"generate_answer_from_llm: DeepSeek API 响应格式不符合预期 (缺少 choices 或 choices 为空): {response_data}")
            return {"error": "AI 服务响应格式不正确。"}
    except requests.exceptions.Timeout:
        logger.error(f"generate_answer_from_llm: 调用 DeepSeek API 超时。")
        return {"error": "AI 服务请求超时，请稍后再试。"}
    except requests.exceptions.RequestException as e: # 更广泛地捕获 requests 相关的异常
        logger.error(f"generate_answer_from_llm: 调用 DeepSeek API 时发生网络或请求错误: {e}", exc_info=True)
        return {"error": f"与 AI 服务通信时发生错误: {e}"}
    except Exception as e: # 捕获其他所有潜在异常，例如 response.json() 失败等
        logger.error(f"generate_answer_from_llm: 处理 LLM 响应或未知错误: {e}", exc_info=True)
        return {"error": f"处理 AI 服务响应时发生未知错误: {e}"}


def extract_comparison_entities_refined(query: str) -> list[str]:
    """
    尝试提取对比查询中的 iPhone 实体。
    仍然是简化版，需要根据实际查询模式不断优化。
    """
    query_lower = query.lower()
    entities = []
    
    # 模式：iphoneX pro 和 iphoneY pro, iphoneX 和 iphoneY
    # 允许 "iphone" 和 数字之间有可选空格，允许 "pro" / "plus" / "max" / "mini" 后缀
    # 这个正则表达式会捕获完整的型号名称，例如 "iphone 15 pro" 或 "iphone 16"
    # 它通过 (iphone\s*\d+\s*(?:pro|plus|max|mini)?) 匹配一个完整的型号，
    # 然后通过 | (iphone\s*\d+) 匹配一个不带后缀的型号。
    # (?:...) 是非捕获组。
    pattern = r"(iphone\s*\d+\s*(?:pro|plus|max|mini|se)?|iphone\s*\d+)" # 增加了 se
    
    # 首先检查是否包含明确的对比性关键词
    comparison_keywords = ["对比", "区别", "升级", "和...相比", "与...比较"]
    is_likely_comparison = any(keyword in query for keyword in comparison_keywords) and \
                           ("和" in query or "与" in query or "跟" in query)

    if is_likely_comparison:
        # 使用 re.findall 找到所有匹配的 iPhone 型号
        found_iphones = re.findall(pattern, query_lower)
        
        # 去重并规范化 (例如去除多余空格，虽然 pattern 本身已经考虑了)
        normalized_iphones = sorted(list(set([name.replace(" ", "").strip() for name in found_iphones])))
        
        if len(normalized_iphones) >= 2:
            # 如果找到了两个或以上不同的 iPhone 型号，取前两个作为对比实体
            # （更复杂的逻辑可以处理超过两个实体的情况，或选择最相关的两个）
            entities = normalized_iphones[:2] 
            logger.info(f"extract_comparison_entities_refined: 识别到对比实体: {entities} 从查询: '{query}'")
        else:
            logger.debug(f"extract_comparison_entities_refined: 未能从对比性查询 '{query}' 中提取到至少两个不同的iPhone实体。找到: {normalized_iphones}")
    else:
        logger.debug(f"extract_comparison_entities_refined: 查询 '{query}' 未被识别为对比性查询。")
            
    return entities


def get_final_answer(query: str) -> dict:
    """
    完整的 RAG 流程：检索上下文 -> LLM 生成答案。
    """
    logger.info(f"get_final_answer: 开始处理查询: '{query}'")
    
    context_chunks = []
    retrieved_something = False
    is_comparison = False 

    comparison_entities = extract_comparison_entities_refined(query)

    if comparison_entities: # 如果成功提取到两个对比实体
        is_comparison = True
        logger.info(f"get_final_answer: 检测到对比性查询，实体: {comparison_entities}")
        temp_context_set = set() 
        # 可以根据实体数量和上下文质量需求调整 k_per_entity
        k_per_entity = 5 # 为每个对比实体检索N个最相关的块

        for entity_name in comparison_entities:
            # 构造针对每个实体的具体检索查询
            # 之前的 'iphone15pro' 作为查询效果不错，因为知识库主要是规格文档
            entity_query = entity_name 
            logger.info(f"get_final_answer: 正在为实体 '{entity_name}' (使用查询 '{entity_query}') 检索上下文...")
            entity_context_result = retrieve_context(entity_query, k=k_per_entity)
            
            if entity_context_result.get("retrieved_chunks"):
                for chunk in entity_context_result["retrieved_chunks"]:
                    temp_context_set.add(chunk) # 用集合去重
                if entity_context_result["retrieved_chunks"]: # 只要有一个实体检索到内容就算成功
                    retrieved_something = True 
        
        context_chunks = list(temp_context_set)
        if not context_chunks: # 如果分别查询后仍然没内容
             logger.warning(f"get_final_answer: 分别检索对比实体后，未能找到足够信息。")
             # 仍然可以尝试让LLM基于原始查询和这个“空”上下文去回复，LLM的prompt会处理这种情况
             # 或者直接返回一个预设的“信息不足以对比”的答案
             return {"answer": f"抱歉，未能充分检索到关于您提及产品 ({', '.join(comparison_entities)}) 的详细信息以进行对比。"}
    
    else: # 非对比性查询，或实体提取失败
        logger.info(f"get_final_answer: 按普通查询处理。")
        # 对于普通查询，k=10 似乎效果不错
        context_result = retrieve_context(query, k=10) 
        if "error" in context_result:
            return {"error": context_result["error"]}
        if not context_result.get("retrieved_chunks"):
            return {"answer": f"抱歉，根据我目前掌握的关于您所咨询产品的信息，暂时无法回答您关于“{query}”的问题。您可以尝试换个问法或咨询其他方面的信息。"}
        context_chunks = context_result["retrieved_chunks"]
        if context_chunks:
            retrieved_something = True

    if not retrieved_something or not context_chunks:
        logger.warning(f"get_final_answer: 最终未能检索到任何上下文信息用于查询 '{query}'。")
        # 即使到这里 context_chunks 还是空的，也把原始问题和空上下文给LLM，让Prompt中的指令来处理
        # return {"answer": f"抱歉，我没有找到与您查询“{query}”相关的足够信息。"}
    
    # 即使 context_chunks 可能为空，也把原始查询和（可能为空的）上下文交给 LLM
    # LLM 的 Prompt 设计了在信息不足时如何回应
    llm_result = generate_answer_from_llm(query, context_chunks, is_comparison=is_comparison) 
    
    if "error" in llm_result:
        return {"error": llm_result["error"]}
    
    return {"answer": llm_result.get("answer", "抱歉，AI 未能生成有效的回答。")}