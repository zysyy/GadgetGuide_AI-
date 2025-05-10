# backend/qa_handler.py
import requests
import os
import re # 导入正则表达式模块

from langchain_ollama import OllamaEmbeddings
from .knowledge_base_processor import load_faiss_index
from .config import OLLAMA_EMBEDDING_MODEL, DEEPSEEK_API_KEY

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL_NAME = "deepseek-chat"

vector_db = load_faiss_index()

def reload_vector_db():
    global vector_db
    vector_db = load_faiss_index()
    if vector_db:
        print("qa_handler: FAISS 索引已重新加载。")
    else:
        print("qa_handler: FAISS 索引重新加载失败或索引为空。")
    return vector_db

def retrieve_context(query: str, k: int = 5) -> dict: # 将默认k值调整为一个适中的值，如5
    """
    根据用户查询从 FAISS 索引中检索相关上下文。
    """
    if vector_db is None:
        print(f"qa_handler.retrieve_context (query: '{query}'): 知识库索引未加载。")
        return {"error": "知识库索引未加载，请先处理知识库文档。"}
    try:
        print(f"qa_handler.retrieve_context: 正在为查询 '{query}' 检索上下文 (k={k})...")
        results = vector_db.similarity_search(query, k=k)
        if not results:
            print(f"qa_handler.retrieve_context: 未能为查询 '{query}' 找到相关信息。")
            return {"message": "未能从知识库中找到相关信息。", "retrieved_chunks": []}
        retrieved_chunks = [doc.page_content for doc in results]
        print(f"qa_handler.retrieve_context: 为查询 '{query}' 检索到 {len(retrieved_chunks)} 个 ({len(results)} docs) 相关片段。")
        return {"retrieved_chunks": retrieved_chunks}
    except Exception as e:
        print(f"qa_handler.retrieve_context: 检索上下文时出错 (查询: '{query}'): {e}")
        return {"error": f"检索上下文时出错: {e}"}

