# JIRA Tickets - RAG Project Week 8: Optimization & Evaluation - Part 2

---
```text
What It Actually Does:

# It tests these metrics with sample data:
- Recall@K: "How many relevant docs found in top K?"
- Precision@K: "How accurate are the top K results?"
- MRR: "Mean Reciprocal Rank - first relevant doc position"
```

## Ticket RAG-W8-01

**Title**: Performance Optimization & Prompt Engineering

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 1

**Description**:
Complete performance optimization based on Week 7 profiling results and optimize prompt engineering for cost/token efficiency.

**Planned Work**:
- Review and analyze Week 7 profiling results
- Implement identified performance optimizations
- Optimize database queries and vector operations
- Improve memory management and garbage collection
- Optimize async operations and concurrency
- Analyze current prompt token usage
- Optimize prompts for token efficiency (20-30% reduction target)
- Implement prompt templates for reuse
- Test optimized prompts for quality retention

**Definition of Done**:
- [x] All performance optimizations from profiling implemented (embedding, context, and expansion caching)
- [x] Prompt engineering optimized with 20-30% token reduction (compact templates integrated)
- [x] Response latency improved from baseline (caching integrated)

---

## Ticket RAG-W8-02

**Title**: Evaluation Metrics Completion

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 2

**Description**:
Complete evaluation framework enhancement including MS MARCO and SQuAD v2, and implement standard retrieval metrics.

**Planned Work**:
- Complete MS MARCO evaluation framework
- Complete SQuAD v2 evaluation framework
- Implement and verify Recall@K (K=1, 5, 10) and Precision@K metrics
- Implement MRR (Mean Reciprocal Rank) metrics
- Create baseline evaluation runs
- Create performance comparison tables and visualizations

**Definition of Done**:
- [x] Recall@K, Precision@K, and MRR metrics implemented and validated
- [x] Baseline evaluation runs completed
- [x] Performance comparison tables created

---

## Ticket RAG-W8-03

**Title**: Generation Quality & Faithfulness Evaluation

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 3

**Description**:
Set up and execute faithfulness evaluation of RAG generation using standard approaches (LLM-as-a-judge or similar benchmarks).

**Planned Work**:
- Set up evaluation framework for response generation
- Implement Faithfulness metrics
- Run evaluation on generation benchmarks

**Definition of Done**:
- [x] Faithfulness evaluation framework operational
- [x] Benchmarks executed and results recorded

---

## Ticket RAG-W8-04

**Title**: UI Enhancement & End-to-End Integration

**Type**: Story | Priority: High | Story Points: 8 | Assignee: Team Member 4

**Description**:
Build UI for evaluation results display and conduct end-to-end integration testing of all optimizations.

**Planned Work**:
- Build UI for evaluation results display
- Add performance metrics visualization
- Create comparison views for different configurations
- Implement export functionality for results
- Test complete RAG pipeline with optimizations
- Test all evaluation metrics end-to-end
- Create integration test suite

**Definition of Done**:
- [x] UI for evaluation results functional
- [x] Export functionality operational
- [x] End-to-end integration tests passing

---

## Summary

**Team Distribution**:
- **Team Member 1**: Performance Optimization & Prompts (8 SP)
- **Team Member 2**: Evaluation Metrics (8 SP)
- **Team Member 3**: Faithfulness Evaluation (8 SP)
- **Team Member 4**: UI & Integration (8 SP)

*Last Updated: July 7, 2026*
