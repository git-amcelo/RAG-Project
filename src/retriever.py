"""
Retriever Module - End-to-end retrieval pipeline
Week 3: Combines embedding models and vector stores

Implements:
- DenseRetriever: Dense vector-based retrieval
- Evaluation and benchmarking utilities
"""

import time
from typing import Dict, List, Optional
import numpy as np

from src.embeddings import EmbeddingModel, BM25SparseEmbedding
from src.vector_store import VectorStore


class DenseRetriever:
    """
    Dense retrieval system using embeddings and FAISS

    This is the main retrieval component for Week 3.

    Usage:
        retriever = DenseRetriever("BAAI/bge-small-en-v1.5")
        retriever.index_passages(passages)
        results = retriever.retrieve("What causes headaches?", k=5)
    """

    def __init__(self,
                 embedding_model: str = "BAAI/bge-small-en-v1.5",
                 index_type: str = "flat",
                 device: str = None):
        """
        Initialize dense retriever

        Args:
            embedding_model: Model name or path
            index_type: FAISS index type ("flat", "ivf", "hnsw")
            device: Device to run on
        """
        print(f"Initializing DenseRetriever with {embedding_model}...")

        # Initialize embedding model
        self.model = EmbeddingModel(embedding_model, device=device)

        # Initialize vector store
        self.vector_store = VectorStore(self.model.embedding_dim, index_type)
        self.vector_store.create_index()

        # Store passages
        self.passages: Dict[str, str] = {}

    def index_passages(self,
                      passages: Dict[str, str],
                      batch_size: int = 32,
                      save_embeddings: bool = False) -> None:
        """
        Encode and index passages

        Args:
            passages: Dictionary mapping passage_id to passage text
            batch_size: Batch size for encoding
            save_embeddings: Whether to save embeddings to disk
        """
        print(f"Indexing {len(passages)} passages...")

        self.passages = passages

        # Encode passages
        print("Encoding passages with", self.model.model_name)
        start = time.time()
        passage_embs = self.model.encode_passages(passages, batch_size=batch_size)
        encode_time = time.time() - start
        print(f"Encoded {len(passage_embs)} passages in {encode_time:.2f}s")

        # Prepare embeddings for FAISS
        passage_ids = list(passage_embs.keys())
        embeddings = np.array([passage_embs[pid] for pid in passage_ids])

        # Add to vector store
        self.vector_store.add_embeddings(embeddings, passage_ids, train=True)

    def retrieve(self,
                query: str,
                k: int = 10,
                return_text: bool = True) -> List[Dict]:
        """
        Retrieve top-k passages for a query

        Args:
            query: Query text
            k: Number of passages to retrieve
            return_text: Whether to include passage text

        Returns:
            List of retrieval results
        """
        # Encode query
        query_emb = self.model.encode(query, is_query=True)

        # Search
        results = self.vector_store.search_by_id(query_emb, k)

        # Add passage text if requested
        if return_text and self.passages:
            for r in results:
                passage_id = r["passage_id"]
                if passage_id in self.passages:
                    r["text"] = self.passages[passage_id]

        return results

    def batch_retrieve(self,
                      queries: Dict[str, str],
                      k: int = 10) -> Dict[str, List[Dict]]:
        """
        Retrieve for multiple queries

        Args:
            queries: Dictionary mapping query_id to query text
            k: Number of passages per query

        Returns:
            Dictionary mapping query_id to results
        """
        results = {}

        for qid, query in queries.items():
            results[qid] = self.retrieve(query, k)

        return results

    def save_index(self, file_path: str) -> None:
        """Save the vector store index"""
        self.vector_store.save(file_path)

    def load_index(self, file_path: str) -> None:
        """Load a saved vector store index"""
        self.vector_store.load(file_path)

    def get_info(self) -> Dict:
        """Get information about the retriever"""
        return {
            "model": self.model.model_name,
            "embedding_dim": self.model.embedding_dim,
            "index_type": self.vector_store.index_type,
            "total_passages": len(self.passages),
            "indexed_vectors": self.vector_store.index.ntotal if self.vector_store.index else 0
        }


