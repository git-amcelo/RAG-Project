"""
Evaluation Module for RAG System
Week 3-8: Comprehensive evaluation metrics

Components:
- Standard Metrics: Recall, Precision, MRR, NDCG, Hit Rate
- Faithfulness Evaluation: LLM-based answer quality assessment
- Evaluator: Comprehensive retrieval evaluation
"""

from .evaluation import (
    # Individual metrics
    recall_at_k,
    precision_at_k,
    average_precision,
    mrr,
    hit_rate_at_k,

    # Evaluator class
    RetrievalEvaluator,

    # Helper functions
    evaluate_retriever,
    compare_retrievers
)

from .faithfulness import (
    # Faithfulness evaluator
    FaithfulnessEvaluator,
    # Helper functions
    evaluate_rag_response
)

from .comparison import (
    # Performance comparison
    PerformanceComparer,
    PerformanceMetrics
)

__all__ = [
    # Standard metrics
    "recall_at_k",
    "precision_at_k",
    "average_precision",
    "mrr",
    "hit_rate_at_k",
    "RetrievalEvaluator",
    "evaluate_retriever",
    "compare_retrievers",
    # Faithfulness evaluation
    "FaithfulnessEvaluator",
    "evaluate_rag_response",
    # Performance comparison
    "PerformanceComparer",
    "PerformanceMetrics",
]
