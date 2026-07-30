# RAG Project - Week 3 Tasks

## Phase 2: Build Retrieval Pipeline (Week 3)

> **Guideline Reference:** Week 3 - Build retrieval pipeline, Implement semantic vector search → Baseline retrieval system

---

## Week 3 Focus: Implement Dense Retrieval System

Week 2 completed the foundation. Week 3 builds the core retrieval pipeline with dense embeddings and FAISS vector search.

---

## 1. Data Preparation (RAG-7) ✅

### Goal: Download and prepare MS MARCO dataset

### Tasks:
- [x] Extract 1000 queries from MS MARCO v2.1
- [x] Extract ~10,000 passages (10 per query)
- [x] Extract qrels for evaluation
- [x] Clean and preprocess text
- [x] Create train/validation/test splits

### Quick Start:

```bash
# Run the data extraction script
python extract_data.py
```

Expected output:
```
📊 Data Summary:
  ✅ Queries:   1000
  ✅ Passages:  9975
  ✅ Qrels:     446 queries with relevance
```

### Using the Data Loader:

```python
from src.data_loader import MSMarcoDataLoader

# Initialize
loader = MSMarcoDataLoader("data/raw")

# Extract from MS MARCO v2.1
loader.extract_from_v21(
    split="validation",
    max_queries=1000,
    max_passages_per_query=10
)

# Load processed data
loader.load_processed_data()

# Create splits
train, val, test = loader.create_splits()
```

---

## 2. Embedding Models (RAG-8) ✅

### Goal: Implement BGE-small and E5-base

### Tasks:
- [x] Load BGE-small model
- [x] Load E5-base model
- [x] Test embedding generation
- [x] Compare dimensions and speed
- [x] Test similarity computation

### Code:

```python
from src.embeddings import EmbeddingModel

# Load BGE-small (384 dimensions)
bge_model = EmbeddingModel("BAAI/bge-small-en-v1.5")

# Load E5-base (768 dimensions)
e5_model = EmbeddingModel("intfloat/e5-base-v2")

# Test encoding
query = "What causes headaches?"
query_emb = bge_model.encode(query, is_query=True)
print(f"Embedding shape: {query_emb.shape}")

# Compute similarity
text1 = "Headaches can be caused by stress."
text2 = "Climate change affects temperatures."
sim = bge_model.compute_similarity(
    bge_model.encode(text1),
    bge_model.encode(text2)
)
print(f"Similarity: {sim:.4f}")
```

### Model Comparison:

| Model | Dimensions | Speed | Use Case |
|-------|-------------|-------|----------|
| BGE-small | 384 | Fast | General retrieval |
| E5-base | 768 | Medium | Context-heavy queries |

---

## 3. Vector Store with FAISS (RAG-9) ✅

### Goal: Set up efficient similarity search

### Tasks:
- [x] Create Flat index (baseline)
- [x] Create IVF index (faster)
- [x] Test search functionality
- [x] Compare search speed

### Code:

```python
from src.vector_store import VectorStore
import numpy as np

# Create index
store = VectorStore(embedding_dim=384, index_type="flat")
store.create_index()

# Add embeddings
store.add_embeddings(embeddings, passage_ids, train=True)

# Search
query_embedding = model.encode(query)
results = store.search_by_id(query_embedding, k=10)
```

### Index Types:

| Type | Speed | Accuracy | Best For |
|------|-------|----------|----------|
| Flat | Slow | Exact | Baseline, small data |
| IVF | Fast | Near-exact | Medium-large data |
| HNSW | Very Fast | Near-exact | Production systems |

---

## 4. Retrieval Pipeline (RAG-10) ✅

### Goal: End-to-end retrieval system

### Tasks:
- [x] Create DenseRetriever class
- [x] Implement query encoding
- [x] Implement FAISS search
- [x] Return top-k passages
- [x] Test on sample queries

### Code:

```python
from src.retriever import DenseRetriever

# Initialize retriever
retriever = DenseRetriever("BAAI/bge-small-en-v1.5", index_type="flat")

# Index passages
retriever.index_passages(passages, batch_size=32)

# Retrieve
query = "What causes headaches?"
results = retriever.retrieve(query, k=5)

for r in results:
    print(f"{r['passage_id']}: {r['score']:.4f}")
    print(f"  {r['text'][:80]}...")
```

---

## 5. Evaluation Metrics (RAG-11) ✅

### Goal: Measure retrieval quality

### Tasks:
- [x] Implement Recall@K
- [x] Implement MRR
- [x] Implement Precision@K
- [x] Evaluate on validation set
- [x] Document baseline performance

### Code:

```python
from src.evaluation import evaluate_retriever

# Evaluate
metrics = evaluate_retriever(
    retriever,
    queries=val_queries,
    qrels=val_qrels,
    k_values=[1, 5, 10],
    verbose=True
)

print(f"Recall@10: {metrics['recall@10']:.4f}")
print(f"MRR: {metrics['mrr']:.4f}")
```

---

## Week 3 Deliverables ✅

### 1. Data ✅
- 1000 queries extracted
- ~10,000 passages extracted
- Qrels for evaluation
- Saved in `data/processed/`

### 2. Working Code ✅
- `src/data_loader.py` - Data loading
- `src/embeddings.py` - Embedding models (BGE-small, E5-base, BM25)
- `src/vector_store.py` - FAISS indices (Flat, IVF, HNSW)
- `src/retriever.py` - DenseRetriever and HybridRetriever classes
- `src/evaluation.py` - Evaluation metrics

### 3. Results to Document:
- Recall@K scores (K=1,5,10)
- MRR score
- Retrieval time benchmarks
- Embedding comparison (BGE vs E5)

### 4. Scripts ✅
- `extract_data.py` - Data extraction script
- `run_week3_tests.py` - Complete test suite

---

## Testing Checklist ✅

- [x] Data extraction successful
- [x] BGE-small model loads
- [x] E5-base model loads
- [x] Passages encode successfully
- [x] FAISS index creates
- [x] Search returns results
- [x] Evaluation metrics compute
- [x] Full pipeline runs end-to-end

---

## Quick Start Script

```bash
# 1. Extract data (if not already done)
python extract_data.py

# 2. Run full test suite
python run_week3_tests.py

# 3. Test specific modules
python run_week3_tests.py --module embeddings
python run_week3_tests.py --module vector
python run_week3_tests.py --module retriever
python run_week3_tests.py --module eval
```

---

## What's Next (Week 4)?

After Week 3, you'll have:
- ✅ Working dense retrieval system
- ✅ Baseline performance metrics
- ✅ Understanding of embeddings and FAISS

**Week 4** will add:
- BM25 sparse retrieval
- Hybrid dense + sparse retrieval
- Retrieval comparison experiments

---



Screenshots:


## References

- MS MARCO v2.1: `load_dataset("microsoft/ms_marco", "v2.1")`
- BGE-small: https://huggingface.co/BAAI/bge-small-en-v1.5
- E5-base: https://huggingface.co/intfloat/e5-base-v2
- FAISS: https://github.com/facebookresearch/faiss
