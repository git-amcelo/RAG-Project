# RAG Project - Week 2 Tasks

## Phase 1: Understanding RAG Systems (Weeks 1-2)

> **Guideline Reference:** Week 1-2 - Understand RAG systems, Read papers, Prepare environment → Literature summary

---

## Week 2 Focus: Complete Literature Review & Finalize Environment

Week 1 covered the basics (environment setup, initial research). Week 2 completes the foundation phase with deeper understanding and documentation.

---

## 1. Literature Review Completion

### Tasks:
- [ ] Read Lewis et al. (2020) - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- [ ] Read 2-3 additional RAG papers (see suggestions below)
- [ ] Understand the RAG architecture components
- [ ] Document key findings from papers
- [ ] Identify research gaps/contribution opportunities

### Primary Paper to Read:

**Lewis et al. (2020) - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"**

Key sections to focus on:
- RAG architecture (retriever + reader)
- Training approaches (joint vs end-to-end)
- Evaluation metrics and benchmarks
- Comparison with standard language models

### Additional Paper Suggestions:

Choose 2-3 from:

| Paper | Focus | Why Read It? |
|-------|-------|--------------|
| ✅ Karpukhin et al. (2020) - "Dense Passage Retrieval" | DPR architecture | Understanding dense retrieval |
| ✅ Guu et al. (2020) - "REALM: Retrieval-Augmented Language Model Pre-Training" | Pre-training with retrieval | Advanced RAG techniques |


---

## 2. Literature Summary Document

### Tasks:
- [ ] Create `LITERATURE_SUMMARY.md`
- [ ] Summarize each paper (1-2 paragraphs each)
- [ ] Create comparison table of methods
- [ ] Identify key insights for your implementation
- [ ] Note potential research contributions

### Literature Summary Template:

```markdown
# Literature Summary - RAG Project

## Paper Summaries

### 1. Lewis et al. (2020) - RAG

**Key Idea:** Combine pre-trained parametric and non-parametric memory for language generation.

**Architecture:**
- Retriever: DPR (dense passage retrieval)
- Generator: BART/T5 seq2seq model
- Two variants: RAG-Sequence (joint), RAG-Token (independent)

**Findings:**
- Outperforms standard language models on knowledge-intensive tasks
- End-to-end training is most effective
- Retrieval improves factuality

**Relevance to Our Project:**
- Base architecture for our implementation
- Evaluation metrics to use

### 2. [Additional Paper]

[Same format]

---

## Method Comparison

| Method | Retrieval | Generation | Training | Key Strength |
|--------|-----------|------------|----------|--------------|
| RAG | DPR | BART | End-to-end | Balanced performance |
| DPR | Dense | N/A | Pre-trained | Strong retrieval |
| REALM | MLM + Retrieval | BERT | Pre-training | Integrated pre-training |

---

## Key Insights for Implementation

1. **Architecture Choice:**
   - Use separate retriever + generator (easier to debug)
   - Consider hybrid retrieval (dense + sparse)

2. **Training Strategy:**
   - Start with pre-trained components
   - Fine-tune if time permits

3. **Evaluation:**
   - Use Recall@K, MRR for retrieval
   - Use exact match/F1 for QA

---

## Potential Research Contributions

Based on literature review, potential contributions:
- [ ] Hybrid retrieval comparison
- [ ] Query expansion techniques
- [ ] Context compression methods
- [ ] Reranking model integration
```

---

## 3. Environment Finalization

### Tasks:
- [ ] Verify all packages installed correctly
- [ ] Test GPU availability (if applicable)
- [ ] Create `environment_test.py` script
- [ ] Document any issues/fixes
- [ ] Set up project logging

### Environment Checklist:

```python
# environment_test.py - Run to verify setup

def test_environment():
    print("Testing RAG Project Environment...")

    # 1. Python version
    import sys
    print(f"✓ Python: {sys.version.split()[0]}")

    # 2. Core packages
    import torch
    print(f"✓ PyTorch: {torch.__version__}")
    print(f"✓ CUDA available: {torch.cuda.is_available()}")

    import transformers
    print(f"✓ Transformers: {transformers.__version__}")

    from sentence_transformers import SentenceTransformer
    print(f"✓ SentenceTransformers: installed")

    import faiss
    print(f"✓ FAISS: {faiss.__version__}")

    import datasets
    print(f"✓ Datasets: {datasets.__version__}")

    # 3. Test embedding model loading
    try:
        model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        print(f"✓ BGE-small model loads correctly")
    except Exception as e:
        print(f"✗ BGE-small loading failed: {e}")

    # 4. Test dataset access
    try:
        from datasets import load_dataset
        ds = load_dataset('microsoft/ms_marco', 'v2.1', split='validation[0:1]')
        print(f"✓ MS MARCO v2.1 accessible")
    except Exception as e:
        print(f"✗ MS MARCO access failed: {e}")

    print("\nEnvironment test complete!")

if __name__ == "__main__":
    test_environment()
```

### Required Packages Verification:

```bash
# Verify all packages are installed
pip list | grep -E "(torch|transformers|sentence|faiss|datasets|anthropic|langchain)"
```

Expected output:
```
anthropic               # For Claude API
faiss-cpu               # Vector similarity search
langchain               # LLM framework
sentence-transformers   # Embedding models
torch                   # Deep learning
transformers            # HuggingFace models
datasets                # MS MARCO dataset
```

