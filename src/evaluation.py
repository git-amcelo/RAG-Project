"""
Evaluation Module for RAG Retrieval
Week 3: Metrics for measuring retrieval quality

Implements:
- Recall@K: Percentage of relevant docs found in top K
- MRR: Mean Reciprocal Rank
- Precision@K: Precision at cut-off K
- NDCG@K: Normalized Discounted Cumulative Gain
"""

import time
from typing import Dict, List
import numpy as np


def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """
    Calculate Recall@K

    Recall@K = |relevant documents in top K| / |total relevant documents|

    Args:
        retrieved_ids: List of retrieved document IDs (ordered by rank)
        relevant_ids: List of relevant document IDs
        k: Cut-off rank

    Returns:
        Recall@K score (0 to 1)
    """
    if not relevant_ids:
        return 0.0

    retrieved_at_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)

    recalled = len(retrieved_at_k & relevant_set)
    return recalled / len(relevant_set)


def precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """
    Calculate Precision@K

    Precision@K = |relevant documents in top K| / K

    Args:
        retrieved_ids: List of retrieved document IDs (ordered by rank)
        relevant_ids: List of relevant document IDs
        k: Cut-off rank

    Returns:
        Precision@K score (0 to 1)
    """
    if k == 0:
        return 0.0

    retrieved_at_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)

    relevant_retrieved = len(retrieved_at_k & relevant_set)
    return relevant_retrieved / k


def average_precision(retrieved_ids: List[str],
                     relevant_ids: List[str],
                     k: int = None) -> float:
    """
    Calculate Average Precision (AP)

    AP = mean of precision scores at ranks where relevant docs are found

    Args:
        retrieved_ids: List of retrieved document IDs (ordered by rank)
        relevant_ids: List of relevant document IDs
        k: Maximum rank to consider (None for all)

    Returns:
        Average Precision score (0 to 1)
    """
    if not relevant_ids:
        return 0.0

    relevant_set = set(relevant_ids)
    precisions = []

    max_rank = k if k else len(retrieved_ids)

    for i in range(max_rank):
        if retrieved_ids[i] in relevant_set:
            precisions.append(precision_at_k(retrieved_ids, relevant_ids, i + 1))

    return np.mean(precisions) if precisions else 0.0


def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR)

    MRR = 1 / rank of first relevant document

    Args:
        retrieved_ids: List of retrieved document IDs (ordered by rank)
        relevant_ids: List of relevant document IDs

    Returns:
        MRR score (0 to 1)
    """
    relevant_set = set(relevant_ids)

    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in relevant_set:
            return 1.0 / (i + 1)

    return 0.0


def ndcg_at_k(retrieved_ids: List[str],
              relevant_ids: List[str],
              relevance_scores: Dict[str, float] = None,
              k: int = 10) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG@K)

    NDCG measures ranking quality with graded relevance

    Args:
        retrieved_ids: List of retrieved document IDs (ordered by rank)
        relevant_ids: List of relevant document IDs
        relevance_scores: Optional dict mapping doc_id to relevance score
        k: Cut-off rank

    Returns:
        NDCG@K score (0 to 1)
    """
    # Default binary relevance
    if relevance_scores is None:
        relevance_scores = {doc_id: 1.0 for doc_id in relevant_ids}

    # DCG calculation
    dcg = 0.0
    for i in range(min(k, len(retrieved_ids))):
        doc_id = retrieved_ids[i]
        rel = relevance_scores.get(doc_id, 0.0)
        dcg += rel / np.log2(i + 2)  # +2 because log2(1) = 0

    # Ideal DCG (perfect ranking)
    ideal_relevances = sorted(
        [relevance_scores.get(doc_id, 0.0) for doc_id in relevant_ids],
        reverse=True
    )
    idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_relevances[:k]))

    return dcg / idcg if idcg > 0 else 0.0


def hit_rate_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """
    Calculate Hit Rate@K (whether any relevant doc is in top K)

    Args:
        retrieved_ids: List of retrieved document IDs (ordered by rank)
        relevant_ids: List of relevant document IDs
        k: Cut-off rank

    Returns:
        Hit Rate@K score (0 or 1)
    """
    retrieved_at_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)

    return 1.0 if len(retrieved_at_k & relevant_set) > 0 else 0.0


