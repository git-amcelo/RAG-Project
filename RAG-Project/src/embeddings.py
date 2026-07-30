"""
Embeddings Module for RAG System
Week 3: BGE-small and E5-base embedding models

Implements:
- BGE-small: 384 dimensions, fast
- E5-base: 768 dimensions, higher quality
"""

import os
import time
from typing import Dict, List, Union
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class EmbeddingModel:
    """
    Wrapper for sentence embedding models

    Supports:
    - BAAI/bge-small-en-v1.5 (384 dim, fast)
    - intfloat/e5-base-v2 (768 dim, higher quality)
    """

    def __init__(self,
                 model_name: str = "BAAI/bge-small-en-v1.5",
                 device: str = None,
                 cache_dir: str = "models/embeddings"):
        """
        Initialize embedding model

        Args:
            model_name: HuggingFace model name
            device: Device to run on (None for auto-detect)
            cache_dir: Directory to cache downloaded models
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # Detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Loading model: {model_name}")
        print(f"Device: {self.device}")

        # Load model
        self.model = SentenceTransformer(
            model_name,
            device=self.device,
            cache_folder=cache_dir
        )

        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Embedding dimension: {self.embedding_dim}")

        # Check if this is an E5 model (requires "query:" and "passage:" prefixes)
        self.is_e5 = "e5" in model_name.lower()

    def encode(self,
               text: Union[str, List[str]],
               is_query: bool = False,
               batch_size: int = 32,
               show_progress: bool = True) -> np.ndarray:
        """
        Encode text(s) into embeddings

        Args:
            text: Single text string or list of texts
            is_query: Whether this is a query (affects E5 prefix)
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar

        Returns:
            Embeddings as numpy array
        """
        # Add prefix for E5 models
        if self.is_e5:
            if isinstance(text, str):
                text = f"query: {text}" if is_query else f"passage: {text}"
            else:
                prefix = "query: " if is_query else "passage: "
                text = [prefix + t for t in text]

        # Encode
        embeddings = self.model.encode(
            text,
            batch_size=batch_size,
            show_progress_bar=show_progress and isinstance(text, list) and len(text) > 10,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalization for similarity search
        )

        return embeddings

    def encode_queries(self,
                      queries: Dict[str, str],
                      batch_size: int = 32) -> Dict[str, np.ndarray]:
        """
        Encode multiple queries

        Args:
            queries: Dictionary mapping query_id to query text
            batch_size: Batch size for encoding

        Returns:
            Dictionary mapping query_id to embedding
        """
        query_texts = list(queries.values())
        query_ids = list(queries.keys())

        embeddings = self.encode(query_texts, is_query=True, batch_size=batch_size)

        return {qid: emb for qid, emb in zip(query_ids, embeddings)}

    def encode_passages(self,
                       passages: Dict[str, str],
                       batch_size: int = 32) -> Dict[str, np.ndarray]:
        """
        Encode multiple passages

        Args:
            passages: Dictionary mapping passage_id to passage text
            batch_size: Batch size for encoding

        Returns:
            Dictionary mapping passage_id to embedding
        """
        passage_texts = list(passages.values())
        passage_ids = list(passages.keys())

        embeddings = self.encode(passage_texts, is_query=False, batch_size=batch_size)

        return {pid: emb for pid, emb in zip(passage_ids, embeddings)}

    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings

        Since embeddings are L2-normalized, cosine similarity = dot product

        Args:
            emb1: First embedding
            emb2: Second embedding

        Returns:
            Cosine similarity score (0 to 1)
        """
        return float(np.dot(emb1, emb2))

    def save_embeddings(self,
                       embeddings: Dict[str, np.ndarray],
                       file_path: str) -> None:
        """
        Save embeddings to disk

        Args:
            embeddings: Dictionary mapping id to embedding
            file_path: Path to save embeddings
        """
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)

        ids = list(embeddings.keys())
        vectors = np.array([embeddings[id] for id in ids])

        np.savez(file_path, ids=ids, vectors=vectors)
        print(f"Saved {len(ids)} embeddings to {file_path}")

    def load_embeddings(self, file_path: str) -> Dict[str, np.ndarray]:
        """
        Load embeddings from disk

        Args:
            file_path: Path to load embeddings from

        Returns:
            Dictionary mapping id to embedding
        """
        data = np.load(file_path, allow_pickle=True)
        ids = data['ids']
        vectors = data['vectors']

        return {id: vectors[i] for i, id in enumerate(ids)}


