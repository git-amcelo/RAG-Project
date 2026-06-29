# JIRA Tickets - RAG Project Week 6: Hybrid Retrieval & Optimization

## Overview

4 comprehensive JIRA tickets documenting the implementation work for Week 6, focusing on hybrid retrieval, reranking, query expansion, chunk optimization, context compression, and evaluation. All tasks align with the RAG Project Guideline PDF scope. One ticket per team member.

---

## Ticket RAG-W6-01

**Title**: Hybrid Retrieval & Reranking Implementation

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 1

**Description**:
Implement hybrid retrieval combining dense vector search (FAISS) with sparse retrieval (BM25), plus cross-encoder reranking and query expansion to significantly improve retrieval quality.

**Planned Work**:
- Set up BM25/TF-IDF sparse retriever
- Implement weighted fusion strategy (α × dense + (1-α) × sparse)
- Implement Reciprocal Rank Fusion (RRF)
- Add dynamic weighting between dense/sparse
- Integrate with existing FAISS dense retrieval
- Create unified retrieval pipeline
- Set up cross-encoder reranker models (BGE-reranker-base)
- Implement cross-encoder re-ranking pipeline
- Create query expansion module with synonym generation
- Implement query rewriting for ambiguous queries
- Add re-ranking result caching mechanism
- Configure top-K candidates for re-ranking

**Technical Implementation**:
```
Hybrid Retrieval Pipeline:
┌─────────────────────────────────────────────────────────────┐
│  User Query                                                  │
├─────────────────────────────────────────────────────────────┤
│  Query Expansion → Enhanced queries                         │
├─────────────────────────────────────────────────────────────┤
│  ├─ Dense Branch (FAISS) → Top-K dense similarities       │
│  ├─ Sparse Branch (BM25) → Top-K BM25 scores               │
├─────────────────────────────────────────────────────────────┤
│  Fusion Layer (weighted/RRF) → Unified scores              │
├─────────────────────────────────────────────────────────────┤
│  Cross-Encoder Re-ranking → Refined scores                 │
├─────────────────────────────────────────────────────────────┤
│  Final Results → Top-N documents for LLM                   │
└─────────────────────────────────────────────────────────────┘

Fusion Strategies:
- Weighted sum: α × dense_score + (1-α) × sparse_score
- Reciprocal Rank Fusion: 1/(k+rank_dense) + 1/(k+rank_sparse)
- Configurable α parameter for tuning

Query Expansion:
- Synonym generation using WordNet
- Related term extraction using embeddings
- Query decomposition for complex questions
```

**Files to Create**:
- `src/retrieval/hybrid_search.py` - Hybrid search orchestration
- `src/retrieval/sparse_retriever.py` - BM25/TF-IDF implementation
- `src/retrieval/fusion.py` - Fusion strategies
- `src/reranking/cross_encoder.py` - Cross-encoder implementation
- `src/reranking/query_expansion.py` - Query expansion logic
- `src/reranking/cache.py` - Result caching
- `config/hybrid_config.yaml` - Configuration

**Definition of Done**:
- [ ] Hybrid retrieval (dense + BM25) fully functional
- [ ] At least 2 fusion strategies implemented and tested
- [ ] Cross-encoder re-ranking working
- [ ] Query expansion improving retrieval
- [ ] Measurable improvement over dense-only baseline
- [ ] Latency <500ms for hybrid pipeline
- [ ] Configuration tunable via config files

---

## Ticket RAG-W6-02

**Title**: Chunk Optimization & Context Compression

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 2

**Description**:
Implement chunk optimization to analyze the impact of chunk size and overlap on retrieval quality, plus context compression to filter redundant information and optimize context window for LLM input.

**Planned Work**:
- Analyze chunk size impact on retrieval quality
- Experiment with different chunk sizes (256, 512, 1024 tokens)
- Implement overlap optimization (50, 100, 200 tokens)
- Compare retrieval performance across configurations
- Create chunk optimization evaluation framework
- Implement context compression algorithms
- Filter redundant retrieved information
- Create relevance scoring for context chunks
- Optimize context window for LLM input
- Test compression impact on response quality
- Document optimal configuration

**Technical Implementation**:
```
Chunk Optimization:
┌─────────────────────────────────────────────────────────────┐
│  Variables to Test:                                          │
│  - Chunk sizes: [256, 512, 1024, 2048] tokens              │
│  - Overlap: [0, 50, 100, 200] tokens                        │
│  - Splitting method: [recursive, semantic, fixed]           │
├─────────────────────────────────────────────────────────────┤
│  Metrics:                                                    │
│  - Retrieval quality (Recall@K, MRR)                         │
│  - Processing time                                          │
│  - Storage requirements                                     │
│  - LLM context utilization                                  │
└─────────────────────────────────────────────────────────────┘

Context Compression:
┌─────────────────────────────────────────────────────────────┐
│  Strategies:                                                │
│  - Relevance scoring: Rank chunks by query relevance         │
│  - Redundancy removal: Remove similar chunks               │
│  - Length filtering: Limit total context length             │
│  - Information density: Prioritize dense, informative chunks│
└─────────────────────────────────────────────────────────────┘
```