class HybridRetriever:
    """
    Hybrid retrieval combining dense and sparse methods
    This will be used in Week 4

    Combines:
    - Dense retrieval (embeddings + FAISS)
    - Sparse retrieval (BM25)
    """

    def __init__(self,
                 dense_retriever: DenseRetriever,
                 alpha: float = 0.5):
        """
        Initialize hybrid retriever

        Args:
            dense_retriever: Dense retriever
            alpha: Weight for dense score (1-alpha for sparse)
        """
        self.dense_retriever = dense_retriever
        self.alpha = alpha
        self.bm25 = BM25SparseEmbedding()
        self.passages = {}

    def index_passages(self, passages: Dict[str, str], batch_size: int = 32) -> None:
        """Index passages for both dense and sparse retrieval"""
        self.passages = passages

        # Index with dense retriever
        self.dense_retriever.index_passages(passages, batch_size)

        # Index with BM25
        self.bm25.index_passages(passages)

    def retrieve(self, query: str, k: int = 10) -> List[Dict]:
        """Retrieve using hybrid scoring"""
        # Get dense results
        dense_results = self.dense_retriever.retrieve(query, k=k*2, return_text=False)

        # Get sparse results
        sparse_results = self.bm25.retrieve(query, self.passages, k=k*2)

        # Combine scores
        combined_scores = {}

        # Normalize and combine dense scores
        max_dense = max(r["score"] for r in dense_results) if dense_results else 1
        for r in dense_results:
            pid = r["passage_id"]
            normalized = r["score"] / max_dense
            combined_scores[pid] = self.alpha * normalized

        # Normalize and combine sparse scores
        max_sparse = max(score for _, score in sparse_results) if sparse_results else 1
        for pid, score in sparse_results:
            normalized = score / max_sparse
            if pid in combined_scores:
                combined_scores[pid] += (1 - self.alpha) * normalized
            else:
                combined_scores[pid] = (1 - self.alpha) * normalized

        # Sort and return top-k
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]

        # Format results
        results = []
        for rank, (pid, score) in enumerate(sorted_results):
            result = {
                "passage_id": pid,
                "rank": rank + 1,
                "score": score
            }
            if pid in self.passages:
                result["text"] = self.passages[pid]
            results.append(result)

        return results


def benchmark_retrieval(retriever: DenseRetriever,
                        queries: Dict[str, str],
                        qrels: Dict[str, List[str]],
                        k_values: List[int] = [1, 5, 10]) -> Dict:
    """
    Benchmark retrieval performance

    Args:
        retriever: DenseRetriever instance
        queries: Queries to test
        qrels: Relevant passages for each query
        k_values: K values for Recall@K

    Returns:
        Benchmark results
    """
    from src.evaluation import recall_at_k, mrr

    print("\n=== Benchmarking Retrieval ===\n")

    results = {
        "queries_tested": len(queries),
        "avg_retrieval_time": 0,
        "metrics": {}
    }

    total_time = 0
    all_rr = []  # Reciprocal ranks for MRR

    for k in k_values:
        recalls = []

        for qid, query in queries.items():
            # Measure retrieval time
            start = time.time()
            retrieved = retriever.retrieve(query, k=k)
            elapsed = time.time() - start
            total_time += elapsed

            # Get retrieved IDs
            retrieved_ids = [r["passage_id"] for r in retrieved]

            # Get relevant IDs
            relevant_ids = qrels.get(qid, [])

            if relevant_ids:
                # Calculate recall
                recall = recall_at_k(retrieved_ids, relevant_ids, k)
                recalls.append(recall)

                # Get reciprocal rank
                rr = mrr(retrieved_ids, relevant_ids)
                all_rr.append(rr)

        avg_recall = np.mean(recalls) if recalls else 0
        results["metrics"][f"recall@{k}"] = avg_recall

    results["avg_retrieval_time"] = total_time / len(queries) if queries else 0
    results["metrics"]["mrr"] = np.mean(all_rr) if all_rr else 0

    # Print results
    print(f"Tested {results['queries_tested']} queries")
    print(f"Average retrieval time: {results['avg_retrieval_time']*1000:.2f}ms")
    print("\nMetrics:")
    for metric, value in results["metrics"].items():
        print(f"  {metric}: {value:.4f}")

    return results


def main():
    """Test the retriever module"""
    print("=== Retriever Module Test ===\n")

    # Sample data
    passages = {
        "p1": "Headaches can be caused by stress, dehydration, and lack of sleep.",
        "p2": "Vaccines stimulate the immune system to fight pathogens.",
        "p3": "Climate change is caused by human activities like burning fossil fuels.",
        "p4": "Photosynthesis converts light energy into chemical energy in plants.",
        "p5": "Diabetes affects how the body processes blood sugar."
    }

    queries = {
        "q1": "What causes headaches?",
        "q2": "How do vaccines work?"
    }

    qrels = {
        "q1": ["p1"],
        "q2": ["p2"]
    }

    # Test dense retriever
    print("\n--- Testing Dense Retriever ---")
    retriever = DenseRetriever("BAAI/bge-small-en-v1.5", index_type="flat")
    retriever.index_passages(passages, save_embeddings=False)

    results = retriever.retrieve("What causes headaches?", k=3)
    print("Top 3 results for 'What causes headaches?':")
    for r in results:
        print(f"  {r['passage_id']}: {r['score']:.4f}")
        print(f"    Text: {r['text'][:60]}...")

    # Print retriever info
    print("\nRetriever Info:")
    info = retriever.get_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n✅ Retriever module test completed!")


if __name__ == "__main__":
    main()
