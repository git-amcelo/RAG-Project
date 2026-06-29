# Model Comparison Implementation Guide

## 🎯 Overview

This guide explains how to implement and use the BGE-small vs E5-base model comparison as part of Weeks 4-5, using the same Week 3 benchmark for consistent evaluation.

## 📊 Models to Compare

### BGE-small (BAAI/bge-small-en-v1.5)
- **Dimensions**: 384
- **Speed**: Fast (~30% faster than E5-base)
- **Storage**: Small (50% less storage)
- **Accuracy**: Good (Week 3: Recall@5 ≈ 0.75)
- **Best For**: Real-time applications, resource-constrained environments

### E5-base (intfloat/e5-base-v2)
- **Dimensions**: 768
- **Speed**: Medium
- **Storage**: Medium
- **Accuracy**: Better (Week 3: Recall@5 ≈ 0.78)
- **Best For**: Maximum accuracy, complex queries, batch processing

## 🚀 Quick Start

### 1. Run Model Comparison
```bash
# Compare both models
python benchmarks/week3_reconstruction.py

# Test BGE-small only
python benchmarks/week3_reconstruction.py --model bge

# Test E5-base only
python benchmarks/week3_reconstruction.py --model e5

# Custom query count
python benchmarks/week3_reconstruction.py --queries 50
```

### 2. Expected Output
```
─ Week 3 Benchmark Results ──────────────────────────────

┌──────────────────────────────────────────────────────────┐
│            BGE-small vs E5-base Comparison                │
├──────────────────────────────────────────────────────────┤
│ Metric          │ BGE-small   │ E5-base     │ Difference │
├──────────────────────────────────────────────────────────┤
│ Embedding Dim   │ 384         │ 768         │ +384 dims  │
│ Recall@5        │ 0.7500      │ 0.7850      │ +3.5%      │
│ MRR             │ 0.6850      │ 0.7200      │ +5.1%      │
│ MAP             │ 0.7200      │ 0.7500      │ +4.2%      │
└──────────────────────────────────────────────────────────┘
```

## 📋 Implementation Steps

### Step 1: Recreate Week 3 Benchmark
**File**: `benchmarks/week3_reconstruction.py`
- Load MS MARCO data (same as Week 3)
- Test both BGE-small and E5-base
- Use identical evaluation metrics
- Compare performance and accuracy

### Step 2: Integrate into Chat Application
**Backend**: Add model selection to RAG pipeline
```python
# src/model_config.py
class ModelSelector:
    def recommend_model(self, query_complexity, num_documents):
        if query_complexity > 0.7 and num_documents < 1000:
            return "intfloat/e5-base-v2"  # E5 for complex queries
        else:
            return "BAAI/bge-small-en-v1.5"  # BGE for speed
```

**Frontend**: Add model selector component
```typescript
// frontend/src/components/ModelSelector.tsx
interface ModelOption {
  id: string;
  name: string;
  description: string;
  dimensions: number;
  speed: "fast" | "medium";
  accuracy: "good" | "better";
}
```

### Step 3: Display Results to Users
- Show model comparison in chat interface
- Provide recommendations based on query type
- Display performance metrics
- Allow manual model selection

## 🎨 UI Components

### Model Selector Component
**Location**: `frontend/src/components/ModelSelector.tsx`

Features:
- Dropdown with model options
- Performance indicators
- Automatic recommendation
- Per-query statistics

### Model Comparison Display
**Location**: `frontend/src/components/ModelComparison.tsx`

Features:
- Side-by-side metrics
- Performance charts
- Accuracy vs speed trade-offs
- Storage comparison

## 📈 Usage in Application

### Backend Integration
```python
# In RAG pipeline
from src.model_config import ModelSelector

model_selector = ModelSelector()

# Automatic model selection
model_name = model_selector.recommend_model(
    query_complexity=0.8,
    num_documents=len(documents)
)

# Manual model selection
model_name = user_preference  # From frontend
retriever = DenseRetriever(model_name)
```

### Frontend Integration
```typescript
// In chat interface
const [selectedModel, setSelectedModel] = useState('bge-small');

// Model selection
<ModelSelector
  value={selectedModel}
  onChange={setSelectedModel}
  showRecommendations={true}
/>

// Display comparison
<ModelComparison
  results={modelComparisonResults}
  currentModel={selectedModel}
/>
```

## 🧪 Testing

### Unit Tests
```bash
# Test model comparison logic
pytest tests/test_model_comparison.py

# Test model selector
pytest tests/test_model_selector.py
```

### Integration Tests
```bash
# Test end-to-end with both models
pytest tests/integration/test_both_models.py

# Test UI model selection
pytest tests/integration/test_model_ui.py
```

### Performance Tests
```bash
# Compare encoding speed
python benchmarks/test_encoding_speed.py

# Compare retrieval speed
python benchmarks/test_retrieval_speed.py

# Compare storage requirements
python benchmarks/test_storage_usage.py
```

## 📊 Expected Results

Based on Week 3 benchmark reconstruction:

```
Performance Summary:
┌─────────────┬────────────┬────────────┬────────────┐
│  Model      │   Speed    │  Accuracy   │  Storage    │
├─────────────┼────────────┼────────────┼────────────┤
│ BGE-small   │ 1.0x (ref) │ 0.750       │ 1.0x (ref)  │
├─────────────┼────────────┼────────────┼────────────┤
│ E5-base     │ 0.7x       │ 0.785       │ 2.0x        │
└─────────────┴────────────┴────────────┴────────────┘

Recommendations:
• Real-time chat: BGE-small (speed priority)
• Document analysis: E5-base (accuracy priority)
• Resource-limited: BGE-small (storage priority)
• Complex queries: E5-base (quality priority)
```

## 🔧 Configuration

### Backend Configuration
```python
# config.py
EMBEDDING_MODELS = {
    "bge-small": {
        "path": "BAAI/bge-small-en-v1.5",
        "dimensions": 384,
        "use_case": "general"
    },
    "e5-base": {
        "path": "intfloat/e5-base-v2",
        "dimensions": 768,
        "use_case": "complex"
    }
}

DEFAULT_MODEL = "bge-small"
MODEL_AUTO_SELECTION = True
```

### Frontend Configuration
```typescript
// frontend/src/config/models.ts
export const MODEL_OPTIONS = [
  {
    id: 'bge-small',
    name: 'BGE-small',
    dimensions: 384,
    speed: 'fast',
    accuracy: 'good',
    description: 'Fast and efficient for general queries'
  },
  {
    id: 'e5-base',
    name: 'E5-base',
    dimensions: 768,
    speed: 'medium',
    accuracy: 'better',
    description: 'Higher accuracy for complex queries'
  }
];
```

## 📝 Documentation

### User-Facing Documentation
- Model selection guide
- Performance comparison
- Recommendation tips
- Use case examples

### Developer Documentation
- Integration instructions
- API reference
- Testing procedures
- Performance optimization

## 🎯 Success Criteria

- ✅ Both models tested on Week 3 benchmark
- ✅ Performance metrics documented
- ✅ UI components for model selection
- ✅ Automatic model recommendation
- ✅ User documentation complete
- ✅ Integration with chat application
- ✅ Performance monitoring implemented

---

**Ready to implement model comparison in your RAG application!**