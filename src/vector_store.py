"""
Vector Store Module using FAISS
Week 3: Fast similarity search with FAISS indices

Implements:
- Flat index: Exact search, baseline
- IVF index: Fast approximate search
- HNSW index: Very fast graph-based search
"""

import os
import time
import pickle
from typing import Dict, List, Tuple, Union
import numpy as np
import faiss


class VectorStore:
    """
    FAISS-based vector store for similarity search

    Supports multiple index types:
    - Flat: Exact L2 search (baseline)
    - IVF: Inverted File Index (faster)
    - HNSW: Hierarchical Navigable Small World (very fast)
    """

    def __init__(self, embedding_dim: int, index_type: str = "flat"):
        """
        Initialize vector store

        Args:
            embedding_dim: Dimension of embeddings
            index_type: Type of FAISS index ("flat", "ivf", "hnsw")
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.index = None
        self.passage_ids = []  # Map index position to passage ID

        # IVF-specific parameters
        self.nlist = 100  # Number of clusters for IVF

        # HNSW-specific parameters
        self.M = 32  # HNSW connection parameter

    def create_index(self, index_type: str = None) -> faiss.Index:
        """
        Create a FAISS index

        Args:
            index_type: Type of index to create

        Returns:
            FAISS index object
        """
        if index_type is None:
            index_type = self.index_type

        self.index_type = index_type
        print(f"Creating {index_type.upper()} index (dim={self.embedding_dim})")

        if index_type == "flat":
            # Exact search using L2 distance
            self.index = faiss.IndexFlatL2(self.embedding_dim)

        elif index_type == "ivf":
            # Inverted File Index for faster search
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.nlist)
            print(f"  IVF with nlist={self.nlist}")

        elif index_type == "hnsw":
            # Hierarchical Navigable Small World graph
            self.index = faiss.IndexHNSWFlat(self.embedding_dim, self.M)
            print(f"  HNSW with M={self.M}")

        else:
            raise ValueError(f"Unknown index type: {index_type}")

        return self.index

    def add_embeddings(self,
                       embeddings: Union[np.ndarray, List[np.ndarray]],
                       passage_ids: List[str] = None,
                       train: bool = True) -> None:
        """
        Add embeddings to the index

        Args:
            embeddings: Embeddings to add
            passage_ids: Optional list of passage IDs
            train: Whether to train IVF index before adding
        """
        # Convert to numpy array
        if isinstance(embeddings, list):
            embeddings = np.array(embeddings)
        elif not isinstance(embeddings, np.ndarray):
            raise TypeError("embeddings must be numpy array or list")

        # Ensure 2D array
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        n_embeddings = embeddings.shape[0]

        # Check dimensions
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dim mismatch: expected {self.embedding_dim}, got {embeddings.shape[1]}")

        # Store passage IDs
        if passage_ids is not None:
            if len(passage_ids) != n_embeddings:
                raise ValueError(f"Number of IDs ({len(passage_ids)}) doesn't match embeddings ({n_embeddings})")
            self.passage_ids.extend(passage_ids)
        else:
            # Generate default IDs
            self.passage_ids.extend([f"doc_{len(self.passage_ids) + i}" for i in range(n_embeddings)])

        # Create index if not exists
        if self.index is None:
            self.create_index()

        # Train IVF index if needed
        if self.index_type == "ivf" and train and not self.index.is_trained:
            print(f"Training IVF index on {n_embeddings} vectors...")
            self.index.train(embeddings)
            print("Training complete.")

        # Add embeddings
        print(f"Adding {n_embeddings} embeddings to index...")
        start = time.time()
        self.index.add(embeddings)
        add_time = time.time() - start
        print(f"Added in {add_time:.2f}s")

        print(f"Index now contains {self.index.ntotal} vectors")

    def search(self,
               query_embedding: Union[np.ndarray, List[np.ndarray]],
               k: int = 10) -> Tuple[List[List[int]], List[List[float]]]:
        """
        Search for similar embeddings

        Args:
            query_embedding: Query embedding(s)
            k: Number of results to return

        Returns:
            Tuple of (indices, distances)
        """
        if self.index is None:
            raise ValueError("Index is empty. Add embeddings first.")

        # Convert to numpy array
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding)

        # Ensure 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Search
        distances, indices = self.index.search(query_embedding, k)

        return indices.tolist(), distances.tolist()

    def search_by_id(self, query_embedding: np.ndarray, k: int = 10) -> List[Dict]:
        """
        Search and return results with passage IDs

        Args:
            query_embedding: Query embedding
            k: Number of results

        Returns:
            List of results with passage_id, rank, score
        """
        indices, distances = self.search(query_embedding, k)

        results = []
        for rank, (idx, dist) in enumerate(zip(indices[0], distances[0])):
            if idx < len(self.passage_ids) and idx >= 0:
                results.append({
                    "passage_id": self.passage_ids[idx],
                    "rank": rank + 1,
                    "distance": float(dist),
                    "score": 1.0 / (1.0 + float(dist))  # Convert distance to similarity
                })

        return results

    def save(self, file_path: str) -> None:
        """
        Save index to disk

        Args:
            file_path: Path to save index (without extension)
        """
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, f"{file_path}.index")

        # Save metadata
        metadata = {
            "embedding_dim": self.embedding_dim,
            "index_type": self.index_type,
            "passage_ids": self.passage_ids,
            "nlist": self.nlist if self.index_type == "ivf" else None,
            "M": self.M if self.index_type == "hnsw" else None
        }

        with open(f"{file_path}.metadata", "wb") as f:
            pickle.dump(metadata, f)

        print(f"Saved index to {file_path}.index")

    def load(self, file_path: str) -> None:
        """
        Load index from disk

        Args:
            file_path: Path to load index from
        """
        # Load FAISS index
        self.index = faiss.read_index(f"{file_path}.index")

        # Load metadata
        with open(f"{file_path}.metadata", "rb") as f:
            metadata = pickle.load(f)

        self.embedding_dim = metadata["embedding_dim"]
        self.index_type = metadata["index_type"]
        self.passage_ids = metadata["passage_ids"]
        self.nlist = metadata.get("nlist", 100)
        self.M = metadata.get("M", 32)

        print(f"Loaded {self.index_type.upper()} index with {self.index.ntotal} vectors")

    def get_index_info(self) -> Dict:
        """
        Get information about the index

        Returns:
            Dictionary with index information
        """
        info = {
            "type": self.index_type,
            "dimension": self.embedding_dim,
            "total_vectors": self.index.ntotal if self.index else 0,
            "is_trained": self.index.is_trained if hasattr(self.index, 'is_trained') else True,
            "passage_ids_count": len(self.passage_ids)
        }

        if self.index_type == "ivf":
            info["nlist"] = self.nlist
        elif self.index_type == "hnsw":
            info["M"] = self.M

        return info


def compare_index_types(embeddings: np.ndarray,
                       query_embedding: np.ndarray) -> Dict:
    """
    Compare different FAISS index types

    Args:
        embeddings: Embeddings to index
        query_embedding: Query to test

    Returns:
        Comparison results
    """
    print("\n=== Comparing FAISS Index Types ===\n")

    embedding_dim = embeddings.shape[1]
    index_types = ["flat", "ivf", "hnsw"]
    results = {}

    for idx_type in index_types:
        print(f"\nTesting {idx_type.upper()} index...")

        store = VectorStore(embedding_dim, idx_type)
        store.create_index()
        store.add_embeddings(embeddings, train=True)

        # Measure search time
        start = time.time()
        indices, distances = store.search(query_embedding, k=10)
        search_time = time.time() - start

        results[idx_type] = {
            "search_time": search_time,
            "total_vectors": store.index.ntotal,
            "results": indices[0][:5]
        }

        print(f"  Search time: {search_time*1000:.2f}ms")

    return results


def main():
    """Test the vector store module"""
    print("=== Vector Store Module Test ===\n")

    # Create sample embeddings
    np.random.seed(42)
    n_passages = 100
    embedding_dim = 384  # BGE-small dimension

    embeddings = np.random.random((n_passages, embedding_dim)).astype('float32')
    passage_ids = [f"passage_{i}" for i in range(n_passages)]

    # Create query
    query_embedding = np.random.random(embedding_dim).astype('float32')

    # Test Flat index
    print("\n--- Testing Flat Index ---")
    store = VectorStore(embedding_dim, "flat")
    store.create_index()
    store.add_embeddings(embeddings, passage_ids)

    results = store.search_by_id(query_embedding, k=5)
    print("Top 5 results:")
    for r in results[:3]:
        print(f"  {r['passage_id']}: score={r['score']:.4f}")

    print("\n✅ Vector store module test completed!")


if __name__ == "__main__":
    main()