def generate_answer_from_llm(original_query: str, context_chunks: list[str], is_comparison: bool = False) -> dict:
    """
    使用检索到的上下文和用户查询，调用 DeepSeek API 生成答案。
    is_comparison: 标志是否为对比性查询，用于微调Prompt。
    """
    if not DEEPSEEK_API_KEY:
        print("qa_handler.generate_answer_from_llm: DEEPSEEK_API_KEY 未配置。")
        return {"error": "AI 服务配置不完整 (API Key缺失)。"}

    context_str = "\n\n---\n\n".join(context_chunks)
    
    # 根据是否为对比查询，可以微调Prompt
    if is_comparison:
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
    print(f"\nqa_handler.generate_answer_from_llm: 发送给 LLM 的 Prompt (用户原始查询: '{original_query}', 是否对比: {is_comparison}):\n{prompt_template}\n")

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEEPSEEK_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt_template}],
        "max_tokens": 1500, 
        "temperature": 0.3, # 对于对比和事实问答，更低的温度通常更好
    }

    try:
        print(f"qa_handler.generate_answer_from_llm: 正在调用 DeepSeek API (模型: {DEEPSEEK_MODEL_NAME})...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_data = response.json()
        
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
            return {"error": "AI 服务响应格式不正确."}
    except requests.exceptions.Timeout:
        print(f"qa_handler.generate_answer_from_llm: 调用 DeepSeek API 超时。")
        return {"error": "AI 服务请求超时，请稍后再试。"}
    except requests.exceptions.RequestException as e:
        print(f"qa_handler.generate_answer_from_llm: 调用 DeepSeek API 时发生网络错误: {e}")
        return {"error": f"与 AI 服务通信时发生网络错误: {e}"}
    except Exception as e:
        print(f"qa_handler.generate_answer_from_llm: 处理 LLM 响应时发生未知错误: {e}")
        return {"error": f"处理 AI 服务响应时发生未知错误: {e}"}


def extract_comparison_entities_refined(query: str) -> list[str]:
    """
    稍微改进的实体提取方法，尝试更准确地匹配 iPhone 型号。
    仍然是简化版，复杂的场景需要更专业的NLP工具。
    """
    query_lower = query.lower()
    entities = []
    
    # 改进的正则表达式，尝试匹配 "iphone" (可选空格) 数字 (可选 "pro", "plus", "max" 等)
    # 这个表达式仍然可以进一步优化以覆盖更多情况
    # (?i) 表示不区分大小写
    # (?:iphone\s?)? 匹配可选的 "iphone " 或 "iphone"
    # (\d+) 匹配一个或多个数字
    # (?:\s?(?:pro|plus|max|mini))? 匹配可选的型号后缀如 " pro", "pro", " plus" 等
    # 我们这里简化为直接匹配包含 iphone 和数字及 pro 的组合
    
    # 查找查询中所有类似 "iphone XX pro" 或 "iphone XX" 的模式
    # re.findall 会找到所有不重叠的匹配项
    # 这里的正则表达式需要仔细设计以匹配您期望的实体格式
    # 例如："iphone 15 pro", "iphone 16 pro", "iphone15pro", "iphone16"
    # 我们需要提取出规范化的名称，例如 "iphone 15 pro" 和 "iphone 16 pro"
    
    # 一个更具体的模式，假设实体格式总是 "iphone" + 数字 + 可选的 "pro"
    # (?i) 表示不区分大小写 (虽然我们已经 query_lower 了)
    # \s* 匹配0或多个空格
    # (?: ... )? 表示一个可选的非捕获组
    pattern = r"(iphone\s*\d+\s*(?:pro|plus|max|mini)?|iphone\s*\d+)" # 匹配 iphone 数字 后可选 pro/plus/max/mini
    
    # 尝试从查询中提取两个主要的 iPhone 实体
    # 这个逻辑仍然非常简化，并且高度依赖查询的格式
    if "和" in query and ("对比" in query or "区别" in query or "升级" in query):
        parts = query_lower.split("和")
        if len(parts) >= 2:
            # 提取 "和" 前面的实体
            match1 = re.search(pattern, parts[0])
            if match1:
                entities.append(match1.group(1).replace(" ", "").strip()) # 规范化，去除空格

            # 提取 "和" 后面的实体 (只取第一个匹配到的)
            # 需要清理掉对比相关的词汇
            part2_cleaned = parts[1]
            for keyword in ["对比", "之间", "的", "配置", "升级", "区别", "怎么样", "一些信息"]:
                part2_cleaned = part2_cleaned.replace(keyword, "")
            
            match2 = re.search(pattern, part2_cleaned)
            if match2:
                entity2_normalized = match2.group(1).replace(" ", "").strip()
                if entity2_normalized not in entities: # 避免重复
                     entities.append(entity2_normalized)
    
    # 如果找到了两个不同的、符合模式的实体，则认为是对比查询
    if len(entities) == 2 and entities[0] != entities[1]:
        # 可以进一步规范化实体名称，例如确保 "iphone15pro" 和 "iphone 15 pro" 都被识别
        # 这里我们假设提取到的已经是比较规范的了
        return entities
    return []


def get_final_answer(query: str) -> dict:
    """
    完整的 RAG 流程：检索上下文 -> LLM 生成答案。
    """
    print(f"\nqa_handler.get_final_answer: 开始处理查询: '{query}'")
    
    context_chunks = []
    retrieved_something = False
    is_comparison = False # 标志是否为对比查询，用于选择Prompt

    comparison_entities = extract_comparison_entities_refined(query) # 使用改进的提取函数

    if comparison_entities:
        print(f"qa_handler.get_final_answer: 检测到对比性查询，实体: {comparison_entities}")
        is_comparison = True
        temp_context_set = set() 
        k_per_entity = 5 

        for entity_raw in comparison_entities:
            # 为每个实体构造一个更具体的检索查询，可以加上 "技术规格", "特点" 等
            # entity_query = f"{entity_raw} 的技术规格和主要特点"
            # 或者更简单，直接用实体名，因为我们的知识库主要是规格文档
            entity_query = entity_raw # 直接使用提取到的实体名进行检索
            print(f"qa_handler.get_final_answer: 正在为实体 '{entity_raw}' (使用查询 '{entity_query}') 检索上下文...")
            entity_context_result = retrieve_context(entity_query, k=k_per_entity)
            
            if entity_context_result.get("retrieved_chunks"):
                for chunk in entity_context_result["retrieved_chunks"]:
                    temp_context_set.add(chunk)
                retrieved_something = True
        
        context_chunks = list(temp_context_set)
        if not context_chunks:
             print(f"qa_handler.get_final_answer: 分别检索对比实体后，未能找到足够信息。")
             return {"answer": f"抱歉，未能充分检索到关于您提及产品 ({', '.join(comparison_entities)}) 的详细信息以进行对比。"}
    
    else: 
        print(f"qa_handler.get_final_answer: 按普通查询处理。")
        # 对于普通查询，您之前用 k=10 检索到了双方信息，虽然不均衡，但LLM能处理
        # 我们这里也用 k=10 作为默认值给 retrieve_context (如果没传k)
        # 或者在这里明确指定，比如 k=7 或 k=10
        context_result = retrieve_context(query, k=10) # 默认k值可以根据之前的测试调整
        if "error" in context_result:
            return {"error": context_result["error"]}
        if not context_result.get("retrieved_chunks"):
            return {"answer": f"抱歉，根据我目前掌握的关于您所咨询产品的信息，暂时无法回答您关于“{query}”的问题。您可以尝试换个问法或咨询其他方面的信息。"}
        context_chunks = context_result["retrieved_chunks"]
        retrieved_something = True

    if not retrieved_something or not context_chunks:
        print(f"qa_handler.get_final_answer: 最终未能检索到任何上下文信息。")
        return {"answer": f"抱歉，我没有找到与您查询“{query}”相关的足够信息。"}

    llm_result = generate_answer_from_llm(query, context_chunks, is_comparison=is_comparison) 
    
    if "error" in llm_result:
        return {"error": llm_result["error"]}
    
    return {"answer": llm_result.get("answer", "抱歉，AI 未能生成有效的回答。")}