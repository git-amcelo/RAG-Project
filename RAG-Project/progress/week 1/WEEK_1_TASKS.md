# RAG Project - Week 1 Tasks

## Tasks Overview

### 1. Environment Setup (RAG-1)
- [ ✅ ] Install Python 3.9+
- [ ✅ ] Create virtual environment
- [ ✅ ] Install required packages
- [ ✅ ] Verify installation

---

## 2. Literature Review (RAG-2)

### What is RAG?
RAG (Retrieval-Augmented Generation) is an AI technique that combines two things:
- **Retrieval:** Searching through a large collection of documents to find relevant information
- **Generation:** Using an AI model (like GPT) to generate answers based on the retrieved information

### Why does it matter?
Traditional AI models have two problems:
1. They only know what they were trained on (they can't access new information)
2. They sometimes "hallucinate" or make things up

RAG solves both by letting the AI search through real documents before answering, so it's:
- More accurate (uses real data)
- Up-to-date (can add new documents anytime)
- More transparent (you can see what sources it used)

### What the Lewis et al. (2020) paper covers:
- The original RAG architecture
- How retrieval and generation work together
- Performance comparisons with other methods
- Key ideas like indexing, retrieval parameters, and training approaches

### What you'll find in other RAG papers:
- Improvements to the original design
- Different retrieval strategies
- Better ways to combine search and generation
- Performance benchmarks

---

## 3. Dataset Selection (RAG-3)

### What is MS MARCO?
MS MARCO (Microsoft Machine Reading Comprehension) is a large, publicly available dataset used for:
- Question answering
- Document retrieval
- Search engine tasks

It contains:
- ~500,000 real questions from Bing users
- ~8 million passages (documents)
- Human-written answers

### Data structure you'll encounter:
- **Questions:** The queries users ask (e.g., "What causes headaches?")
- **Passages:** The text chunks that might contain answers
- **Relevance labels:** Which passages are relevant to which questions
- **Answers:** The correct responses (for training/testing)

### Why document the format?
Before coding, you need to know:
- File formats (JSON, TSV, etc.)
- Field names (what keys to use)
- Data size (how much RAM/storage needed)
- How to load and process it efficiently

---

## 4. Embedding Models Research (RAG-4)

### What are embeddings?
Embeddings convert text into lists of numbers (vectors) that represent meaning:
- "dog" and "puppy" → similar vectors
- "car" and "banana" → very different vectors

This allows computers to understand semantic similarity (meaning) instead of just matching words.

### BGE-small:
- **Full name:** BAAI General Embedding (small version)
- **Strength:** Good balance between speed and accuracy
- **Use case:** When you have moderate resources but still want quality results
- **Size:** Smaller and faster than larger models

### E5-base:
- **Full name:** Embeddings from Bidirectional Encoder Representations Transformers
- **Strength:** Good at understanding context in sentences
- **Use case:** General-purpose tasks where context matters
- **Size:** Medium-sized model

### SentenceTransformers:
- A framework/library that makes it easy to use embedding models
- Pre-trained models ready to use
- Can fine-tune models for specific tasks

### Comparison points to look for:
- **Accuracy:** How well they capture meaning
- **Speed:** How fast they process text
- **Size:** How much memory/processing power they need
- **Language support:** Which languages they work with

---

## 5. Vector Database Understanding (RAG-5)

### What is FAISS?
FAISS (Facebook AI Similarity Search) is a library for fast similarity search:
- Given a query vector, find the most similar vectors in a dataset
- Handles millions or billions of vectors efficiently
- Developed by Meta (Facebook)

### Why do you need it?
Once you convert all your documents to embeddings (vectors), you need to:
- Store them
- Search through them quickly
- Find the most similar ones to a query

Without FAISS or similar tools, searching through millions of vectors would be very slow.

### Indexing types:
- **Flat Index:** Exact search, slower but accurate (good for small datasets)
- **IVF (Inverted File Index):** Partitions data, faster, slight accuracy trade-off
- **HNSW (Hierarchical Navigable Small World):** Graph-based, very fast with good accuracy
- **PQ (Product Quantization):** Compresses vectors, saves memory

### Query types:
- **KNN (K-Nearest Neighbors):** Find the K most similar vectors
- **Range search:** Find all vectors within a certain similarity threshold
- **Approximate search:** Fast but may miss some results (usually acceptable)

---

## 6. Literature Summary (RAG-6)

### What to include:

**Key Concepts:**
- RAG architecture (how it works at a high level)
- Why RAG is better than just using an AI model alone
- Trade-offs (speed vs. accuracy, cost vs. performance)
- Common challenges and solutions

**System Architecture:**
- The components: documents → embeddings → vector store → retrieval → generation
- How data flows through the system
- Where embeddings, FAISS, and the AI model fit together

---

## Quick Mental Model

Think of RAG like a smart student taking an open-book test:

1. **Dataset** = The textbook with all the answers
2. **Embeddings** = Indexing the textbook so you can find relevant pages quickly
3. **FAISS** = A fast way to flip to the right pages
4. **RAG System** = The student who searches the textbook and then writes the answer
5. **Literature Review** = Understanding how other students have done this before

---

## Bottom Line
We are building a system that can "search first, then answer" — combining the power of a search engine with an AI's ability to generate natural responses.

# Youtube Video watched about RAG
https://www.youtube.com/watch?v=Ty8gcCKuwNI