class RetrievalEvaluator:
    """
    Comprehensive evaluation for retrieval systems

    Usage:
        evaluator = RetrievalEvaluator(k_values=[1, 5, 10])
        for qid, query in queries.items():
            results = retriever.retrieve(query, k=10)
            retrieved_ids = [r["passage_id"] for r in results]
            evaluator.evaluate(retrieved_ids, qrels[qid])
        metrics = evaluator.get_mean_metrics()
    """

    def __init__(self, k_values: List[int] = None):
        """
        Initialize evaluator

        Args:
            k_values: K values for evaluation metrics
        """
        self.k_values = k_values or [1, 5, 10]
        self.reset()

    def reset(self) -> None:
        """Reset all metrics"""
        self.results = {
            "recall": {k: [] for k in self.k_values},
            "precision": {k: [] for k in self.k_values},
            "hit_rate": {k: [] for k in self.k_values},
            "ap": [],
            "mrr": [],
            "ndcg": {k: [] for k in self.k_values}
        }
        self.query_count = 0

    def evaluate(self,
                retrieved_ids: List[str],
                relevant_ids: List[str],
                relevance_scores: Dict[str, float] = None) -> Dict:
        """
        Evaluate a single query

        Args:
            retrieved_ids: Retrieved document IDs (ordered)
            relevant_ids: Relevant document IDs
            relevance_scores: Optional relevance scores for NDCG

        Returns:
            Dictionary of metrics for this query
        """
        query_metrics = {}

        # Recall@K
        for k in self.k_values:
            recall = recall_at_k(retrieved_ids, relevant_ids, k)
            self.results["recall"][k].append(recall)
            query_metrics[f"recall@{k}"] = recall

        # Precision@K
        for k in self.k_values:
            precision = precision_at_k(retrieved_ids, relevant_ids, k)
            self.results["precision"][k].append(precision)
            query_metrics[f"precision@{k}"] = precision

        # Hit Rate@K
        for k in self.k_values:
            hit = hit_rate_at_k(retrieved_ids, relevant_ids, k)
            self.results["hit_rate"][k].append(hit)
            query_metrics[f"hit_rate@{k}"] = hit

        # Average Precision
        ap = average_precision(retrieved_ids, relevant_ids)
        self.results["ap"].append(ap)
        query_metrics["ap"] = ap

        # MRR
        mrr_score = mrr(retrieved_ids, relevant_ids)
        self.results["mrr"].append(mrr_score)
        query_metrics["mrr"] = mrr_score

        # NDCG@K
        for k in self.k_values:
            ndcg = ndcg_at_k(retrieved_ids, relevant_ids, relevance_scores, k)
            self.results["ndcg"][k].append(ndcg)
            query_metrics[f"ndcg@{k}"] = ndcg

        self.query_count += 1
        return query_metrics

    def get_mean_metrics(self) -> Dict:
        """
        Get mean metrics across all evaluated queries

        Returns:
            Dictionary of mean metrics
        """
        if self.query_count == 0:
            return {}

        mean_metrics = {}

        for k in self.k_values:
            mean_metrics[f"recall@{k}"] = np.mean(self.results["recall"][k])
            mean_metrics[f"precision@{k}"] = np.mean(self.results["precision"][k])
            mean_metrics[f"hit_rate@{k}"] = np.mean(self.results["hit_rate"][k])
            mean_metrics[f"ndcg@{k}"] = np.mean(self.results["ndcg"][k])

        mean_metrics["map"] = np.mean(self.results["ap"])
        mean_metrics["mrr"] = np.mean(self.results["mrr"])

        return mean_metrics

    def get_std_metrics(self) -> Dict:
        """Get standard deviation of metrics"""
        if self.query_count == 0:
            return {}

        std_metrics = {}

        for k in self.k_values:
            std_metrics[f"recall@{k}"] = np.std(self.results["recall"][k])
            std_metrics[f"precision@{k}"] = np.std(self.results["precision"][k])
            std_metrics[f"hit_rate@{k}"] = np.std(self.results["hit_rate"][k])
            std_metrics[f"ndcg@{k}"] = np.std(self.results["ndcg"][k])

        std_metrics["map"] = np.std(self.results["ap"])
        std_metrics["mrr"] = np.std(self.results["mrr"])

        return std_metrics

    def print_results(self) -> None:
        """Print evaluation results"""
        mean = self.get_mean_metrics()

        print(f"\n{'='*50}")
        print(f"Evaluation Results ({self.query_count} queries)")
        print(f"{'='*50}\n")

        print("Recall@K:")
        for k in self.k_values:
            print(f"  Recall@{k}: {mean.get(f'recall@{k}', 0):.4f}")

        print("\nPrecision@K:")
        for k in self.k_values:
            print(f"  Precision@{k}: {mean.get(f'precision@{k}', 0):.4f}")

        print("\nOther Metrics:")
        print(f"  MRR: {mean.get('mrr', 0):.4f}")
        print(f"  MAP: {mean.get('map', 0):.4f}")

        print("\nNDCG@K:")
        for k in self.k_values:
            print(f"  NDCG@{k}: {mean.get(f'ndcg@{k}', 0):.4f}")


