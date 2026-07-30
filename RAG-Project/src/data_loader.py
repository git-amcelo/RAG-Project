"""
Data Loader Module for MS MARCO Dataset
Week 3: Extract and prepare data for dense retrieval

Handles:
- Loading MS MARCO v2.1 dataset
- Extracting queries and passages
- Creating relevance judgments (qrels)
- Preprocessing text
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional
from datasets import load_dataset
from tqdm import tqdm


class MSMarcoDataLoader:
    """
    Load and preprocess MS MARCO dataset for RAG system

    Usage:
        loader = MSMarcoDataLoader()
        loader.extract_from_v21(max_queries=1000)
        loader.load_processed_data()
    """

    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
        """
        Initialize the data loader

        Args:
            raw_dir: Directory for raw downloaded data
            processed_dir: Directory for processed data
        """
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir

        # Create directories
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)

        # Data containers
        self.queries: Dict[str, str] = {}
        self.passages: Dict[str, str] = {}
        self.qrels: Dict[str, List[str]] = {}  # Query relevance judgments

    def extract_from_v21(self,
                        split: str = "validation",
                        max_queries: int = 1000,
                        max_passages_per_query: int = 10) -> None:
        """
        Extract queries and passages from MS MARCO v2.1 dataset

        Args:
            split: Dataset split ('validation', 'train', or 'test')
            max_queries: Maximum queries to extract
            max_passages_per_query: Maximum passages per query
        """
        print(f"Extracting data from MS MARCO v2.1 {split} set...")
        print(f"Max queries: {max_queries}")
        print(f"Max passages per query: {max_passages_per_query}")

        # Load dataset from HuggingFace
        dataset = load_dataset("microsoft/ms_marco", "v2.1", split=split)

        # Limit queries if specified
        if max_queries:
            dataset = dataset.select(range(min(max_queries, len(dataset))))

        # Extract data
        self.queries = {}
        self.qrels = {}
        self.passages = {}

        for item in tqdm(dataset, desc="Extracting"):
            query_id = str(item.get('query_id', len(self.queries)))
            query = item.get('query', '')

            if not query:
                continue

            # Store query
            self.queries[query_id] = query

            # Extract passages
            passage_data = item.get('passages', {})
            passage_texts = passage_data.get('passage_text', [])
            is_selected = passage_data.get('is_selected', [])

            relevant_passages = []

            for i, text in enumerate(passage_texts[:max_passages_per_query]):
                if text and text.strip():
                    pid = f"{query_id}_p{i}"
                    self.passages[pid] = text.strip()

                    # Track relevant passages (where is_selected == 1)
                    if i < len(is_selected) and is_selected[i] == 1:
                        relevant_passages.append(pid)

            # Store qrels if there are relevant passages
            if relevant_passages:
                self.qrels[query_id] = relevant_passages

        # Print summary
        print(f"\n{'='*50}")
        print(f"Data Extraction Summary")
        print(f"{'='*50}")
        print(f"Queries:   {len(self.queries)}")
        print(f"Passages:  {len(self.passages)}")
        print(f"Qrels:     {len(self.qrels)} queries with relevance")
        print(f"{'='*50}\n")

        # Save processed data
        self.save_processed_data()

    def save_processed_data(self) -> None:
        """Save all processed data to disk"""
        print(f"Saving processed data to {self.processed_dir}...")

        # Save queries
        queries_path = os.path.join(self.processed_dir, "queries.json")
        with open(queries_path, 'w') as f:
            json.dump(self.queries, f, indent=2)

        # Save passages
        passages_path = os.path.join(self.processed_dir, "passages.json")
        with open(passages_path, 'w') as f:
            json.dump(self.passages, f, indent=2)

        # Save qrels
        qrels_path = os.path.join(self.processed_dir, "qrels.json")
        with open(qrels_path, 'w') as f:
            json.dump(self.qrels, f, indent=2)

        print("Saved all processed data!")

    def load_processed_data(self) -> None:
        """Load all processed data from disk"""
        print(f"Loading processed data from {self.processed_dir}...")

        # Load queries
        queries_path = os.path.join(self.processed_dir, "queries.json")
        if os.path.exists(queries_path):
            with open(queries_path, 'r') as f:
                self.queries = json.load(f)
            print(f"Loaded {len(self.queries)} queries")

        # Load passages
        passages_path = os.path.join(self.processed_dir, "passages.json")
        if os.path.exists(passages_path):
            with open(passages_path, 'r') as f:
                self.passages = json.load(f)
            print(f"Loaded {len(self.passages)} passages")

        # Load qrels
        qrels_path = os.path.join(self.processed_dir, "qrels.json")
        if os.path.exists(qrels_path):
            with open(qrels_path, 'r') as f:
                self.qrels = json.load(f)
            print(f"Loaded qrels for {len(self.qrels)} queries")

    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,;:!?-]', ' ', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def preprocess_all_passages(self) -> None:
        """Preprocess all passages"""
        print("Preprocessing passages...")
        processed = {}
        for pid, text in tqdm(self.passages.items(), desc="Preprocessing"):
            processed[pid] = self.preprocess_text(text)
        self.passages = processed
        print("Preprocessing complete!")

    def create_splits(self,
                     train_ratio: float = 0.7,
                     val_ratio: float = 0.15,
                     test_ratio: float = 0.15,
                     random_seed: int = 42) -> Tuple[Dict, Dict, Dict]:
        """
        Split queries into train, validation, and test sets

        Args:
            train_ratio: Proportion for training
            val_ratio: Proportion for validation
            test_ratio: Proportion for testing
            random_seed: Random seed

        Returns:
            Tuple of (train_queries, val_queries, test_queries)
        """
        import random

        query_ids = list(self.queries.keys())
        random.seed(random_seed)
        random.shuffle(query_ids)

        n = len(query_ids)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_ids = query_ids[:train_end]
        val_ids = query_ids[train_end:val_end]
        test_ids = query_ids[val_end:]

        train_queries = {qid: self.queries[qid] for qid in train_ids}
        val_queries = {qid: self.queries[qid] for qid in val_ids}
        test_queries = {qid: self.queries[qid] for qid in test_ids}

        print(f"\nData splits:")
        print(f"  Train:   {len(train_queries)} queries")
        print(f"  Val:     {len(val_queries)} queries")
        print(f"  Test:    {len(test_queries)} queries")

        return train_queries, val_queries, test_queries

    def get_statistics(self) -> Dict:
        """
        Get statistics about the loaded data

        Returns:
            Dictionary with statistics
        """
        passage_lengths = [len(p.split()) for p in self.passages.values()]
        query_lengths = [len(q.split()) for q in self.queries.values()]

        qrels_counts = [len(v) for v in self.qrels.values()]

        return {
            "num_queries": len(self.queries),
            "num_passages": len(self.passages),
            "num_qrels": len(self.qrels),
            "avg_passage_length": sum(passage_lengths) / len(passage_lengths) if passage_lengths else 0,
            "avg_query_length": sum(query_lengths) / len(query_lengths) if query_lengths else 0,
            "avg_qrels_count": sum(qrels_counts) / len(qrels_counts) if qrels_counts else 0
        }


def main():
    """Test the data loader"""
    print("=== MS MARCO Data Loader Test ===\n")

    # Initialize
    loader = MSMarcoDataLoader()

    # Try to load existing data
    try:
        loader.load_processed_data()
        stats = loader.get_statistics()
        print(f"\nStatistics:")
        for key, value in stats.items():
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
    except FileNotFoundError:
        print("No processed data found. Run extract_data.py first!")


if __name__ == "__main__":
    main()
