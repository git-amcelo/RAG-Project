# Week 8 Tasks: Optimization & Evaluation - Part 2

## Overview

**Duration**: Week 8 (July 16 - July 22, 2026)
**Phase**: Optimization & Evaluation - Part 2
**Previous Completed**: Week 1-7 (Requirements, Model Selection, Core RAG, Advanced Features, Optimization Part 1)

---

## Week 8 Theme: Evaluation & Performance Optimization

This week focuses on completing performance optimization based on Week 7 profiling results, optimizing prompt engineering for token efficiency, and completing the evaluation framework to measure standard metrics (Recall, Precision, MRR, Faithfulness). All features align with the project scope defined in the RAG Project Guideline.

---


---

## Week 8 Definition of Done

### Performance Optimization
- [x] All identified performance bottlenecks addressed (embedding, context, expansion caching)
- [x] Prompt engineering optimized with measured token savings (compact templates)
- [x] Response latency improved from baseline (caching implemented)

### Evaluation
- [x] Recall@K, Precision@K, and MRR metrics validated (from Week 3)
- [x] Faithfulness evaluation completed (FaithfulnessEvaluator with Ollama)
- [x] Performance comparison tables created (PerformanceComparer module)

### Integration
- [x] UI for evaluation results functional (timing breakdown and quality scores added to panel)
- [x] End-to-end integration tests passing (run_week8_tests.py all passing)

---

## Success Criteria

### Quantitative Metrics
- **Performance**: Measurable improvement in response latency
- **Token Efficiency**: 20-30% reduction in prompt tokens
- **Evaluation**: Complete Recall@K, Precision@K, and MRR metrics computed

### Project Scope Alignment
- ✅ Performance Optimization - Required
- ✅ Recall, Precision, MRR metrics - Required
- ✅ Faithfulness evaluation - Required

---

## Key Deliverables

### Code Deliverables ✅ COMPLETED
- `src/evaluation/faithfulness.py` - Faithfulness evaluation module (Ollama-based)
- `src/evaluation/comparison.py` - Performance comparison module
- `src/evaluation/evaluation.py` - Evaluation metrics implementation (from Week 3)
- `src/rag_chain.py` - Integrated faithfulness evaluation and caching
- `src/api/main.py` - Added `/evaluate`, `/performance` endpoints
- `run_week8_tests.py` - Complete Week 8 test suite

### Testing Deliverables ✅ COMPLETED
- Standard evaluation metric computations (Recall@K, Precision@K, MRR) - ✅ From Week 3
- Faithfulness evaluation tests - ✅ New for Week 8
- Performance comparison tables (Markdown, CSV, JSON export) - ✅ New for Week 8
- Cache performance tests - ✅ New for Week 8

---

## Next Steps After Week 8

Following the RAG Project Guideline:
- **Week 9**: Refactoring & Documentation - Part 1 (Documentation and analysis of failed retrieval cases)
- **Week 10**: Refactoring & Documentation - Part 2 (Preparing final report and presentation)
- **Week 11**: Final Demo Preparation & Presentation

---

## Evaluation Metrics Reference

*These examples assume a user is asking questions about the **COMP-8567 Assignment 03 PDF**.*

### 1. Recall (Completeness)
* **What it means**: Did the search engine find all the relevant sections in the PDF?
* **Example Query**: *"Can we use the system() function in minibash?"*
  * **Relevant Context in PDF**: There are **2** places in the PDF that explicitly forbid this (Page 1: *"NOTE: You cannot use the system() library function"* and Page 5: *"You cannot use the system() function"*).
  * **If RAG retrieves both pages**: Recall is **100%** ($2/2$).
  * **If RAG retrieves only Page 1**: Recall is **50%** ($1/2$).

### 2. Precision (No Filler)
* **What it means**: How much of the retrieved text is actually useful for answering the query?
* **Example Query**: *"How do you write output to a common FIFO pipe?"*
  * **Relevant Context in PDF**: Page 3 shows: `||| Write output to a common FIFO pipe`.
  * **If RAG retrieves 5 chunks**: If **4** chunks describe the FIFO pipe `|||` rules, but **1** chunk describes the plagiarism detection tool (MOSS), Precision is **80%** ($4/5$).

### 3. MRR - Mean Reciprocal Rank (Placement)
* **What it means**: How high up in the search results did the system place the most relevant page?
* **Example Query**: *"What does the pstop command do?"*
  * If the page showing `pstop stop the most recently created background process` (Page 2) is returned at **Rank 1**: Score is **1.0** ($1/1$).
  * If it is returned at **Rank 3**: Score is **0.33** ($1/3$).
  * If it is not found at all: Score is **0.0**.

### 4. Faithfulness (Honesty)
* **What it means**: Did the AI stick strictly to the facts in the assignment document without hallucinating?
* **Example Query**: *"What is the file naming convention for submission?"*
  * **Faithful**: The AI answers *"You must submit the file named `minibash_fname_lname_SID.c`"*, which matches the PDF's requirement: *"You need to submit the following: 1. minibash_fname_lname_SID.c"*.
  * **Unfaithful**: The AI answers *"You must submit the file named `assignment_3.zip`"*, which is unfaithful because the PDF explicitly requires `minibash_fname_lname_SID.c` and does not mention `assignment_3.zip`.

---
```text
What It Actually Does:

# It tests these metrics with sample data:
- Recall@K: "How many relevant docs found in top K?"
- Precision@K: "How accurate are the top K results?"
- MRR: "Mean Reciprocal Rank - first relevant doc position"
```
*Last Updated: July 7, 2026*
