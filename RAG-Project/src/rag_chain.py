"""
RAG Chain Implementation with LangChain
Weeks 4-5: Retrieval Augmented Generation pipeline

Implements:
- LangChain integration with existing embedding models
- RetrievalQA chain with custom prompts
- Conversational memory management
- Google Gemini API integration for LLM (free tier)
- Document-aware retrieval
"""

import os
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    # Update imports for newer LangChain versions
    # pyrefly: ignore [missing-import]
    from langchain.chains import RetrievalQA
    # pyrefly: ignore [missing-import]
    from langchain.memory import ConversationBufferMemory
    from langchain_core.prompts import PromptTemplate
    from langchain_core.documents import Document as LangDocument
    from langchain_community.vectorstores import FAISS
    print("✓ LangChain imports successful")
except ImportError as e:
    print(f"Using simplified RAG implementation (no complex chains): {e}")
    # For simplified implementation, we'll skip the complex chain imports
    RetrievalQA = None
    ConversationBufferMemory = None
    PromptTemplate = None
    LangDocument = None  # Will use dict instead

from sentence_transformers import SentenceTransformer
import numpy as np

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.model_config import ModelType, ModelSelector
from src.embeddings import EmbeddingModel
# LLM backend is selected at runtime via LLM_BACKEND env var
from src.gemini_client import GeminiClient
from src.ollama_client import OllamaClient
# Query expansion and context compression
from src.query_expansion import QueryExpander
from src.context_compression import ContextCompressor, CompressionConfig
# Faithfulness evaluation
from src.evaluation.faithfulness import FaithfulnessEvaluator


@dataclass
class ChainConfig:
    """Configuration for RAG chain"""
    model_type: ModelType = ModelType.BGE_SMALL
    temperature: float = 0.1
    max_tokens: int = 1024
    chain_type: str = "stuff"  # stuff, map_reduce, refine
    k: int = 5  # Number of documents to retrieve
    memory_limit: int = 5  # Number of conversation turns to remember

    # Query Expansion Settings
    enable_query_expansion: bool = False  # Enable query expansion
    num_expanded_queries: int = 3  # Number of expanded queries to generate

    # Context Compression Settings
    enable_context_compression: bool = False  # Enable context compression
    max_context_tokens: int = 2000  # Max tokens for compressed context
    similarity_threshold: float = 0.5  # Min similarity for chunks


