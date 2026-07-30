# RAG Project - Foundation-Model-Based Retrieval-Augmented Generation

## Project Overview
Building a practical RAG system combining LLMs with external knowledge retrieval techniques.

## Tech Stack
- **Embedding Models**: BGE-small, E5-base, SentenceTransformers
- **Vector Database**: FAISS
- **Framework**: LangChain
- **LLM**: Anthropic Claude / OpenAI
- **Retrieval**: Dense + BM25 (Hybrid)

## Project Structure
```
.
├── data/                    # Datasets and documents
│   ├── raw/                # Original datasets
│   └── processed/          # Processed/cleaned data
├── src/                    # Source code
│   ├── retrieval/          # Retrieval components
│   ├── generation/         # LLM generation
│   ├── evaluation/         # Metrics and evaluation
│   └── utils/              # Helper utilities
├── notebooks/              # Jupyter notebooks for experiments
├── checkpoints/            # Saved models and indices
├── results/                # Experimental results and visualizations
├── docs/                   # Literature summaries and documentation
└── reports/                # Final reports and presentations
```

## Phase Progress
- [ ] Phase 1: Week 1-2 - Understand RAG systems
- [ ] Phase 2: Week 3 - Build retrieval pipeline
- [ ] Phase 3: Week 4 - Compare embeddings
- [ ] Phase 4: Week 5 - LLM integration
- [ ] Phase 5: Week 6 - Hybrid retrieval
- [ ] Phase 6: Week 7 - Optimization
- [ ] Phase 7: Week 8 - Evaluation
- [ ] Phase 8: Week 9 - Analysis
- [ ] Phase 9: Week 10 - Final submission