**Evaluation Framework**:
```
Test Configurations:
┌──────────┬──────────┬──────────┬────────────────┐
│ Chunk Size│ Overlap  │ Recall@5 │    MRR         │
├──────────┼──────────┼──────────┼────────────────┤
│ 256      │ 0        │ ?        │ ?              │
│ 256      │ 50       │ ?        │ ?              │
│ 512      │ 100      │ ?        │ ?              │
│ 1024     │ 200      │ ?        │ ?              │
└──────────┴──────────┴──────────┴────────────────┘
```

**Files to Create**:
- `src/optimization/chunk_optimizer.py` - Chunk optimization
- `src/optimization/overlap_analyzer.py` - Overlap analysis
- `src/compression/context_compression.py` - Context compression
- `src/compression/relevance_scorer.py` - Relevance scoring
- `benchmarks/chunk_eval.py` - Chunk evaluation
- `config/chunk_config.yaml` - Chunk configurations

**Definition of Done**:
- [ ] Chunk optimization completed with clear results
- [ ] Optimal chunk size and overlap identified
- [ ] Context compression working
- [ ] Measurable improvement in context efficiency
- [ ] Comprehensive evaluation report
- [ ] Configuration recommendations documented

---

## Ticket RAG-W6-03

**Title**: Evaluation & Benchmarking on Standard Datasets

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 3

**Description**:
Implement comprehensive evaluation framework using standard datasets (MS MARCO, SQuAD v2) to measure retrieval quality with standard metrics (Recall@K, MRR) and prepare IEEE-style results.

**Planned Work**:
- Set up MS MARCO passage retrieval evaluation
- Set up SQuAD v2 question answering evaluation
- Prepare custom PDF/document collection for testing
- Create evaluation data pipeline
- Implement Recall@K (K=1,5,10,20)
- Implement MRR (Mean Reciprocal Rank)
- Implement Precision@K
- Create evaluation metric computation framework
- Set up baseline comparisons
- Evaluate dense retrieval baseline
- Evaluate hybrid retrieval performance
- Evaluate reranking impact
- Create performance comparison tables
- Generate result visualizations
- Analyze failed retrieval cases
- Document retrieval quality improvements
- Create evaluation report
- Prepare IEEE-style results section

**Technical Implementation**:
```
Evaluation Pipeline:
┌─────────────────────────────────────────────────────────────┐
│  Dataset Loading → Query Processing → Retrieval → Metrics   │
├─────────────────────────────────────────────────────────────┤
│  Datasets:                                                  │
│  - MS MARCO: Passage ranking benchmark                     │
│  - SQuAD v2: Question answering & retrieval               │
│  - Custom PDFs: Domain-specific testing                     │
├─────────────────────────────────────────────────────────────┤
│  Metrics:                                                    │
│  - Recall@K: Percentage of relevant docs in top-K          │
│  - MRR: Mean Reciprocal Rank (1/rank of first relevant)    │
│  - Precision@K: Accuracy in top-K results                   │
└─────────────────────────────────────────────────────────────┘

Comparison Table:
┌─────────────────┬───────────┬───────────┬───────────┐
│     Method      │ Recall@5  │    MRR    │ Precision │
├─────────────────┼───────────┼───────────┼───────────┤
│ Dense (FAISS)   │   Base    │   Base    │   Base    │
│ Hybrid (Dense+BM25)│ ?      │     ?     │     ?     │
│ + Reranking     │     ?     │     ?     │     ?     │
│ + Query Exp.    │     ?     │     ?     │     ?     │
└─────────────────┴───────────┴───────────┴───────────┘
```

**Files to Create**:
- `src/evaluation/dataset_loader.py` - Dataset loading
- `src/evaluation/evaluator.py` - Evaluation pipeline
- `src/evaluation/metrics.py` - Metrics computation
- `src/evaluation/comparison.py` - Baseline comparison
- `benchmarks/msmarco_eval.py` - MS MARCO evaluation
- `benchmarks/squad_eval.py` - SQuAD v2 evaluation
- `results/evaluation_report.md` - Evaluation report
- `results/ieee_results.tex` - IEEE-style results

**Definition of Done**:
- [ ] MS MARCO evaluation completed with results
- [ ] SQuAD v2 evaluation completed with results
- [ ] Custom PDF collection evaluated
- [ ] All metrics (Recall@K, MRR, Precision) computed
- [ ] Performance comparison tables created
- [ ] Baseline comparisons documented
- [ ] Failed case analysis completed
- [ ] IEEE-style results section prepared

---

## Ticket RAG-W6-04

**Title**: UI Development, Testing & Documentation

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 4

**Description**:
Build user interface for hybrid retrieval system, implement comprehensive testing, and prepare all documentation including IEEE-style report sections.

