# Literature Summary - RAG Project

**Authors:** Team 10
**Date:** June 2026
**Course:** COMP 8967

---

## Selected Papers

| # | Paper | Focus |
|---|-------|--------|
| 1 | Lewis et al. (2020) - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" | RAG architecture |
| 2 | Karpukhin et al. (2020) - "Dense Passage Retrieval" | DPR architecture |
| 3 | Guu et al. (2020) - "REALM: Retrieval-Augmented Language Model Pre-Training" | Pre-training with retrieval |

---

## Paper Summaries

### 1. Lewis et al. (2020) - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"

**Link:** https://arxiv.org/abs/2005.11401

**Key Idea:**
> [Summarize the core contribution in 1-2 sentences]

**Architecture:**

| Component | Description |
|-----------|-------------|
| Retriever | DPR (dense passage retrieval) - BERT-based |
| Generator | BART or T5 seq2seq model |
| Training | End-to-end or joint training |
| Variants | RAG-Sequence (joint), RAG-Token (independent) |

**Key Findings:**
- [Finding 1]
- [Finding 2]
- [Finding 3]

**Evaluation Results:**
- Dataset: [Which datasets were used?]
- Metrics: [What metrics?]
- Performance: [Key results]

**Relevance to Our Project:**
- [Why is this important for your implementation?]
- [What will you adopt from this approach?]

---

### 2. Karpukhin et al. (2020) - "Dense Passage Retrieval"

**Link:** https://arxiv.org/abs/2004.04906

**Key Idea:**
> [Summarize DPR - how it represents queries and passages as dense embeddings]

**Architecture:**

```
Query → BERT → [CLS] token → Query Embedding (768-dim)
Passage → BERT → [CLS] token → Passage Embedding (768-dim)

Similarity = dot_product(query_emb, passage_emb)
```

**Training Approach:**
- Positive passages: Gold passages from dataset
- Negative passages: In-batch negatives + hard negatives
- Loss: NLL (Negative Log Likelihood)

**Key Findings:**
- [Finding 1 about dense retrieval]
- [Finding 2 about training strategies]
- [Finding 3 about performance]

**Comparison with BM25:**
| Metric | BM25 | DPR |
|--------|------|-----|
| [Metric] | [Score] | [Score] |

**Relevance to Our Project:**
- [How does this inform your embedding model choice?]
- [Will you use similar training strategies?]

---

### 3. Guu et al. (2020) - "REALM: Retrieval-Augmented Language Model Pre-Training"

**Link:** https://arxiv.org/abs/2002.08909

**Key Idea:**
> [Summarize REALM - how it integrates retrieval into pre-training]

**Architecture:**

```
Input Query → MLM Head → Masked Token Prediction
                  ↓
        Retrieval Module (Neural retrieval)
                  ↓
        Retrieved Documents → Context for MLM
```

**Pre-training Objective:**
- Combines Masked Language Modeling with retrieval
- Retrieves documents relevant to masked tokens
- End-to-end training of retriever + reader

**Key Innovations:**
- [Innovation 1]
- [Innovation 2]

**Key Findings:**
- [Finding about pre-training with retrieval]
- [Finding about knowledge integration]

**Relevance to Our Project:**
- [How does this inform your approach?]
- [Is pre-training feasible for your scope?]

---

## Method Comparison

### Architecture Comparison

| Method | Retriever | Generator | Training | Knowledge Source |
|--------|-----------|-----------|----------|------------------|
| RAG | DPR (BERT) | BART/T5 | End-to-end | External passages |
| DPR | BERT (dual encoder) | N/A | Pre-trained + fine-tune | External passages |
| REALM | MLM-based retrieval | MLM (BERT) | Pre-training | External corpus |

### Key Differences

| Aspect | RAG | DPR | REALM |
|--------|-----|-----|-------|
| **Generation** | Yes (seq2seq) | No | Yes (MLM) |
| **Training** | End-to-end | Two-stage | Pre-training |
| **Retrieval** | DPR | DPR | Neural retriever |
| **Use Case** | Open-domain QA | Passage retrieval | Knowledge-intensive tasks |

### Performance Summary

| Method | Dataset | Metric | Score |
|--------|---------|--------|-------|
| RAG | [Dataset] | [Metric] | [Score] |
| DPR | [Dataset] | [Metric] | [Score] |
| REALM | [Dataset] | [Metric] | [Score] |

---

## Key Insights for Implementation

### 1. Architecture Choices

Based on the literature, we will:

**Retrieval:**
- [ ] Use dense retrieval (DPR-style)
- [ ] Model: BGE-small or E5-base (SentenceTransformers)
- [ ] Similarity: Dot product (L2-normalized embeddings)

**Reason:** [Why this choice based on papers]

### 2. Training Strategy

- [ ] Use pre-trained models (no pre-training from scratch)
- [ ] Fine-tune if time permits
- [ ] Use MS MARCO for evaluation

**Reason:** [Scope constraints based on project timeline]

### 3. Evaluation Metrics

From the papers, standard metrics are:

| Metric | Formula | What it Measures |
|--------|---------|------------------|
| Recall@K | relevant in top K / total relevant | Retrieval coverage |
| MRR | 1 / rank of first relevant | Early ranking quality |
| Exact Match | exact answer match | Generation accuracy |

We will use: [Which metrics for your project]

### 4. Implementation Priorities

Based on literature review:

1. **Priority 1:** [What to implement first]
2. **Priority 2:** [What to implement second]
3. **Priority 3:** [Optional enhancements]

---

## Research Gaps & Contribution Opportunities

Based on literature review, potential contributions:

| Area | Gap | Potential Contribution |
|------|-----|------------------------|
| Hybrid Retrieval | Most papers focus on dense only | Compare dense vs sparse vs hybrid |
| Query Expansion | Limited exploration in RAG | LLM-based query expansion |
| Reranking | Not extensively studied | Compare reranking methods |
| Context Optimization | Fixed retrieval amounts | Study optimal K values |

**Our Focus:** [Which area will you focus on?]

---

## Glossary of Key Terms

| Term | Definition |
|-------|------------|
| **Dense Retrieval** | Using vector embeddings to find similar passages |
| **Sparse Retrieval** | Traditional keyword-based search (e.g., BM25) |
| **DPR** | Dense Passage Retrieval - BERT-based dual encoder |
| **RAG** | Retrieval-Augmented Generation |
| **MRR** | Mean Reciprocal Rank - 1/rank of first relevant |
| **Recall@K** | Percentage of relevant documents in top K |
| **Hybrid Retrieval** | Combining dense and sparse retrieval |
| **Reranking** | Reordering retrieved results for better precision |
| **End-to-end Training** | Training retriever and generator together |
| **In-batch Negatives** | Using other batch samples as negative examples |

---

## References

1. Lewis, M., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." arXiv:2005.11401.

2. Karpukhin, V., et al. (2020). "Dense Passage Retrieval for Open-Domain Question Answering." EMNLP 2020.

3. Guu, K., et al. (2020). "REALM: Retrieval-Augmented Language Model Pre-Training." arXiv:2002.08909.

---

## Notes

### Questions for Further Research

- [Question 1]
- [Question 2]
- [Question 3]

### Implementation Ideas

- [Idea 1]
- [Idea 2]
- [Idea 3]

---

*Last Updated: [Date]*
