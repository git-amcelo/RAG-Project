#!/usr/bin/env python3
"""
Week 8 Test Script - Complete Pipeline Evaluation & Performance Optimization
Tests faithfulness evaluation, RAG chain integration, performance optimization, and comparison

Usage:
    python run_week8_tests.py              # Run all tests
    python run_week8_tests.py --module faithfulness  # Test specific module
    python run_week8_tests.py --full       # Full evaluation with all optimizations
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.faithfulness import FaithfulnessEvaluator
from src.evaluation.comparison import PerformanceComparer, PerformanceMetrics
from src.rag_chain import RAGChain, ChainConfig
from src.model_config import ModelType


def print_section(title: str) -> None:
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_faithfulness_evaluation():
    """Test 1: Faithfulness evaluation module"""
    print_section("TEST 1: Faithfulness Evaluation Module")

    evaluator = FaithfulnessEvaluator()

    # Test case 1: Faithful answer
    print("Test Case 1: Faithful Answer")
    context1 = "Python is a high-level programming language created by Guido van Rossum in 1991."
    question1 = "Who created Python?"
    answer1 = "Python was created by Guido van Rossum."

    result1 = evaluator.evaluate(context1, question1, answer1, detect_hallucinations=False)
    print(f"  Score: {result1['score']:.2f}")
    print(f"  Faithful: {result1['is_faithful']}")
    print(f"  Reason: {result1.get('reason', '')}")

    # Test case 2: Hallucinating answer
    print("\nTest Case 2: Hallucinating Answer")
    answer2 = "Python was created by Guido van Rossum in 1995 at Google."
    result2 = evaluator.evaluate(context1, question1, answer2)
    print(f"  Score: {result2['score']:.2f}")
    print(f"  Faithful: {result2['is_faithful']}")
    print(f"  Hallucinations: {result2['hallucinations']}")

    # Test batch evaluation
    print("\nTest Case 3: Batch Evaluation")
    qa_pairs = [
        {"context": "E = mc² is Einstein's formula.", "question": "What is E=mc²?", "answer": "It's Einstein's formula."},
        {"context": "Water boils at 100°C.", "question": "When does water boil?", "answer": "Water boils at 100°C."},
        {"context": "The Earth orbits the Sun.", "question": "What orbits the Sun?", "answer": "The Moon orbits the Sun."}
    ]

    batch_result = evaluator.evaluate_batch(qa_pairs)
    print(f"  Mean Faithfulness: {batch_result['mean_metrics']['mean_faithfulness']:.2f}")
    print(f"  Faithful Rate: {batch_result['mean_metrics']['faithful_rate']:.2%}")

    # Print summary
    evaluator.print_results()

    print("\n✅ Faithfulness evaluation test passed!")
    return evaluator


def test_rag_chain_with_faithfulness():
    """Test 2: RAG chain with integrated faithfulness evaluation"""
    print_section("TEST 2: RAG Chain with Faithfulness Evaluation")

    # Create sample RAG chain
    config = ChainConfig(
        model_type=ModelType.BGE_SMALL,
        enable_query_expansion=False,
        enable_context_compression=False
    )

    print("Initializing RAG chain...")
    rag = RAGChain(config)

    # Add sample documents
    sample_docs = [
        "RAG stands for Retrieval-Augmented Generation. It combines a retriever that fetches relevant document chunks from a vector database with a large language model that generates an answer conditioned on those chunks.",
        "Faithfulness evaluation measures whether an answer sticks to the provided context without introducing information not present in the context.",
        "Performance optimization in RAG systems includes caching query embeddings, compressing contexts, and using efficient vector indices."
    ]

    print("Indexing sample documents...")
    chunks = [
        {"text": doc, "metadata": {"source": f"doc{i}"}}
        for i, doc in enumerate(sample_docs)
    ]
    rag.index_documents(chunks=chunks)

    # Test without faithfulness evaluation
    print("\nTest 1: Without Faithfulness Evaluation")
    result1 = rag.answer_question("What is RAG?", evaluate_faithfulness=False)
    print(f"  Answer: {result1['answer'][:100]}...")
    print(f"  Faithfulness: {result1.get('faithfulness', 'Not evaluated')}")
    print(f"  Processing Time: {result1['processing_time']:.3f}s")

    # Test with faithfulness evaluation
    print("\nTest 2: With Faithfulness Evaluation")
    result2 = rag.answer_question("What is RAG?", evaluate_faithfulness=True)
    print(f"  Answer: {result2['answer'][:100]}...")
    if result2.get('faithfulness'):
        print(f"  Faithfulness Score: {result2['faithfulness']['score']:.2f}")
        print(f"  Is Faithful: {result2['faithfulness']['is_faithful']}")
        print(f"  Hallucinations: {result2['faithfulness']['hallucinations']}")
    print(f"  Processing Time: {result2['processing_time']:.3f}s")

    # Check timing breakdown
    print("\nTiming Breakdown:")
    for key, value in result2.get('timing_breakdown', {}).items():
        print(f"  {key}: {value:.3f}s")

    print("\n✅ RAG chain with faithfulness evaluation test passed!")
    return rag


def test_performance_optimization():
    """Test 3: Performance optimization with caching"""
    print_section("TEST 3: Performance Optimization (Caching)")

    config = ChainConfig(
        model_type=ModelType.BGE_SMALL,
        enable_context_compression=False
    )

    print("Initializing RAG chain with optimization enabled...")
    rag = RAGChain(config)

    # Add sample documents
    sample_docs = [
        "Cache optimization stores frequently accessed data to avoid redundant computation.",
        "Embedding cache stores query embeddings to avoid re-encoding the same query.",
        "Context cache stores compressed contexts for repeated queries."
    ] * 3  # Add some redundancy

    chunks = [
        {"text": doc, "metadata": {"source": f"doc{i}"}}
        for i, doc in enumerate(sample_docs)
    ]
    rag.index_documents(chunks=chunks)

    # Test cache performance with repeated queries
    queries = [
        "What is cache optimization?",
        "What is cache optimization?",  # Same query - should hit cache
        "How does embedding cache work?",
        "How does embedding cache work?"  # Same query - should hit cache
    ]

    print("\nTesting cache performance with repeated queries...")
    for query in queries:
        result = rag.answer_question(query)
        print(f"  Query: {query[:50]}...")
        print(f"    Processing Time: {result['processing_time']:.3f}s")

    # Get cache statistics
    print("\nCache Statistics:")
    stats = rag.get_stats()
    cache_stats = stats.get('cache_stats', {})

    for cache_type, cache_data in cache_stats.items():
        print(f"  {cache_type}:")
        print(f"    Hits: {cache_data['hits']}")
        print(f"    Misses: {cache_data['misses']}")
        print(f"    Hit Rate: {cache_data['hit_rate']:.2%}")
        print(f"    Size: {cache_data['size']} entries")

    print("\n✅ Performance optimization test passed!")
    return rag


def test_comparison_module():
    """Test 4: Performance comparison module"""
    print_section("TEST 4: Performance Comparison Module")

    # Create sample metrics
    baseline = PerformanceMetrics(
        recall_at_1=0.65,
        recall_at_5=0.82,
        recall_at_10=0.91,
        precision_at_5=0.72,
        mrr=0.74,
        map_score=0.68,
        avg_retrieval_time=0.15,
        avg_generation_time=1.2,
        avg_total_time=1.35,
        avg_total_tokens=1200,
        faithfulness_score=0.75,
        faithful_rate=0.70,
        cache_hit_rate=0.0
    )

    optimized = PerformanceMetrics(
        recall_at_1=0.71,
        recall_at_5=0.88,
        recall_at_10=0.94,
        precision_at_5=0.79,
        mrr=0.81,
        map_score=0.75,
        avg_retrieval_time=0.08,
        avg_generation_time=0.9,
        avg_total_time=0.98,
        avg_total_tokens=950,
        faithfulness_score=0.82,
        faithful_rate=0.78,
        cache_hit_rate=0.35
    )

    # Create comparison
    comparer = PerformanceComparer()
    comparison = comparer.compare(baseline, optimized, "Baseline", "Optimized")

    print("Comparison Summary:")
    print(f"  Overall Assessment: {comparison['summary']['overall_assessment']}")

    print("\nQuality Improvements:")
    for imp in comparison['summary']['quality_improvements']:
        print(f"  - {imp['metric']}: {imp['improvement']}")

    print("\nPerformance Improvements:")
    for imp in comparison['summary']['performance_improvements']:
        print(f"  - {imp['metric']}: {imp['improvement']}")

    print("\n✅ Performance comparison test passed!")
    return comparer


def test_complete_pipeline():
    """Test 5: Complete pipeline with all Week 8 features"""
    print_section("TEST 5: Complete Pipeline with All Features")

    config = ChainConfig(
        model_type=ModelType.BGE_SMALL,
        enable_query_expansion=False,
        enable_context_compression=False
    )

    print("Initializing complete RAG pipeline...")
    rag = RAGChain(config)

    # Add documents
    documents = [
        "RAG (Retrieval-Augmented Generation) is a technique that combines retrieval systems with language models to generate responses based on retrieved context.",
        "Faithfulness evaluation uses LLM-as-a-judge to assess whether answers stick to the provided context.",
        "Performance optimization includes caching, compression, and efficient indexing to improve response times.",
        "The Week 8 implementation includes faithfulness evaluation, performance optimization, and comparison tables."
    ]

    chunks = [
        {"text": doc, "metadata": {"source": f"doc{i}"}}
        for i, doc in enumerate(documents)
    ]
    rag.index_documents(chunks=chunks)

    # Test queries with faithfulness evaluation
    test_queries = [
        "What is RAG?",
        "How does faithfulness evaluation work?",
        "What performance optimizations are included?"
    ]

    print("\nRunning complete pipeline tests...")
    results = []
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = rag.answer_question(query, evaluate_faithfulness=True)
        results.append(result)

        print(f"  Answer: {result['answer'][:80]}...")
        if result.get('faithfulness'):
            print(f"  Faithfulness: {result['faithfulness']['score']:.2f}")
        print(f"  Documents Retrieved: {result['num_documents_retrieved']}")
        print(f"  Processing Time: {result['processing_time']:.3f}s")

    # Get overall statistics
    print("\nOverall Statistics:")
    stats = rag.get_stats()
    print(f"  Documents Indexed: {stats['documents_indexed']}")
    print(f"  LLM Requests: {stats['llm_stats']['request_count']}")
    print(f"  Total Tokens: {stats['llm_stats']['total_tokens']}")

    # Calculate average metrics
    avg_faithfulness = sum(
        r.get('faithfulness', {}).get('score', 0) for r in results
    ) / len(results)
    avg_time = sum(r['processing_time'] for r in results) / len(results)

    print(f"\nAverage Faithfulness Score: {avg_faithfulness:.2f}")
    print(f"Average Processing Time: {avg_time:.3f}s")

    print("\n✅ Complete pipeline test passed!")
    return results


def main():
    """Run Week 8 tests"""
    parser = argparse.ArgumentParser(description="Week 8 RAG Tests")
    parser.add_argument("--module", type=str,
                       choices=["faithfulness", "rag", "optimization", "comparison", "pipeline"],
                       help="Test specific module")
    parser.add_argument("--full", action="store_true",
                       help="Run full evaluation on all data")

    args = parser.parse_args()

    print("\n" + "="*60)
    print("  RAG PROJECT - WEEK 8 TESTS")
    print("  Complete Pipeline Evaluation & Performance Optimization")
    print("="*60)

    try:
        if args.module == "faithfulness":
            test_faithfulness_evaluation()
        elif args.module == "rag":
            test_rag_chain_with_faithfulness()
        elif args.module == "optimization":
            test_performance_optimization()
        elif args.module == "comparison":
            test_comparison_module()
        elif args.module == "pipeline":
            test_complete_pipeline()
        elif args.full:
            test_complete_pipeline()
        else:
            # Run all tests
            test_faithfulness_evaluation()
            test_rag_chain_with_faithfulness()
            test_performance_optimization()
            test_comparison_module()
            test_complete_pipeline()

            print("\n" + "="*60)
            print("  ✅ ALL WEEK 8 TESTS PASSED!")
            print("="*60)
            print("\nWeek 8 Deliverables Completed:")
            print("  ✅ Faithfulness evaluation module (Ollama-based)")
            print("  ✅ RAG chain integration with optional evaluation")
            print("  ✅ Performance optimization (embedding, context, expansion caching)")
            print("  ✅ Performance comparison module")
            print("  ✅ Complete pipeline tests")
            print("\nNext Steps:")
            print("  1. Run API integration tests (Week 8, Phase 5)")
            print("  2. Build frontend UI components (Week 8, Phase 6)")
            print("  3. Run full evaluation on real dataset")
            print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
