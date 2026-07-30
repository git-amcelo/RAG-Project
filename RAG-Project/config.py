"""
RAG Project Configuration
Central configuration for all RAG project components
"""

import os
from pathlib import Path


# =============================================================================
# Project Paths
# =============================================================================

# Root directory
PROJECT_ROOT = Path(__file__).parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

# Model directories
MODELS_DIR = PROJECT_ROOT / "models"
EMBEDDING_MODELS_DIR = MODELS_DIR / "embeddings"
INDICES_DIR = MODELS_DIR / "indices"

# Output directories
LOGS_DIR = PROJECT_ROOT / "logs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EMBEDDINGS_DIR,
                 MODELS_DIR, EMBEDDING_MODELS_DIR, INDICES_DIR,
                 LOGS_DIR, OUTPUTS_DIR, NOTEBOOKS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Dataset Configuration
# =============================================================================

# MS MARCO dataset
MS_MARCO_VERSION = "v2.1"
MS_MARCO_DATASET = "microsoft/ms_marco"

# Data extraction settings
MAX_QUERIES = 1000           # Number of queries to extract
MAX_PASSAGES_PER_QUERY = 10  # Passages per query
DEFAULT_SPLIT = "validation" # Dataset split to use

# Train/val/test split ratios
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15


# =============================================================================
# Embedding Model Configuration
# =============================================================================

# BGE-small model (384 dimensions, faster)
BGE_MODEL = "BAAI/bge-small-en-v1.5"
BGE_DIMENSION = 384

# E5-base model (768 dimensions, more accurate)
E5_MODEL = "intfloat/e5-base-v2"
E5_DIMENSION = 768

# Default model to use
DEFAULT_EMBEDDING_MODEL = BGE_MODEL
DEFAULT_EMBEDDING_DIM = BGE_DIMENSION

# Embedding settings
BATCH_SIZE = 32
NORMALIZE_EMBEDDINGS = True  # L2 normalization for similarity search
DEVICE = "cuda" if os.getenv("CUDA_AVAILABLE") == "1" else "cpu"


# =============================================================================
# FAISS Configuration
# =============================================================================

# Index type: "flat", "ivf", "hnsw", "pq"
DEFAULT_INDEX_TYPE = "flat"

# IVF (Inverted File) parameters
IVF_NLIST = 100  # Number of clusters

# HNSW (Hierarchical Navigable Small World) parameters
HNSW_M = 32  # Number of connections per node

# Search parameters
DEFAULT_TOP_K = 10  # Number of results to return


# =============================================================================
# Retrieval Configuration
# =============================================================================

# Retrieval parameters
TOP_K_RETRIEVAL = 10       # For standard retrieval
TOP_K_GENERATION = 5        # For RAG generation (fewer, more relevant)

# Hybrid retrieval (dense + sparse)
HYBRID_ALPHA = 0.5         # Weight for dense (1-alpha for sparse)

# Reranking
USE_RERANKING = False
RERANK_TOP_K = 20          # Rerank top N results


# =============================================================================
# Evaluation Configuration
# =============================================================================

# K values for Recall@K and Precision@K
K_VALUES = [1, 5, 10]

# Metrics to compute
METRICS = ["recall", "precision", "mrr", "map", "ndcg"]


# =============================================================================
# Logging Configuration
# =============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "rag_project.log"


# =============================================================================
# API Keys (load from environment)
# =============================================================================

# HuggingFace (for faster model downloads)
HF_TOKEN = os.getenv("HF_TOKEN", None)

# Anthropic API (for Claude)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", None)

# OpenAI API (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)


# =============================================================================
# Experiment Configuration
# =============================================================================

# Random seed for reproducibility
RANDOM_SEED = 42

# Verbose output
VERBOSE = True

# Save intermediate results
SAVE_INTERMEDIATE = True


# =============================================================================
# Helper Functions
# =============================================================================

def get_config_summary():
    """Return a summary of current configuration"""
    return {
        "embedding_model": DEFAULT_EMBEDDING_MODEL,
        "embedding_dim": DEFAULT_EMBEDDING_DIM,
        "index_type": DEFAULT_INDEX_TYPE,
        "top_k": TOP_K_RETRIEVAL,
        "device": DEVICE,
        "batch_size": BATCH_SIZE,
        "k_values": K_VALUES,
    }


def print_config():
    """Print current configuration"""
    print("="*60)
    print("  RAG Project Configuration")
    print("="*60)

    config = get_config_summary()

    print("\nModel Settings:")
    print(f"  Embedding Model: {config['embedding_model']}")
    print(f"  Embedding Dim: {config['embedding_dim']}")
    print(f"  Device: {config['device']}")
    print(f"  Batch Size: {config['batch_size']}")

    print("\nRetrieval Settings:")
    print(f"  Index Type: {config['index_type']}")
    print(f"  Top-K: {config['top_k']}")

    print("\nEvaluation Settings:")
    print(f"  K Values: {config['k_values']}")

    print("\nPaths:")
    print(f"  Data: {DATA_DIR}")
    print(f"  Models: {MODELS_DIR}")
    print(f"  Logs: {LOGS_DIR}")

    print("="*60 + "\n")


if __name__ == "__main__":
    print_config()