class BM25SparseEmbedding:
    """
    BM25 sparse retrieval model
    Used in Week 4 for hybrid retrieval with dense embeddings
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 model

        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b
        self.doc_freqs = {}  # Document term frequencies
        self.idf = {}  # Inverse document frequency
        self.doc_lens = {}  # Document lengths
        self.avgdl = 0  # Average document length

    def tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        text = text.lower()
        return text.split()

    def index_passages(self, passages: Dict[str, str]) -> None:
        """
        Build BM25 index from passages

        Args:
            passages: Dictionary mapping passage_id to passage text
        """
        print("Building BM25 index...")

        for pid, text in tqdm(passages.items(), desc="Tokenizing"):
            tokens = self.tokenize(text)
            self.doc_lens[pid] = len(tokens)

            term_counts = {}
            for token in tokens:
                term_counts[token] = term_counts.get(token, 0) + 1
            self.doc_freqs[pid] = term_counts

        # Calculate average document length
        self.avgdl = sum(self.doc_lens.values()) / len(self.doc_lens)

        # Calculate IDF
        N = len(passages)
        vocab = set()
        for term_counts in self.doc_freqs.values():
            vocab.update(term_counts.keys())

        for term in vocab:
            df = sum(1 for term_counts in self.doc_freqs.values() if term in term_counts)
            self.idf[term] = np.log1p((N - df + 0.5) / (df + 0.5))

        print(f"BM25 index built with {len(vocab)} unique terms")

    def score(self, query: str, passage_id: str) -> float:
        """
        Compute BM25 score for query-passage pair

        Args:
            query: Query text
            passage_id: Passage ID

        Returns:
            BM25 score
        """
        query_tokens = self.tokenize(query)
        doc_terms = self.doc_freqs.get(passage_id, {})
        doc_len = self.doc_lens.get(passage_id, 0)

        score = 0
        for token in query_tokens:
            if token in doc_terms:
                tf = doc_terms[token]
                idf = self.idf.get(token, 0)

                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                score += idf * numerator / denominator

        return score

    def retrieve(self, query: str, passages: Dict[str, str], k: int = 10) -> List[tuple]:
        """
        Retrieve top-k passages for query

        Args:
            query: Query text
            passages: All passages
            k: Number of results

        Returns:
            List of (passage_id, score) tuples
        """
        scores = []
        for pid in passages.keys():
            score = self.score(query, pid)
            scores.append((pid, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]


def compare_models(queries: Dict[str, str],
                   passages: Dict[str, str]) -> Dict:
    """
    Compare BGE-small and E5-base models

    Args:
        queries: Sample queries
        passages: Sample passages

    Returns:
        Comparison results
    """
    print("\n=== Comparing Embedding Models ===\n")

    models = {
        "BGE-small": "BAAI/bge-small-en-v1.5",
        "E5-base": "intfloat/e5-base-v2"
    }

    results = {}

    for name, model_path in models.items():
        print(f"\nTesting {name}...")

        model = EmbeddingModel(model_path)

        sample_query = list(queries.values())[0]
        sample_passage = list(passages.values())[0]

        # Test encoding speed
        start = time.time()
        query_emb = model.encode(sample_query, is_query=True)
        passage_emb = model.encode(sample_passage, is_query=False)
        encode_time = time.time() - start

        # Compute similarity
        similarity = model.compute_similarity(query_emb, passage_emb)

        results[name] = {
            "dimension": model.embedding_dim,
            "encode_time": encode_time,
            "similarity": similarity
        }

        print(f"  Dimension: {model.embedding_dim}")
        print(f"  Encode time: {encode_time:.4f}s")
        print(f"  Query-Passage similarity: {similarity:.4f}")

    return results


def main():
    """Test the embeddings module"""
    print("=== Embeddings Module Test ===\n")

    # Sample data
    queries = {
        "q1": "What causes headaches?",
        "q2": "How do vaccines work?"
    }
    passages = {
        "p1": "Headaches can be caused by stress, dehydration, and lack of sleep.",
        "p2": "Vaccines stimulate the immune system to fight pathogens.",
        "p3": "Climate change is caused by human activities."
    }

    # Test BGE-small
    print("\n--- Testing BGE-small ---")
    bge_model = EmbeddingModel("BAAI/bge-small-en-v1.5")

    query_emb = bge_model.encode("What causes headaches?", is_query=True)
    print(f"Query embedding shape: {query_emb.shape}")

    passage_embs = bge_model.encode_passages(passages)
    print(f"Encoded {len(passage_embs)} passages")

    # Test similarity
    for pid, emb in passage_embs.items():
        sim = bge_model.compute_similarity(query_emb, emb)
        print(f"  Similarity to {pid}: {sim:.4f}")

    print("\n✅ Embeddings module test completed!")


if __name__ == "__main__":
    main()