def evaluate_retriever(retriever,
                      queries: Dict[str, str],
                      qrels: Dict[str, List[str]],
                      k_values: List[int] = None,
                      verbose: bool = True) -> Dict:
    """
    Evaluate a retriever on a set of queries

    Args:
        retriever: Retriever instance with retrieve() method
        queries: Dictionary of query_id -> query text
        qrels: Dictionary of query_id -> list of relevant doc_ids
        k_values: K values for evaluation
        verbose: Whether to print results

    Returns:
        Dictionary of evaluation metrics
    """
    if k_values is None:
        k_values = [1, 5, 10]

    evaluator = RetrievalEvaluator(k_values)

    total_time = 0

    for qid, query in queries.items():
        # Retrieve
        start = time.time()
        results = retriever.retrieve(query, k=max(k_values))
        elapsed = time.time() - start
        total_time += elapsed

        # Get retrieved IDs
        retrieved_ids = [r["passage_id"] for r in results]

        # Get relevant IDs
        relevant_ids = qrels.get(qid, [])

        # Evaluate
        evaluator.evaluate(retrieved_ids, relevant_ids)

    # Get mean metrics
    mean_metrics = evaluator.get_mean_metrics()
    mean_metrics["avg_retrieval_time"] = total_time / len(queries) if queries else 0

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Evaluation on {len(queries)} queries")
        print(f"{'='*60}")
        print(f"\nAverage retrieval time: {mean_metrics['avg_retrieval_time']*1000:.2f}ms\n")

        print("Recall@K:")
        for k in k_values:
            print(f"  Recall@{k}: {mean_metrics[f'recall@{k}']:.4f}")

        print("\nMRR & MAP:")
        print(f"  MRR: {mean_metrics['mrr']:.4f}")
        print(f"  MAP: {mean_metrics['map']:.4f}")

    return mean_metrics


def compare_retrievers(retrievers: Dict[str, object],
                      queries: Dict[str, str],
                      qrels: Dict[str, List[str]],
                      k_values: List[int] = None) -> Dict:
    """
    Compare multiple retrievers

    Args:
        retrievers: Dictionary of retriever_name -> retriever_instance
        queries: Test queries
        qrels: Relevance judgments
        k_values: K values for evaluation

    Returns:
        Comparison results
    """
    if k_values is None:
        k_values = [1, 5, 10]

    print("\n=== Comparing Retrievers ===\n")

    comparison = {}

    for name, retriever in retrievers.items():
        print(f"\nEvaluating: {name}")
        metrics = evaluate_retriever(retriever, queries, qrels, k_values, verbose=False)
        comparison[name] = metrics

        print(f"  MRR: {metrics['mrr']:.4f}")
        print(f"  Recall@10: {metrics['recall@10']:.4f}")
        print(f"  Avg time: {metrics['avg_retrieval_time']*1000:.2f}ms")

    # Print comparison table
    print("\n" + "="*70)
    print(f"{'Retriever':<20} {'MRR':<10} {'Recall@10':<12} {'Time (ms)':<12}")
    print("="*70)

    for name, metrics in comparison.items():
        print(f"{name:<20} {metrics['mrr']:<10.4f} {metrics['recall@10']:<12.4f} {metrics['avg_retrieval_time']*1000:<12.2f}")

    return comparison


def main():
    """Test the evaluation module"""
    print("=== Evaluation Module Test ===\n")

    # Sample data
    retrieved = ["p1", "p3", "p2", "p5", "p4"]
    relevant = ["p1", "p2"]

    # Test individual metrics
    print("\n--- Testing Individual Metrics ---")
    print(f"Retrieved: {retrieved}")
    print(f"Relevant: {relevant}")

    print(f"\nRecall@1: {recall_at_k(retrieved, relevant, 1):.4f}")
    print(f"Recall@5: {recall_at_k(retrieved, relevant, 5):.4f}")
    print(f"Precision@5: {precision_at_k(retrieved, relevant, 5):.4f}")
    print(f"MRR: {mrr(retrieved, relevant):.4f}")
    print(f"NDCG@5: {ndcg_at_k(retrieved, relevant, k=5):.4f}")

    # Test evaluator
    print("\n--- Testing RetrievalEvaluator ---")
    evaluator = RetrievalEvaluator(k_values=[1, 5, 10])

    # Evaluate multiple queries
    queries = {
        "q1": (["p1", "p2", "p3"], ["p1", "p5"]),
        "q2": (["p3", "p4", "p5"], ["p2"]),
        "q3": (["p2", "p1", "p5"], ["p1", "p2"])
    }

    for qid, (retrieved, relevant) in queries.items():
        evaluator.evaluate(retrieved, relevant)
        print(f"Query {qid}: MRR={mrr(retrieved, relevant):.4f}")

    # Print mean results
    evaluator.print_results()

    print("\n✅ Evaluation module test completed!")


if __name__ == "__main__":
    main()