**Planned Work**:
- Create query input interface
- Implement results display with ranking
- Add retrieval metrics display (MRR, Recall)
- Create fusion strategy selector
- Build performance comparison view
- Add source attribution display
- Write unit tests for hybrid retrieval
- Write unit tests for reranking
- Write unit tests for chunk optimization
- Create integration tests for pipeline
- Set up automated testing pipeline
- Create API documentation for hybrid retrieval
- Document reranking configuration
- Write chunk optimization guide
- Create evaluation framework documentation
- Prepare IEEE-style report sections
- Update system architecture documentation

**UI Components**:
```
Query Interface:
┌─────────────────────────────────────────────────────────────┐
│  Search Box                                                  │
│  [Enter your query here...]                    [Search]      │
├─────────────────────────────────────────────────────────────┤
│  Fusion Strategy: [Weighted ▼]   α: [0.7]                   │
│  Reranking: [✓] Enable   Model: [BGE-reranker ▼]          │
│  Chunk Size: [512 ▼]    Overlap: [100 ▼]                   │
└─────────────────────────────────────────────────────────────┘

Results Display:
┌─────────────────────────────────────────────────────────────┐
│  Results for: "your query"                                 │
│  ├─ Doc 1 (Score: 0.95) [Dense: 0.92, BM25: 0.88]        │
│  ├─ Doc 2 (Score: 0.87) [Dense: 0.85, BM25: 0.79]        │
│  ├─ Doc 3 (Score: 0.82) [Dense: 0.78, BM25: 0.91]        │
└─────────────────────────────────────────────────────────────┘

Metrics Display:
┌─────────────────────────────────────────────────────────────┐
│  Query Time: 245ms                                          │
│  Recall@5: 0.78  MRR: 0.65  Precision@5: 0.82              │
└─────────────────────────────────────────────────────────────┘
```

**Files to Create**:
- `frontend/src/components/QueryInput.tsx` - Query input
- `frontend/src/components/ResultsDisplay.tsx` - Results display
- `frontend/src/components/MetricsDisplay.tsx` - Metrics display
- `frontend/src/components/FusionControl.tsx` - Fusion controls
- `tests/unit/test_hybrid.py` - Hybrid retrieval tests
- `tests/unit/test_reranking.py` - Reranking tests
- `tests/unit/test_chunking.py` - Chunk optimization tests
- `tests/integration/test_pipeline.py` - Pipeline tests
- `docs/HYBRID_RETRIEVAL.md` - Hybrid retrieval guide
- `docs/RERANKING_GUIDE.md` - Reranking configuration
- `docs/CHUNK_OPTIMIZATION.md` - Chunk optimization results
- `docs/ARCHITECTURE.md` - System architecture
- `results/ieee_report.tex` - IEEE-style report

**Definition of Done**:
- [ ] Functional UI for query input and results display
- [ ] Metrics display showing retrieval performance
- [ ] Fusion strategy controls working
- [ ] Comprehensive unit and integration tests
- [ ] Automated testing pipeline
- [ ] Complete API documentation
- [ ] Configuration guides for all features
- [ ] IEEE-style report sections prepared
- [ ] System architecture documentation updated

---

## Summary

**Week 6 Deliverables**:
- ✅ Hybrid Retrieval (Dense + BM25 with fusion strategies)
- ✅ Reranking with cross-encoder models
- ✅ Query expansion capabilities
- ✅ Chunk optimization with optimal configuration
- ✅ Context compression
- ✅ Evaluation on MS MARCO and SQuAD v2
- ✅ Performance comparison tables and visualizations
- ✅ UI for hybrid retrieval system
- ✅ Comprehensive testing and documentation

**Team Distribution**:
- **Team Member 1**: Hybrid Retrieval & Reranking (8 SP)
- **Team Member 2**: Chunk Optimization & Context Compression (8 SP)
- **Team Member 3**: Evaluation & Benchmarking (8 SP)
- **Team Member 4**: UI, Testing & Documentation (8 SP)

**Project Scope Alignment**:
All tasks align with RAG Project Guideline PDF recommendations:
- ✅ Hybrid Retrieval (Strongly Recommended)
- ✅ Reranking Models (Recommended)
- ✅ Query Expansion (Recommended)
- ✅ Chunk Optimization (Strongly Recommended)
- ✅ Context Compression (Recommended)
- ✅ Standard Evaluation (Recommended)

**Success Criteria**:
- Measurable improvement in retrieval quality (5-10% MRR)
- Optimal chunk configuration identified
- Complete evaluation results on standard datasets
- Functional UI with metrics display
- Comprehensive documentation
- IEEE-style report sections ready

**Technical Stack**:
- **Hybrid Retrieval**: FAISS + BM25/TF-IDF, fusion strategies
- **Reranking**: BGE-reranker models
- **Query Expansion**: Synonym generation, query rewriting
- **Chunk Optimization**: Size and overlap analysis
- **Context Compression**: Relevance scoring, redundancy removal
- **Evaluation**: MS MARCO, SQuAD v2, Recall@K, MRR metrics
- **UI**: React components for query and results display

---

*Last Updated: June 29, 2026*
*Aligned with RAG Project Guideline PDF Scope*
