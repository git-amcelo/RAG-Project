#!/usr/bin/env python3
"""
Week 3 Benchmark Reconstruction - Model Comparison
Recreates Week 3 evaluation for both BGE-small and E5-base models
to provide comprehensive comparison using the same benchmark.

Usage:
    python benchmarks/week3_reconstruction.py                    # Compare both models
    python benchmarks/week3_reconstruction.py --model bge       # Test BGE-small only
    python benchmarks/_week3_reconstruction.py --model e5      # Test E5-base only
"""

import sys
import os
import argparse
import json
import time
from typing import Dict, List
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import MSMarcoDataLoader
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.retriever import DenseRetriever
from src.evaluation import RetrievalEvaluator, evaluate_retriever


def print_section(title: str) -> None:
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def evaluate_model(model_name: str, model_path: str, queries: Dict, passages: Dict, qrels: Dict,
                  k_values: List[int] = [1, 5, 10]) -> Dict:
    """
    Evaluate a single embedding model on Week 3 benchmark

    Args:
        model_name: Display name for the model
        model_path: HuggingFace model path
        queries: Test queries
        passages: Test passages
        qrels: Relevance judgments
        k_values: K values for evaluation

    Returns:
        Dictionary with evaluation results
    """
    print_section(f"Evaluating {model_name}")

    results = {
        "model_name": model_name,
        "model_path": model_path,
        "embedding_dim": None,
        "index_time": None,
        "retrieval_time": None,
        "metrics": {}
    }

    # Initialize model
    print(f"Loading {model_name}...")
    start_time = time.time()
    model = EmbeddingModel(model_path)
    load_time = time.time() - start_time

    results["embedding_dim"] = model.embedding_dim
    results["load_time"] = load_time
    print(f"✓ Model loaded in {load_time:.2f}s")
    print(f"✓ Embedding dimension: {model.embedding_dim}")

    # Create retriever
    print(f"\nCreating DenseRetriever with {model_name}...")
    retriever = DenseRetriever(model_path, index_type="flat")

    # Index passages
    print(f"Indexing {len(passages)} passages...")
    start_time = time.time()
    retriever.index_passages(passages, save_embeddings=False)
    index_time = time.time() - start_time

    results["index_time"] = index_time
    print(f"✓ Indexing completed in {index_time:.2f}s")

    # Evaluate retrieval
    print(f"\nEvaluating retrieval on {len(queries)} queries...")
    start_time = time.time()
    metrics = evaluate_retriever(
        retriever,
        queries,
        qrels,
        k_values=k_values,
        verbose=True
    )
    retrieval_time = time.time() - start_time

    results["retrieval_time"] = retrieval_time
    results["metrics"] = metrics
    print(f"✓ Evaluation completed in {retrieval_time:.2f}s")

    return results


