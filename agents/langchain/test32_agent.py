"""
langchain_memory.py - 基于 LangChain 的记忆系统

模仿 Mem0 的设计思路，使用 LangChain 的技术栈实现。

核心能力：
1. 添加记忆（向量化 + 存储 + 实体抽取）
2. 搜索记忆（混合搜索 + 实体提升）
3. 增量存储（避免重复）
"""

import json
import uuid
import hashlib
from datetime import datetime
from typing import Any, Optional
import sqlite3

# LangChain 最新版本中 OllamaEmbeddings 需从子模块导入
from langchain_ollama import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage


class EntityExtractor:
    """
    实体抽取器
    
    使用 LLM 从文本中提取结构化实体信息。
    这是 Mem0 的核心能力之一。
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def extract(self, text: str) -> dict:
        """
        从文本中提取实体
        
        示例：
        >>> extractor.extract("我叫王小明，做登录功能测试")
        {"person": "王小明", "project": "登录功能", "task": "测试", ...}
        """
        prompt = f"""
        从以下文本中提取关键实体信息，返回 JSON 格式。
        不要添加任何额外说明，只返回 JSON。
        
        文本：{text}
        
        输出格式：
        {{
            "person": "人物名称，没有则为 null",
            "project": "项目名称，没有则为 null",
            "task": "任务或需求，没有则为 null",
            "preference": "偏好或习惯，没有则为 null",
            "status": "状态或结果，没有则为 null"
        }}
        """
        
        # 调用 LLM 提取实体
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            # 解析返回的 JSON
            entities = json.loads(response.content.strip())
            return entities
        except (json.JSONDecodeError, AttributeError):
            # 如果解析失败，返回空实体
            return {"person": None, "project": None, "task": None,
                    "preference": None, "status": None}


class SimpleMemory:
    """
    简化版记忆系统
    
    实现 Mem0 的核心功能：
    - 添加记忆（自动向量化 + 实体抽取）
    - 搜索记忆（向量 + BM25 混合搜索 + 实体提升）
    - 增量存储（防重复）
    """
    
    def __init__(self, 
                 model_type: str = "ollama",
                 llm_model: str = "qwen3.5:0.8b",
                 embed_model: str = "nomic-embed-text",
                 ollama_base_url: str = "http://localhost:11434",
                 openai_api_key: str = None,
                 openai_api_base: str = None,
                 persist_dir: str = "./memory_db"):
        """
        初始化记忆系统
        
        Args:
            model_type: "ollama" 或 "openai"
            llm_model: 对话模型名称
            embed_model: embedding 模型名称
            ollama_base_url: Ollama 服务地址
            openai_api_key: OpenAI API Key
            openai_api_base: OpenAI 兼容 API 地址
            persist_dir: 数据持久化目录
        """
        self.persist_dir = persist_dir
        
        # 1. 初始化 LLM
        if model_type == "ollama":
            self.llm = ChatOllama(
                model=llm_model,
                base_url=ollama_base_url,
                temperature=0.1
            )
            self.embedder = OllamaEmbeddings(
                model=embed_model,
                base_url=ollama_base_url
            )
        elif model_type == "openai":
            self.llm = ChatOpenAI(
                model=llm_model,
                api_key=openai_api_key,
                base_url=openai_api_base,
                temperature=0.1
            )
            self.embedder = OpenAIEmbeddings(
                model=embed_model or "text-embedding-3-small",
                api_key=openai_api_key,
                base_url=openai_api_base
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 2. 初始化向量存储（使用 ChromaDB）
        # 注意：langchain-chroma 最新版参数名已改为 embeddings
        import os
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.vectorstore = Chroma(
            collection_name="memories",
            persist_directory=self.persist_dir,
            embeddings=self.embedder  # 旧版参数名是 embedding_function
        )
        
        # 3. 初始化实体抽取器
        self.entity_extractor = EntityExtractor(self.llm)
        
        # 4. 初始化 SQLite（用于存储结构化数据）
        self._init_sqlite()
    
    def _init_sqlite(self):
        """初始化 SQLite 数据库"""
        self.conn = sqlite3.connect(f"{self.persist_dir}/memory.db")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                doc_id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                entities TEXT DEFAULT '{}',
                user_id TEXT,
                agent_id TEXT,
                created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
                updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_value TEXT NOT NULL,
                FOREIGN KEY (doc_id) REFERENCES memories(doc_id)
            )
        """)
        self.conn.commit()
    
    def add(self, text: str, user_id: str = None, 
            agent_id: str = None) -> str:
        """
        添加一条记忆
        
        流程：
        1. 检查是否已存在相似记忆（避免重复）
        2. 抽取实体
        3. 向量化
        4. 存储到向量库 + SQLite
        
        Args:
            text: 记忆文本
            user_id: 用户标识
            agent_id: Agent 标识
        
        Returns:
            doc_id: 记忆唯一标识
        """
        # 1. 检查是否已存在相似记忆（增量判断）
        existing = self._find_similar(text, threshold=0.92)
        if existing:
            # 已有相似记忆 → 更新，不新增
            doc_id = existing["doc_id"]
            self._update_memory(doc_id, text)
            return doc_id
        
        # 2. 抽取实体
        entities = self.entity_extractor.extract(text)
        
        # 3. 生成唯一 ID
        doc_id = str(uuid.uuid4())
        
        # 4. 向量化并存储到 ChromaDB
        doc = Document(
            page_content=text,
            metadata={
                "doc_id": doc_id,
                "user_id": user_id,
                "agent_id": agent_id,
                "created_at": datetime.now().isoformat()
            }
        )
        self.vectorstore.add_documents([doc])
        
        # 5. 存储结构数据到 SQLite
        self.conn.execute(
            "INSERT INTO memories (doc_id, text, entities, user_id, agent_id) VALUES (?, ?, ?, ?, ?)",
            (doc_id, text, json.dumps(entities, ensure_ascii=False), user_id, agent_id)
        )
        
        # 6. 存储实体索引（用于实体提升搜索）
        for etype, evalue in entities.items():
            if evalue:
                self.conn.execute(
                    "INSERT INTO entities (doc_id, entity_type, entity_value) VALUES (?, ?, ?)",
                    (doc_id, etype, evalue)
                )
        
        self.conn.commit()
        return doc_id
    
    def search(self, query: str, k: int = 5, user_id: str = None,
               alpha: float = 0.7) -> list:
        """
        搜索记忆（混合搜索：向量 + BM25 + 实体提升）
        
        搜索策略：
        1. 向量相似度搜索（语义理解，权重 alpha）
        2. BM25 关键词搜索（精确匹配，权重 1-alpha）
        3. 实体匹配提升（辅助加权）
        
        Args:
            query: 搜索查询
            k: 返回结果数量
            user_id: 筛选用户
            alpha: 向量搜索权重，默认 0.7，BM25 权重为 0.3
        
        Returns:
            list[dict]: 记忆列表，每个包含 text, score, entities
        """
        # ========== 1. 向量相似度搜索 ==========
        vector_results = self.vectorstore.similarity_search_with_score(query, k=k * 2)
        
        # ========== 2. BM25 关键词搜索 ==========
        bm25_results = self._bm25_search(query, k=k * 2)
        
        # ========== 3. 实体抽取 ==========
        query_entities = self.entity_extractor.extract(query)
        
        # ========== 4. 混合评分 ==========
        # 收集所有候选 doc_id
        all_doc_ids = set()
        for doc, _ in vector_results:
            all_doc_ids.add(doc.metadata.get("doc_id", ""))
        for item in bm25_results:
            all_doc_ids.add(item["doc_id"])
        
        # 计算每个候选的综合得分
        scored_results = []
        for doc_id in all_doc_ids:
            # 向量得分（分数越小越相似）
            vector_score = None
            for doc, score in vector_results:
                if doc.metadata.get("doc_id") == doc_id:
                    vector_score = score
                    break
            
            # BM25 得分（分数越大越匹配，需要归一化）
            bm25_score = None
            for item in bm25_results:
                if item["doc_id"] == doc_id:
                    bm25_score = item["score"]
                    break
            
            # 获取记忆文本和实体
            memory = self._get_memory_by_id(doc_id)
            if not memory:
                continue
            
            # 4a. 基础得分：向量 + BM25 混合
            if vector_score is not None and bm25_score is not None:
                # 向量分数归一化到 [0, 1]，分数越小越相似
                # BM25 分数归一化，分数越大越匹配 → 取反
                normalized_vector = min(vector_score, 1.0)  # 已是越小越好
                normalized_bm25 = 1.0 / (1.0 + bm25_score)  # 转为越小越好
                
                # 混合得分（分数越小越相似，越靠前）
                base_score = normalized_vector * alpha + normalized_bm25 * (1 - alpha)
            elif vector_score is not None:
                base_score = vector_score
            elif bm25_score is not None:
                base_score = 1.0 / (1.0 + bm25_score)
            else:
                continue
            
            # 4b. 实体提升：如果查询实体匹配到记忆中的实体，降分（更靠前）
            doc_entities = json.loads(memory.get("entities", "{}"))
            if doc_entities and query_entities:
                for key, value in query_entities.items():
                    if value and doc_entities.get(key) and \
                       value.lower() in doc_entities[key].lower():
                        # 实体匹配成功 → 分数降低，排序更靠前
                        base_score *= 0.8
            
            scored_results.append({
                "text": memory["text"],
                "score": round(base_score, 4),
                "entities": doc_entities,
                "doc_id": doc_id,
                "vector_score": vector_score,
                "bm25_score": bm25_score
            })
        
        # 5. 按最终得分排序（分数越小越靠前）
        scored_results.sort(key=lambda x: x["score"])
        
        # 6. 返回 Top-K
        return scored_results[:k]
    
    def _bm25_search(self, query: str, k: int = 5) -> list:
        """
        BM25 关键词搜索
        
        BM25 是一种基于词频的经典检索算法，擅长精确匹配关键词。
        支持中英文分词（中文使用 jieba）。
        """
        from rank_bm25 import BM25Okapi
        
        cursor = self.conn.execute("SELECT doc_id, text FROM memories")
        rows = cursor.fetchall()
        if not rows:
            return []
        
        doc_ids = [r[0] for r in rows]
        texts = [r[1] for r in rows]
        
        # 分词：中文用 jieba，英文用 split
        try:
            import jieba
            def tokenize(text):
                return [w for w in jieba.cut(text.lower()) if len(w) > 1]
        except ImportError:
            # 没有 jieba 就用简单的空格分词
            def tokenize(text):
                return [w.lower() for w in text.split() if len(w) > 1]
        
        tokenized_texts = [tokenize(t) for t in texts]
        bm25 = BM25Okapi(tokenized_texts)
        
        query_tokens = tokenize(query)
        scores = bm25.get_scores(query_tokens)
        
        results = [
            {"doc_id": doc_ids[i], "score": scores[i], "text": texts[i]}
            for i in range(len(doc_ids)) if scores[i] > 0
        ]
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]
    
    def _get_memory_by_id(self, doc_id: str) -> dict:
        """根据 doc_id 获取记忆"""
        cursor = self.conn.execute(
            "SELECT doc_id, text, entities FROM memories WHERE doc_id = ?",
            (doc_id,)
        )
        row = cursor.fetchone()
        if row:
            return {"doc_id": row[0], "text": row[1], "entities": row[2]}
        return None
    
    def get_all(self, user_id: str = None) -> list:
        """获取所有记忆"""
        if user_id:
            cursor = self.conn.execute(
                "SELECT doc_id, text, entities FROM memories WHERE user_id = ?",
                (user_id,)
            )
        else:
            cursor = self.conn.execute(
                "SELECT doc_id, text, entities FROM memories"
            )
        
        return [
            {"doc_id": r[0], "text": r[1], "entities": json.loads(r[2])}
            for r in cursor.fetchall()
        ]
    
    def delete(self, doc_id: str):
        """删除一条记忆"""
        self.vectorstore.delete([doc_id])
        self.conn.execute("DELETE FROM memories WHERE doc_id = ?", (doc_id,))
        self.conn.execute("DELETE FROM entities WHERE doc_id = ?", (doc_id,))
        self.conn.commit()
    
    def _find_similar(self, text: str, threshold: float = 0.92) -> dict:
        """查找是否已有相似记忆"""
        results = self.vectorstore.similarity_search_with_score(text, k=1)
        if results and results[0][1] < threshold:
            doc_id = results[0][0].metadata.get("doc_id", "")
            cursor = self.conn.execute(
                "SELECT text, entities FROM memories WHERE doc_id = ?",
                (doc_id,)
            )
            row = cursor.fetchone()
            if row:
                return {"doc_id": doc_id, "text": row[0],
                        "entities": json.loads(row[1])}
        return None
    
    def _update_memory(self, doc_id: str, new_text: str):
        """更新已有记忆"""
        self.vectorstore.delete([doc_id])
        doc = Document(page_content=new_text, metadata={"doc_id": doc_id})
        self.vectorstore.add_documents([doc])
        self.conn.execute(
            "UPDATE memories SET text = ?, updated_at = datetime('now') WHERE doc_id = ?",
            (new_text, doc_id)
        )
        self.conn.commit()
    
    def _get_entities(self, doc_id: str) -> dict:
        """获取一条记忆的实体"""
        cursor = self.conn.execute(
            "SELECT entities FROM memories WHERE doc_id = ?",
            (doc_id,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else {}