---

## 4. Project Structure Setup

### Tasks:
- [ ] Create all necessary directories
- [ ] Set up `.env` file for API keys
- [ ] Create `config.py` for configuration
- [ ] Set up logging configuration
- [ ] Create README.md updates

### Directory Structure:

```
RAG Project/
├── data/
│   ├── raw/              # Downloaded datasets
│   ├── processed/        # Processed data
│   └── embeddings/       # Saved embeddings
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration
│   ├── utils.py         # Utility functions
│   ├── logger.py        # Logging setup
├── models/
│   ├── embeddings/      # Downloaded embedding models
│   └── indices/         # FAISS indices
├── notebooks/
│   ├── 01_literature_review.ipynb
│   ├── 02_data_exploration.ipynb
│   └── 03_experiments.ipynb
├── logs/                # Application logs
├── outputs/             # Experiment results
├── WEEK_1_TASKS.md
├── WEEK_2_TASKS.md
├── WEEK_3_TASKS.md
├── LITERATURE_SUMMARY.md
├── requirements.txt
├── .env
└── README.md
```

### Configuration Template (`config.py`):

```python
"""RAG Project Configuration"""

# Data paths
DATA_DIR = "data"
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
EMBEDDINGS_DIR = "data/embeddings"

# Model paths
MODELS_DIR = "models"
EMBEDDING_MODELS_DIR = "models/embeddings"
INDICES_DIR = "models/indices"

# Embedding models
BGE_MODEL = "BAAI/bge-small-en-v1.5"
E5_MODEL = "intfloat/e5-base-v2"

# FAISS configuration
INDEX_TYPE = "flat"  # "flat", "ivf", "hnsw"
NLIST = 100  # For IVF
M_HNSW = 32  # For HNSW

# Retrieval parameters
TOP_K = 10  # Number of passages to retrieve

# Evaluation
K_VALUES = [1, 5, 10]  # For Recall@K

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/rag_project.log"
```

### Environment Variables (`.env`):

```bash
# HuggingFace (optional, for faster downloads)
HF_TOKEN=your_token_here

# Anthropic API (for generation)
ANTHROPIC_API_KEY=your_key_here

# OpenAI API (optional)
OPENAI_API_KEY=your_key_here
```

---

## 5. Understanding Documentation

### Tasks:
- [ ] Document RAG architecture understanding
- [ ] Create diagrams showing data flow
- [ ] Document evaluation metrics
- [ ] Create glossary of terms

### RAG Architecture Understanding:

**Components to Understand:**

```
Query → [Embedding Model] → Query Vector
                                    ↓
Passages → [Embedding Model] → Passage Embeddings → [FAISS Index]
                                                                    ↓
Query Vector ←──────────── [Similarity Search] ←───────────────┘
                                                    ↓
                                          Top-K Passages
                                                    ↓
                                         [LLM Generator]
                                                    ↓
                                               Final Answer
```

**Key Concepts to Master:**

| Concept | Description | Why Important |
|---------|-------------|---------------|
| Embeddings | Text → Vector representations | Semantic similarity search |
| FAISS | Fast similarity search library | Efficient retrieval |
| Dense Retrieval | Vector-based search | Captures semantic meaning |
| Sparse Retrieval | Keyword-based (BM25) | Exact matching |
| Hybrid Retrieval | Combine dense + sparse | Best of both worlds |
| Reranking | Reorder retrieved results | Improve precision |
| Recall@K | % relevant docs in top K | Retrieval coverage metric |
| MRR | 1/rank of first relevant | Early ranking quality |

---

## Week 2 Deliverables

### Required:

1. **`LITERATURE_SUMMARY.md`**
   - Paper summaries (Lewis et al. + 2-3 others)
   - Method comparison table
   - Key insights
   - Potential contributions

2. **`environment_test.py`**
   - Script that verifies all dependencies
   - Tests model loading
   - Tests dataset access

3. **`config.py`**
   - All configuration parameters
   - Path definitions
   - Model settings

4. **Updated Project Structure**
   - All directories created
   - `.env` file set up
   - Logging configured

5. **`WEEK_2_NOTES.md`** (optional but recommended)
   - Personal notes on RAG understanding
   - Questions for further research
   - Implementation ideas

---

## Progress Checklist

- [ ] Literature review complete (3-4 papers read)
- [ ] Literature summary document created
- [ ] Environment fully verified
- [ ] Project structure finalized
- [ ] Configuration files created
- [ ] Understanding documented

---

## What's Next (Week 3)?

After Week 2, you'll have:
- ✅ Solid understanding of RAG systems
- ✅ Literature review documented
- ✅ Environment fully ready
- ✅ Clear implementation plan

**Week 3** will then focus on building the retrieval pipeline with the code already prepared in `src/`.

---

## References

**Primary Papers:**
- Lewis et al. (2020): https://arxiv.org/abs/2005.11401
- Karpukhin et al. (2020): https://arxiv.org/abs/2004.04906

**Resources:**
- HuggingFace Models: https://huggingface.co/
- FAISS Documentation: https://github.com/facebookresearch/faiss
- SentenceTransformers: https://www.sbert.net/