def compare_models(results: List[Dict]) -> None:
    """Display comparison between models"""
    print_section("MODEL COMPARISON RESULTS")

    # Create comparison table
    print("\n┌" + "─" * 68 + "┐")
    print("│" + " " * 20 + "BGE-small vs E5-base Comparison" + " " * 22 + "│")
    print("├" + "─" * 68 + "┤")

    # Header
    print("│ {:<15} │ {:<12} │ {:<12} │ {:<12} │ {:<12} │".format(
        "Metric", "BGE-small", "E5-base", "Difference", "Improvement"
    ))
    print("├" + "─" * 68 + "┤")

    # Extract metrics for both models
    bge_results = next(r for r in results if "bge-small" in r["model_name"].lower())
    e5_results = next(r for r in results if "e5-base" in r["model_name"].lower())

    # Comparison metrics
    metrics_to_compare = [
        ("Embedding Dim", "embedding_dim", "", ""),
        ("Index Time (s)", "index_time", "", ""),
        ("Retrieval Time (s)", "retrieval_time", "", ""),
        ("Recall@1", "metrics", "recall@1", "%"),
        ("Recall@5", "metrics", "recall@5", "%"),
        ("Recall@10", "metrics", "recall@10", "%"),
        ("MRR", "metrics", "mrr", "%"),
        ("MAP", "metrics", "map", "%"),
    ]

    for display_name, key1, key2, suffix in metrics_to_compare:
        if key2 == "":
            # Direct comparison
            bge_val = bge_results[key1]
            e5_val = e5_results[key1]
            diff = e5_val - bge_val

            if key1 == "embedding_dim":
                diff_str = f"+{int(diff)} dims"
                improvement = "Higher capacity"
            elif key1 == "index_time" or key1 == "retrieval_time":
                diff_pct = (diff / bge_val) * 100
                diff_str = f"+{diff:.2f}s ({diff_pct:+.1f}%)"
                improvement = "Slower" if diff > 0 else "Faster"
            else:
                diff_str = f"{diff:+.4f}"
                improvement = ""
        else:
            # Nested metrics comparison
            bge_val = bge_results[key1][key2]
            e5_val = e5_results[key1][key2]
            diff = e5_val - bge_val
            diff_pct = (diff / bge_val) * 100 if bge_val > 0 else 0

            diff_str = f"{diff:+.4f} ({diff_pct:+.1f}%)"
            improvement = "Better" if diff > 0 else "Worse"

        print("│ {:<15} │ {:<12} │ {:<12} │ {:<12} │ {:<12} │".format(
            display_name,
            f"{bge_val:.4f}" if isinstance(bge_val, float) else str(bge_val),
            f"{e5_val:.4f}" if isinstance(e5_val, float) else str(e5_val),
            diff_str,
            improvement
        ))

    print("└" + "─" * 68 + "┘")

    # Recommendations
    print("\n📊 RECOMMENDATIONS:")
    print("─" * 70)

    recall_diff = e5_results["metrics"]["recall@5"] - bge_results["metrics"]["recall@5"]
    time_diff = e5_results["retrieval_time"] - bge_results["retrieval_time"]

    print(f"\n🎯 Use BGE-small when:")
    print(f"   • Fast response times are critical")
    print(f"   • Memory/storage constraints exist")
    print(f"   • General retrieval quality is sufficient")
    print(f"   • Processing many concurrent queries")

    print(f"\n🎯 Use E5-base when:")
    print(f"   • Maximum retrieval accuracy is required")
    print(f"   • Complex queries need deeper understanding")
    print(f"   • Ample computational resources available")
    print(f"   • Batch processing (not real-time)")

    print(f"\n💡 Performance Trade-offs:")
    print(f"   • Accuracy gain: {recall_diff*100:+.2f}% Recall@5 improvement")
    print(f"   • Speed cost: {time_diff:+.2f}s additional retrieval time")
    print(f"   • Storage: {e5_results['embedding_dim'] - bge_results['embedding_dim']} extra dimensions per vector")


def save_results(results: List[Dict], output_file: str) -> None:
    """Save comparison results to JSON"""
    output_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark": "Week 3 MS MARCO Reconstruction",
        "models_tested": len(results),
        "results": results
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Results saved to {output_file}")


def main():
    """Run model comparison benchmark"""
    parser = argparse.ArgumentParser(
        description="Week 3 Benchmark Reconstruction - Model Comparison"
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["bge", "e5", "both"],
        default="both",
        help="Which model(s) to test"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmarks/comparison_results.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=100,
        help="Number of queries to test (default: 100)"
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print("  WEEK 3 BENCHMARK RECONSTRUCTION - MODEL COMPARISON")
    print("  BGE-small vs E5-base Embedding Models")
    print("="*70)

    # Load data
    print_section("Loading MS MARCO Data")

    loader = MSMarcoDataLoader()
    try:
        loader.load_processed_data()

        # Limit queries for testing
        queries = dict(list(loader.queries.items())[:args.queries])
        passages = loader.passages
        qrels = loader.qrels

        print(f"✓ Loaded {len(queries)} queries for testing")
        print(f"✓ Loaded {len(passages)} passages")
        print(f"✓ Loaded {len(qrels)} relevance judgments")

    except FileNotFoundError:
        print("❌ No processed data found!")
        print("   Run 'python extract_data.py' first to extract MS MARCO data.")
        return 1

    # Define models to test
    models = {
        "BGE-small": "BAAI/bge-small-en-v1.5",
        "E5-base": "intfloat/e5-base-v2"
    }

    # Determine which models to test
    if args.model == "bge":
        models_to_test = [("BGE-small", models["BGE-small"])]
    elif args.model == "e5":
        models_to_test = [("E5-base", models["E5-base"])]
    else:  # both
        models_to_test = list(models.items())

    # Run evaluation
    results = []
    for model_name, model_path in models_to_test:
        try:
            result = evaluate_model(
                model_name,
                model_path,
                queries,
                passages,
                qrels
            )
            results.append(result)
        except Exception as e:
            print(f"❌ Error evaluating {model_name}: {e}")
            import traceback
            traceback.print_exc()

    # Display comparison if both models tested
    if len(results) == 2:
        compare_models(results)

    # Save results
    save_results(results, args.output)

    print("\n" + "="*70)
    print("  ✅ BENCHMARK COMPLETED!")
    print("="*70 + "\n")

    return 0


if __name__ == "__main__":
    exit(main())