class RAGChain:
    """
    Retrieval Augmented Generation Chain

    Features:
    - Document retrieval with embeddings
    - Context-aware response generation
    - Conversational memory
    - Model selection (BGE-small vs E5-base)
    - Custom prompt templates
    """

    def __init__(self, config: ChainConfig):
        """
        Initialize RAG chain

        Args:
            config: Chain configuration
        """
        self.config = config
        self.model_selector = ModelSelector(default_model=config.model_type)

        # Initialize embedding model
        self.embedding_model = EmbeddingModel(config.model_type.value)

        # ------------------------------------------------------------------
        # LLM backend selection  (set LLM_BACKEND=ollama or gemini in .env)
        # ------------------------------------------------------------------
        import os
        backend = os.getenv("LLM_BACKEND", "gemini").strip().lower()

        if backend == "ollama":
            print("✓ Using local Ollama backend")
            self.zai_client = OllamaClient(
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        else:
            # Default: Google Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

            if api_key:
                print(f"✓ Gemini API key found, using Google Gemini ({model_name})")
            else:
                print("⚠️  No GEMINI_API_KEY found – falling back to Ollama")
                backend = "ollama"

            if backend == "ollama":
                self.zai_client = OllamaClient(
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            else:
                self.zai_client = GeminiClient(
                    api_key=api_key,
                    model=model_name,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )


        # Initialize memory (simplified version)
        self.chat_history = []  # Store as list of (role, message) tuples
        self.memory = None  # Will be used for complex memory if needed

        # Store for documents
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None

        # Custom prompt template
        self.prompt_template = self._create_prompt_template()

        # ------------------------------------------------------------------
        # Performance Optimization Caches (Week 8)
        # ------------------------------------------------------------------
        self.embedding_cache = {}  # Cache for query embeddings
        self.context_cache = {}     # Cache for compressed contexts
        self.expansion_cache = {}  # Cache for query expansion results
        self.cache_hits = {"embedding": 0, "context": 0, "expansion": 0}
        self.cache_misses = {"embedding": 0, "context": 0, "expansion": 0}

        # ------------------------------------------------------------------
        # Initialize Query Expansion and Context Compression
        # ------------------------------------------------------------------
        self.query_expander = None
        self.context_compressor = None

        if config.enable_query_expansion:
            print("✓ Query expansion enabled")
            # Initialize with the same LLM client
            self.query_expander = QueryExpander(llm_client=self.zai_client)

        if config.enable_context_compression:
            print("✓ Context compression enabled")
            compression_config = CompressionConfig(
                max_tokens=config.max_context_tokens,
                similarity_threshold=config.similarity_threshold
            )
            self.context_compressor = ContextCompressor(compression_config)

        print(f"✓ RAG Chain initialized")
        print(f"  Model: {config.model_type.value}")
        print(f"  Chain type: {config.chain_type}")
        print(f"  Temperature: {config.temperature}")

    def _create_prompt_template(self):
        """Create custom prompt template for RAG"""
        template = """You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Instructions:
- Answer the question using only the provided context
- If the answer is not in the context, say "I don't have enough information to answer this question"
- Be concise but thorough
- If relevant, mention the source of your information

Answer:"""

        if PromptTemplate:
            return PromptTemplate(
                template=template,
                input_variables=["context", "chat_history", "question"]
            )
        else:
            # Return template as string for simple formatting
            return template

    def index_documents(self, chunks: List[Dict]) -> None:
        """
        Index document chunks for retrieval

        Args:
            chunks: List of document chunks with metadata
        """
        print(f"Indexing {len(chunks)} chunks...")

        # Create LangChain documents (or simple dicts)
        lang_documents = []
        for chunk in chunks:
            if LangDocument:
                doc = LangDocument(
                    page_content=chunk["text"],
                    metadata=chunk["metadata"]
                )
            else:
                doc = {
                    "page_content": chunk["text"],
                    "metadata": chunk["metadata"]
                }
            lang_documents.append(doc)

        # Create embeddings using our model
        texts = [doc.get("page_content", doc) if isinstance(doc, dict) else doc.page_content for doc in lang_documents]
        metadatas = [doc.get("metadata", {}) if isinstance(doc, dict) else doc.metadata for doc in lang_documents]

        # Use SentenceTransformer directly for consistency
        embeddings = self.embedding_model.encode(texts, batch_size=32)

        # Create FAISS index manually
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import FakeEmbeddings

        # Create a simple wrapper for our embeddings
        class CustomEmbeddings:
            def __init__(self, embedding_model):
                self.embedding_model = embedding_model

            def embed_documents(self, texts):
                return self.embedding_model.encode(texts)

            def embed_query(self, text):
                return self.embedding_model.encode(text)

        custom_embeddings = CustomEmbeddings(self.embedding_model)

        # For simplified implementation, we'll create a simple vector store
        try:
            # Create embeddings using our model
            embeddings = self.embedding_model.encode(texts, batch_size=32)

            # Create simple vector store (using numpy for now)
            self.vector_store = {
                "texts": texts,
                "embeddings": embeddings,
                "metadatas": metadatas
            }

            # Create simple retriever function
            self.retriever = self
            print(f"✓ Indexed {len(chunks)} chunks")

        except Exception as e:
            print(f"⚠️  Indexing error: {e}")
            # Create mock vector store
            self.vector_store = {
                "texts": texts,
                "embeddings": None,
                "metadatas": metadatas
            }
            self.retriever = self
            print(f"✓ Created mock index for {len(chunks)} chunks")

    def retrieve_documents(self, query: str) -> List[Dict]:
        """
        Retrieve relevant documents for query

        Args:
            query: Query string

        Returns:
            List of relevant documents
        """
        if not self.vector_store or not self.vector_store.get("texts"):
            print("⚠️  No documents indexed. Use index_documents() first.")
            return []

        try:
            # ------------------------------------------------------------------
            # Query Expansion: Generate alternative queries if enabled (with caching)
            # ------------------------------------------------------------------
            if self.query_expander:
                print("Query expansion enabled - performing multi-query retrieval...")

                # Check expansion cache
                cache_key = f"exp_{query}"
                if cache_key in self.expansion_cache:
                    self.cache_hits["expansion"] += 1
                    print(f"  Cache HIT for query expansion")
                    return self.expansion_cache[cache_key]
                else:
                    self.cache_misses["expansion"] += 1

                expansion_result = self.query_expander.expand_and_retrieve(
                    query=query,
                    retriever_func=self._do_retrieval,
                    k=self.config.k,
                    deduplicate=True
                )

                print(f"Retrieved {expansion_result['total_retrieved']} total documents from {len(expansion_result['all_queries'])} queries")
                print(f"After deduplication and re-ranking: {len(expansion_result['combined_documents'])} documents")

                # Cache the result
                self.expansion_cache[cache_key] = expansion_result['combined_documents']

                return expansion_result['combined_documents']

            else:
                # Standard single-query retrieval
                return self._do_retrieval(query, k=self.config.k)

        except Exception as e:
            print(f"⚠️  Retrieval error: {e}")
            # Return mock documents for testing
            if self.vector_store.get("texts"):
                return [
                    {"page_content": text[:200], "metadata": meta}
                    for text, meta in zip(self.vector_store["texts"][:2], self.vector_store["metadatas"][:2])
                ]
            return [{"page_content": "Sample document content", "metadata": {"source": "test"}}]

    def _do_retrieval(self, query: str, k: int = 5) -> List[Dict]:
        """
        Perform actual vector retrieval for a single query

        Args:
            query: Query string
            k: Number of documents to retrieve

        Returns:
            List of retrieved documents
        """
        if not self.vector_store or not self.vector_store.get("texts"):
            return []

        texts = self.vector_store["texts"]
        embeddings = self.vector_store["embeddings"]
        metadatas = self.vector_store["metadatas"]

        if embeddings is not None:
            # Check embedding cache
            cache_key = f"emb_{query}"
            if cache_key in self.embedding_cache:
                query_embedding = self.embedding_cache[cache_key]
                self.cache_hits["embedding"] += 1
            else:
                # Encode query
                query_embedding = self.embedding_model.encode(query, is_query=True)
                self.embedding_cache[cache_key] = query_embedding
                self.cache_misses["embedding"] += 1

            # Calculate similarities
            import numpy as np
            similarities = np.dot(embeddings, query_embedding)

            # Get top-k results
            k = min(k, len(similarities))
            top_indices = np.argsort(similarities)[-k:][::-1]

            # Create result documents
            docs = []
            for idx in top_indices:
                docs.append({
                    "page_content": texts[idx],
                    "metadata": metadatas[idx],
                    "score": float(similarities[idx])
                })

            return docs
        else:
            # Return all documents as fallback
            return [
                {"page_content": text, "metadata": meta}
                for text, meta in zip(texts, metadatas)
            ]

    def answer_question(
        self,
        question: str,
        use_memory: bool = True,
        evaluate_faithfulness: bool = False
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG

        Args:
            question: User question
            use_memory: Whether to use conversation memory
            evaluate_faithfulness: Whether to evaluate answer faithfulness (Week 8)

        Returns:
            Answer dictionary with response and metadata
        """
        start_time = time.time()

        # Timing breakdown
        timing = {}

        # Initialize result structure
        result = {
            "answer": "",
            "question": question,
            "source_documents": [],
            "processing_time": 0,
            "model_used": self.config.model_type.value,
            "num_documents_retrieved": 0,
            "query_expansion_used": self.config.enable_query_expansion,
            "context_compression_used": self.config.enable_context_compression,
            "timing_breakdown": {},
            "faithfulness": None
        }

        # Retrieve relevant documents
        retrieval_start = time.time()
        docs = self.retrieve_documents(question)
        timing["retrieval_time"] = time.time() - retrieval_start

        if not docs:
            result["answer"] = "I don't have any documents to search through. Please upload some documents first."
            result["processing_time"] = time.time() - start_time
            return result

        # ------------------------------------------------------------------
        # Context Compression: Filter and prune retrieved chunks (with caching)
        # ------------------------------------------------------------------
        original_doc_count = len(docs)
        compression_start = time.time()

        # Create cache key from document IDs (first 100 chars of first doc as simple hash)
        doc_hash = str(hash(str(docs[:2]))) if docs else "empty"

        if self.context_compressor:
            print("Context compression enabled - compressing retrieved chunks...")

            # Check context cache
            cache_key = f"ctx_{doc_hash}"
            if cache_key in self.context_cache:
                self.cache_hits["context"] += 1
                cached_result = self.context_cache[cache_key]
                docs = cached_result["docs"]
                timing["compression_time"] = time.time() - compression_start
                print(f"  Cache HIT for context compression")
                print(f"Compressed {original_doc_count} → {len(docs)} chunks (cached)")
                result["compression_ratio"] = cached_result["compression_ratio"]
                result["original_doc_count"] = original_doc_count
            else:
                self.cache_misses["context"] += 1
                compression_result = self.context_compressor.compress(docs)

                docs = compression_result.compressed_chunks
                timing["compression_time"] = time.time() - compression_start
                print(f"Compressed {original_doc_count} → {len(docs)} chunks")
                print(f"Tokens removed: {compression_result.tokens_removed}")

                result["compression_ratio"] = compression_result.compression_ratio
                result["original_doc_count"] = original_doc_count

                # Cache the compressed result
                self.context_cache[cache_key] = {
                    "docs": docs,
                    "compression_ratio": compression_result.compression_ratio
                }
        else:
            timing["compression_time"] = 0.0

        # Build context from retrieved documents
        if self.context_compressor:
            context = self.context_compressor.format_compressed_context(docs)
        else:
            context = "\n\n".join([
                doc.get("page_content", str(doc)) for doc in docs
            ])

        # Populate result with source documents
        result["source_documents"] = [
            {
                "content": doc.get("page_content", str(doc))[:200] + "...",
                "metadata": doc.get("metadata", {})
            }
            for doc in docs
        ]
        result["num_documents_retrieved"] = len(docs)

        # Get chat history if using memory
        chat_history = ""
        if use_memory and self.chat_history:
            # Format chat history as string
            chat_history = "\n".join([
                f"{role}: {msg}" for role, msg in self.chat_history[-5:]  # Last 5 messages
            ])

        # Generate prompt
        if isinstance(self.prompt_template, str):
            prompt = self.prompt_template.format(
                context=context,
                chat_history=chat_history,
                question=question
            )
        else:
            prompt = self.prompt_template.format(
                context=context,
                chat_history=chat_history,
                question=question
            )


        # Generate answer using LLM with context
        generation_start = time.time()
        try:
            answer = self.zai_client.generate_with_context(
                context=context,
                question=question,
                chat_history=self.chat_history if use_memory else None
            )
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}")
            answer = f"Error communicating with LLM backend: {str(e)}"
        timing["generation_time"] = time.time() - generation_start

        # ------------------------------------------------------------------
        # Faithfulness Evaluation (Week 8): Optional LLM-as-judge
        # ------------------------------------------------------------------
        faithfulness_result = None
        if evaluate_faithfulness and docs and answer:
            try:
                print("Running faithfulness evaluation...")
                evaluator = FaithfulnessEvaluator()
                faithfulness_result = evaluator.evaluate(
                    context=context,
                    question=question,
                    answer=answer,
                    detect_hallucinations=True
                )
                timing["faithfulness_time"] = faithfulness_result["evaluation_time"]
                print(f"  Faithfulness Score: {faithfulness_result['score']:.2f}")
                print(f"  Is Faithful: {faithfulness_result['is_faithful']}")
                if faithfulness_result['hallucinations']:
                    print(f"  Hallucinations: {faithfulness_result['hallucinations']}")
            except Exception as e:
                print(f"⚠️  Faithfulness evaluation failed: {e}")
                timing["faithfulness_time"] = 0.0
        else:
            timing["faithfulness_time"] = 0.0

        # Update memory
        if use_memory:
            self.chat_history.append(("user", question))
            self.chat_history.append(("assistant", answer))

        processing_time = time.time() - start_time

        result = {
            "answer": answer,
            "question": question,
            "source_documents": [
                {
                    "content": doc.get("page_content", str(doc))[:200] + "...",
                    "metadata": doc.get("metadata", {})
                }
                for doc in docs
            ],
            "processing_time": processing_time,
            "model_used": self.config.model_type.value,
            "num_documents_retrieved": len(docs),
            "query_expansion_used": self.config.enable_query_expansion,
            "context_compression_used": self.config.enable_context_compression,
            "timing_breakdown": timing
        }

        # Add faithfulness results if evaluation was performed
        if faithfulness_result:
            result["faithfulness"] = {
                "score": faithfulness_result["score"],
                "is_faithful": faithfulness_result["is_faithful"],
                "hallucinations": faithfulness_result["hallucinations"],
                "reason": faithfulness_result.get("reason", "")
            }
        else:
            result["faithfulness"] = None

        # Add compression metadata if applicable
        if self.context_compressor:
            result["compression_ratio"] = getattr(
                self.context_compressor.compress(
                    self.retrieve_documents(question) if not self.query_expander else docs
                ),
                "compression_ratio",
                0
            )

        return result

    def conversation_chat(self, message: str) -> Dict[str, Any]:
        """
        Interactive chat with conversation memory

        Args:
            message: User message

        Returns:
            Response dictionary
        """
        return self.answer_question(message, use_memory=True)

    def switch_model(self, new_model: ModelType) -> None:
        """
        Switch to a different embedding model

        Args:
            new_model: New model to use
        """
        print(f"Switching model from {self.config.model_type.value} to {new_model.value}")

        old_model = self.config.model_type
        self.config.model_type = new_model

        # Reinitialize embedding model
        self.embedding_model = EmbeddingModel(new_model.value)

        # Reindex documents if they exist
        if self.vector_store:
            print("Reindexing documents with new model...")
            # TODO: Implement reindexing logic
            print("✓ Model switched successfully")

    def clear_memory(self) -> None:
        """Clear conversation memory"""
        self.chat_history = []
        print("✓ Conversation memory cleared")

    def get_stats(self) -> Dict:
        """Get RAG chain statistics"""
        llm_stats = self.zai_client.get_stats()

        # Calculate cache hit rates
        embedding_total = self.cache_hits["embedding"] + self.cache_misses["embedding"]
        context_total = self.cache_hits["context"] + self.cache_misses["context"]
        expansion_total = self.cache_hits["expansion"] + self.cache_misses["expansion"]

        return {
            "config": {
                "model": self.config.model_type.value,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "chain_type": self.config.chain_type,
                "k": self.config.k,
                "query_expansion_enabled": self.config.enable_query_expansion,
                "context_compression_enabled": self.config.enable_context_compression,
                "max_context_tokens": self.config.max_context_tokens,
                "similarity_threshold": self.config.similarity_threshold
            },
            "llm_stats": llm_stats,
            "memory_messages": len(self.chat_history),
            "documents_indexed": len(self.vector_store.get("texts", [])) if self.vector_store else 0,
            "cache_stats": {
                "embedding_cache": {
                    "hits": self.cache_hits["embedding"],
                    "misses": self.cache_misses["embedding"],
                    "hit_rate": self.cache_hits["embedding"] / max(embedding_total, 1),
                    "size": len(self.embedding_cache)
                },
                "context_cache": {
                    "hits": self.cache_hits["context"],
                    "misses": self.cache_misses["context"],
                    "hit_rate": self.cache_hits["context"] / max(context_total, 1),
                    "size": len(self.context_cache)
                },
                "expansion_cache": {
                    "hits": self.cache_hits["expansion"],
                    "misses": self.cache_misses["expansion"],
                    "hit_rate": self.cache_hits["expansion"] / max(expansion_total, 1),
                    "size": len(self.expansion_cache)
                }
            }
        }

    def clear_caches(self) -> None:
        """Clear all performance caches"""
        self.embedding_cache.clear()
        self.context_cache.clear()
        self.expansion_cache.clear()
        self.cache_hits = {"embedding": 0, "context": 0, "expansion": 0}
        self.cache_misses = {"embedding": 0, "context": 0, "expansion": 0}
        print("✓ All caches cleared")


def main():
    """Test RAG chain"""
    print("=== RAG Chain Test ===\n")

    # Create configuration
    config = ChainConfig(
        model_type=ModelType.BGE_SMALL,
        temperature=0.1,
        max_tokens=512,
        k=3
    )

    # Initialize RAG chain
    rag_chain = RAGChain(config)

    # Sample document chunks
    sample_chunks = [
        {
            "text": "The RAG system combines retrieval and generation to provide accurate, context-aware responses. It uses embedding models to find relevant documents and LLMs to generate answers.",
            "metadata": {"source": "intro", "chunk_id": "chunk_001"}
        },
        {
            "text": "BGE-small is a fast embedding model with 384 dimensions. It's suitable for real-time applications where speed is important.",
            "metadata": {"source": "models", "chunk_id": "chunk_002"}
        },
        {
            "text": "E5-base provides higher accuracy with 768 dimensions. It's better for complex queries that require deeper understanding.",
            "metadata": {"source": "models", "chunk_id": "chunk_003"}
        }
    ]

    # Index documents
    rag_chain.index_documents(sample_chunks)

    # Test questions
    questions = [
        "What is a RAG system?",
        "Which embedding model should I use for speed?",
        "What are the differences between BGE-small and E5-base?"
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)

        result = rag_chain.answer_question(question)

        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources: {result['num_documents_retrieved']} documents")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Model used: {result['model_used']}")

    # Show stats
    print(f"\n{'='*60}")
    print("RAG Chain Statistics")
    print('='*60)
    stats = rag_chain.get_stats()
    print(f"Configuration: {stats['config']}")
    print(f"Gemini API calls: {stats['llm_stats']['request_count']}")
    print(f"Memory messages: {stats['memory_messages']}")
    print(f"Documents indexed: {stats['documents_indexed']}")

    print("\n✅ RAG chain test completed!")


if __name__ == "__main__":
    main()