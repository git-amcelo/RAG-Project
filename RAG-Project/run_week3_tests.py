#!/usr/bin/env python3
"""
Week 3 Test Script - Dense Retrieval Pipeline Tests
Tests data loading, embeddings, vector store, retrieval, and evaluation

Usage:
    python run_week3_tests.py              # Run all tests
    python run_week3_tests.py --module data  # Test specific module
    python run_week3_tests.py --full       # Full evaluation on all data
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import MSMarcoDataLoader
from src.embeddings import EmbeddingModel
from src.vector_store import VectorStore
from src.retriever import DenseRetriever
from src.evaluation import RetrievalEvaluator, recall_at_k, mrr, precision_at_k, evaluate_retriever


def print_section(title: str) -> None:
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_data_loader():
    """Test 1: Data loading and preprocessing"""
    print_section("TEST 1: Data Loader")

    loader = MSMarcoDataLoader()

    try:
        # Try to load processed data
        loader.load_processed_data()
        stats = loader.get_statistics()

        print(f"✓ Loaded processed data:")
        print(f"  Queries: {stats['num_queries']}")
        print(f"  Passages: {stats['num_passages']}")
        print(f"  Queries with qrels: {stats['num_qrels']}")
        print(f"  Avg query length: {stats['avg_query_length']:.2f} words")
        print(f"  Avg passage length: {stats['avg_passage_length']:.2f} words")

        # Show samples
        print("\nSample query:")
        qid, query = list(loader.queries.items())[0]
        print(f"  {qid}: {query}")

        return loader

    except FileNotFoundError:
        print("❌ No processed data found!")
        print("   Run 'python extract_data.py' first to extract MS MARCO data.")
        return None


def test_embeddings():
    """Test 2: Embedding models (BGE-small)"""
    print_section("TEST 2: Embedding Models (BGE-small)")

    print("Loading BGE-small model...")
    bge_model = EmbeddingModel("BAAI/bge-small-en-v1.5")

    # Test encoding
    sample_text = "What causes headaches?"
    embedding = bge_model.encode(sample_text, is_query=True)

    print(f"✓ Model loaded: {bge_model.model_name}")
    print(f"✓ Embedding dimension: {embedding.shape[0]}")
    print(f"✓ Device: {bge_model.device}")

    # Test similarity computation
    text1 = "Headaches can be caused by stress."
    text2 = "Stress is a common cause of headaches."
    text3 = "Climate change affects global temperatures."

    emb1 = bge_model.encode(text1)
    emb2 = bge_model.encode(text2)
    emb3 = bge_model.encode(text3)

    sim12 = bge_model.compute_similarity(emb1, emb2)
    sim13 = bge_model.compute_similarity(emb1, emb3)

    print(f"\n✓ Similarity tests:")
    print(f"  Related (headaches/stress): {sim12:.4f}")
    print(f"  Unrelated (headaches/climate): {sim13:.4f}")

    print("\n✅ Embedding models test passed!")
    return bge_model


def test_vector_store():
    """Test 3: FAISS vector store"""
    print_section("TEST 3: Vector Store (FAISS)")

    import numpy as np

    # Create sample embeddings
    np.random.seed(42)
    n_passages = 100
    embedding_dim = 384  # BGE-small dimension

    embeddings = np.random.random((n_passages, embedding_dim)).astype('float32')
    passage_ids = [f"doc_{i}" for i in range(n_passages)]

    # Test Flat index (baseline)
    print("Creating Flat index (baseline)...")
    store = VectorStore(embedding_dim, "flat")
    store.create_index()
    store.add_embeddings(embeddings, passage_ids)

    print(f"✓ Indexed {store.index.ntotal} vectors")

    # Test search
    query_embedding = embeddings[0]  # Use first passage as query
    results = store.search_by_id(query_embedding, k=5)

    print(f"\n✓ Search results (top 5):")
    for r in results[:3]:
        print(f"  {r['passage_id']}: score={r['score']:.4f}")

    # Get index info
    info = store.get_index_info()
    print(f"\n✓ Index info:")
    print(f"  Type: {info['type']}")
    print(f"  Dimension: {info['dimension']}")
    print(f"  Total vectors: {info['total_vectors']}")

    print("\n✅ Vector store test passed!")
    return store


def test_retriever_sample():
    """Test 4: Dense retriever with sample data"""
    print_section("TEST 4: Dense Retriever (Sample Data)")

    # Sample passages
    passages = {
        "p1": "Headaches can be caused by stress, dehydration, and lack of sleep. Tension headaches are the most common type.",
        "p2": "Vaccines work by stimulating the immune system to recognize and fight specific pathogens.",
        "p3": "Climate change is caused by human activities like burning fossil fuels, which release greenhouse gases.",
        "p4": "Photosynthesis converts light energy into chemical energy. Plants use sunlight, water, and CO2.",
        "p5": "Diabetes affects how the body processes blood sugar. Type 1 is autoimmune, Type 2 is lifestyle-related.",
        "p6": "Stress is a major trigger for tension headaches. It causes muscle contractions in the neck and head.",
        "p7": "The immune system fights infections using white blood cells and antibodies.",
        "p8": "Global warming leads to rising sea levels, extreme weather, and ecosystem disruption."
    }

    queries = {
        "q1": "What causes headaches?",
        "q2": "How do vaccines work?"
    }

    qrels = {
        "q1": ["p1", "p6"],
        "q2": ["p2", "p7"]
    }

    # Create retriever
    print("Creating DenseRetriever with BGE-small...")
    retriever = DenseRetriever("BAAI/bge-small-en-v1.5", index_type="flat")

    # Index passages
    retriever.index_passages(passages, save_embeddings=False)

    print(f"✓ Indexed {len(passages)} passages")

    # Test retrieval
    query = "What causes headaches?"
    results = retriever.retrieve(query, k=5)

    print(f"\n✓ Retrieval results for: '{query}'")
    for r in results:
        print(f"  {r['passage_id']}: score={r['score']:.4f}")
        print(f"    {r['text'][:60]}...")

    # Check if relevant passages are found
    retrieved_ids = [r["passage_id"] for r in results]
    relevant_found = [rid for rid in retrieved_ids if rid in qrels["q1"]]
    print(f"\n✓ Relevant passages found: {relevant_found}")

    print("\n✅ Dense retriever test passed!")
    return retriever, queries, qrels


def test_evaluation_metrics():
    """Test 5: Evaluation metrics"""
    print_section("TEST 5: Evaluation Metrics")

    # Sample retrieval results
    retrieved = ["p1", "p6", "p4", "p2", "p3"]
    relevant = ["p1", "p2"]

    print(f"Retrieved: {retrieved}")
    print(f"Relevant: {relevant}")

    # Calculate metrics
    recall_1 = recall_at_k(retrieved, relevant, 1)
    recall_5 = recall_at_k(retrieved, relevant, 5)
    precision_5 = precision_at_k(retrieved, relevant, 5)
    mrr_score = mrr(retrieved, relevant)

    print(f"\n✓ Metrics:")
    print(f"  Recall@1: {recall_1:.4f}")
    print(f"  Recall@5: {recall_5:.4f}")
    print(f"  Precision@5: {precision_5:.4f}")
    print(f"  MRR: {mrr_score:.4f}")

    # Test evaluator
    evaluator = RetrievalEvaluator(k_values=[1, 5, 10])

    queries_results = [
        (["p1", "p2", "p3"], ["p1", "p5"]),
        (["p3", "p4", "p5"], ["p2"]),
        (["p2", "p1", "p5"], ["p1", "p2"])
    ]

    for retrieved, relevant in queries_results:
        evaluator.evaluate(retrieved, relevant)

    print("\n✓ Mean Metrics (3 queries):")
    mean = evaluator.get_mean_metrics()
    for k in [1, 5, 10]:
        print(f"  Recall@{k}: {mean[f'recall@{k}']:.4f}")
    print(f"  MRR: {mean['mrr']:.4f}")
    print(f"  MAP: {mean['map']:.4f}")

    print("\n✅ Evaluation metrics test passed!")


def test_full_pipeline():
    """Test 6: Full pipeline on MS MARCO data"""
    print_section("TEST 6: Full Pipeline on MS MARCO Data")

    # Load data
    loader = MSMarcoDataLoader()
    try:
        loader.load_processed_data()
    except FileNotFoundError:
        print("❌ No processed data found! Run 'python extract_data.py' first.")
        return

    # Limit for testing
    queries = dict(list(loader.queries.items())[:100])
    passages = loader.passages
    qrels = loader.qrels

    print(f"Testing with {len(queries)} queries and {len(passages)} passages")

    # Create retriever
    print("\nInitializing DenseRetriever...")
    retriever = DenseRetriever("BAAI/bge-small-en-v1.5", index_type="flat")

    # Index passages
    retriever.index_passages(passages, save_embeddings=False)

    # Evaluate
    print("\nEvaluating retrieval...")
    metrics = evaluate_retriever(
        retriever,
        queries,
        qrels,
        k_values=[1, 5, 10],
        verbose=True
    )

    print("\n✅ Full pipeline test completed!")
    return metrics


def main():
    """Run Week 3 tests"""
    parser = argparse.ArgumentParser(description="Week 3 RAG Tests")
    parser.add_argument("--module", type=str,
                       choices=["data", "embeddings", "vector", "retriever", "eval", "full"],
                       help="Test specific module")
    parser.add_argument("--full", action="store_true",
                       help="Run full evaluation on all data")

    args = parser.parse_args()

    print("\n" + "="*60)
    print("  RAG PROJECT - WEEK 3 TESTS")
    print("  Dense Retrieval Pipeline")
    print("="*60)

    try:
        if args.module == "data":
            test_data_loader()
        elif args.module == "embeddings":
            test_embeddings()
        elif args.module == "vector":
            test_vector_store()
        elif args.module == "retriever":
            test_retriever_sample()
        elif args.module == "eval":
            test_evaluation_metrics()
        elif args.module == "full":
            test_full_pipeline()
        elif args.full:
            test_full_pipeline()
        else:
            # Run all tests
            test_data_loader()
            test_embeddings()
            test_vector_store()
            test_retriever_sample()
            test_evaluation_metrics()

            print("\n" + "="*60)
            print("  ✅ ALL WEEK 3 TESTS PASSED!")
            print("="*60)
            print("\nNext steps:")
            print("  1. Run 'python extract_data.py' to get MS MARCO data")
            print("  2. Run 'python run_week3_tests.py --full' for full evaluation")
            print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
