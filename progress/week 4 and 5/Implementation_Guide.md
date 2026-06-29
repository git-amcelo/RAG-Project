# Weeks 4-5 Implementation Guide

## 🎯 Overview

This guide provides step-by-step instructions for implementing the complete chat-based RAG application with document upload, processing, and LLM integration.

## 📋 Prerequisites Check

### Current System Status
- ✅ Week 3 completed (Data pipeline, embeddings, retrieval, evaluation)
- ✅ Existing files: `src/data_loader.py`, `embeddings.py`, `vector_store.py`, `retriever.py`
- ✅ ZAI API key available for LLM integration
- ✅ Design reference: `site_designer.md`

### Required Dependencies
```bash
# Backend additions
pip install fastapi uvicorn python-multipart pydantic pyPDF2 pdfplumber python-docx langchain langchain-community

# Frontend additions
npm create vite@latest frontend -- --template react-ts
npm install @tailwindcss/react axios zustand
```

## 🚀 Week 4 Implementation (Days 1-5)

### Day 1-2: Document Processing Foundation

#### Step 1: Create Document Processor
```bash
# Create file structure
mkdir -p src/utils src/api data/{uploads,documents}
touch src/document_processor.py src/utils/text_processing.py
```

#### Step 2: Implement PDF/DOCX Processing
**File**: `src/document_processor.py`

Key Components:
- `DocumentProcessor` class
- PDF extraction with PyPDF2/pdfplumber
- Word document processing with python-docx
- Text chunking with LangChain
- Metadata extraction

#### Step 3: Test Document Processing
```python
# Create test file
touch test_document_processing.py

# Test with sample PDF/DOCX
python test_document_processing.py
```

### Day 3: LangChain RAG Integration & Model Comparison

#### Step 1: Create RAG Chain Implementation
```bash
touch src/rag_chain.py src/utils/zai_client.py src/prompts.py src/model_comparison.py
```

#### Step 2: Implement LangChain Components
**File**: `src/rag_chain.py`
- RetrievalQA chain
- Conversational memory
- Custom prompt templates
- Document-aware retrieval
- Model selection logic (BGE-small vs E5-base)

#### Step 3: Model Comparison Implementation
**File**: `src/model_comparison.py`
```python
# Recreate Week 3 benchmark for both models
# Compare BGE-small vs E5-base on same test set
# Metrics: Recall@K, MRR, MAP
# Speed comparison
# Storage comparison
```

#### Step 4: ZAI API Integration
**File**: `src/utils/zai_client.py`
- ZAI API wrapper
- Model configuration
- Error handling and retry logic

### Day 4-5: FastAPI Backend Development

#### Step 1: Create API Structure
```bash
mkdir -p src/api
touch src/api/{main.py,routes.py,schemas.py,middleware.py}
```

#### Step 2: Implement FastAPI Application
**File**: `src/api/main.py`
- FastAPI app initialization
- CORS middleware
- Exception handlers

#### Step 3: Create API Endpoints
**File**: `src/api/routes.py`

Endpoints to implement:
1. `POST /upload` - Document upload and processing
2. `POST /chat` - Chat with streaming
3. `GET /documents` - List documents
4. `DELETE /documents/{id}` - Remove document
5. `GET /health` - Health check

#### Step 4: Test API
```bash
# Start server
uvicorn src.api.main:app --reload --port 8000

# Test endpoints
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/upload -F "file=@test.pdf"
```

## 🎨 Week 5 Implementation (Days 1-5)

### Day 1-2: React Frontend Setup

#### Step 1: Create React Project
```bash
# Create frontend directory
cd project-root
npm create vite@latest frontend -- --template react-ts

# Install dependencies
cd frontend
npm install @tailwindcss/react axios zustand react-markdown
npm install -D @types/react @types/react-dom
```

#### Step 2: Setup Project Structure
```bash
# Create directory structure
mkdir -p frontend/src/{components,hooks,services,types,styles,utils}
mkdir -p frontend/tests/{e2e,integration}
```

#### Step 3: Configure Tailwind CSS
```bash
# Initialize Tailwind
npx tailwindcss init -p
```

### Day 3: Core Chat Components

#### Step 1: Create Chat Interface
**File**: `frontend/src/components/ChatInterface.tsx`

Components to build:
- `ChatInterface` - Main container
- `MessageList` - Message display
- `MessageInput` - User input
- `TypingIndicator` - Real-time status

#### Step 2: Create Document Management
**File**: `frontend/src/components/DocumentUploader.tsx`
**File**: `frontend/src/components/DocumentList.tsx`

Features:
- Drag-drop upload
- File validation
- Processing status
- Document removal

### Day 4: API Integration

#### Step 1: Create API Client
**File**: `frontend/src/services/api.ts`

```typescript
// API client configuration
- Base URL setup
- Request/response interceptors
- Error handling
- Response parsing
```

#### Step 2: Implement Chat Service
**File**: `frontend/src/services/chatApi.ts`

```typescript
// Chat endpoints
- sendMessage(streaming)
- getChatHistory()
- clearChat()
```

#### Step 3: Implement Document Service
**File**: `frontend/src/services/documentApi.ts`

```typescript
// Document endpoints
- uploadDocument()
- getDocuments()
- deleteDocument()
```

### Day 5: Integration & Testing

#### Step 1: State Management
**File**: `frontend/src/hooks/useChat.ts`
**File**: `frontend/src/hooks/useDocuments.ts`

```typescript
// Custom hooks for:
- Chat state management
- Document state management
- API error handling
- Loading states
```

#### Step 2: E2E Testing
```bash
# Install Playwright
npm install -D @playwright/test

# Create tests
touch frontend/tests/e2e/chat.spec.ts
touch frontend/tests/e2e/upload.spec.ts

# Run tests
npx playwright test
```

#### Step 3: Performance Testing
```bash
# Test document upload performance
# Test chat response times
# Test concurrent users
# Test memory usage
```

## 🔧 Configuration Files

### Backend Configuration

**File**: `config.py` (Update existing)
```python
# Add API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:5173"]

# ZAI API Configuration
ZAI_API_KEY = os.getenv("ZAI_API_KEY")
ZAI_MODEL = "model-name"
ZAI_TEMPERATURE = 0.7
ZAI_MAX_TOKENS = 2048
```

### Frontend Configuration

**File**: `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

## 📊 Testing Strategy

### Model Comparison Testing (Critical!)
```bash
# Recreate Week 3 benchmark with both models
python benchmarks/week3_reconstruction.py

# Test BGE-small performance
python test_model_comparison.py --model BAAI/bge-small-en-v1.5

# Test E5-base performance  
python test_model_comparison.py --model intfloat/e5-base-v2

# Compare both models
python test_model_comparison.py --compare

# Expected results format:
# BGE-small: Recall@5=0.75, MRR=0.68, MAP=0.72
# E5-base: Recall@5=0.78, MRR=0.72, MAP=0.75
```

### Backend Testing
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/

# Model comparison tests
pytest tests/model_comparison/
```

### Frontend Testing
```bash
# Component tests
npm run test

# E2E tests
npx playwright test

# Performance tests
npm run test:performance
```

## 🚦 Deployment

### Backend Deployment
```bash
# Build Docker image
docker build -t rag-backend .

# Run container
docker run -p 8000:8000 rag-backend
```

### Frontend Deployment
```bash
# Build production
npm run build

# Deploy to Vercel
vercel deploy
```

## 📝 Progress Tracking

### Daily Checklist
- [ ] Code implemented
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Team communication

### Weekly Checklist
- [ ] All tickets completed
- [ ] End-to-end testing done
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Demo prepared

## 🐛 Common Issues & Solutions

### Backend Issues
**Issue**: PDF processing fails
```bash
# Solution: Check PDF encoding
# Add error handling for corrupted PDFs
```

**Issue**: Memory overload with large documents
```bash
# Solution: Implement chunking
# Add file size limits
```

### Frontend Issues
**Issue**: CORS errors
```bash
# Solution: Update CORS origins in FastAPI
# Check API base URL in frontend
```

**Issue**: Streaming not working
```bash
# Solution: Check SSE implementation
# Verify async handling in both frontend/backend
```

## 📚 Resources

### Documentation Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [React TypeScript Guide](https://react-typescript-cheatsheet.netlify.app/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### API References
- [ZAI API Documentation](https://docs.zai.ai/)
- [OpenAI API (Alternative)](https://platform.openai.com/docs)

## 🎯 Success Criteria

### Week 4 Success Criteria
- ✅ Document processing working for PDF/DOCX
- ✅ LangChain RAG pipeline functional
- ✅ FastAPI backend with all endpoints
- ✅ ZAI API integration working
- ✅ All backend tests passing

### Week 5 Success Criteria
- ✅ React chat interface functional
- ✅ Document upload UI working
- ✅ API integration complete
- ✅ E2E tests passing
- ✅ Deployment configuration ready
- ✅ Documentation complete

## 📞 Team Coordination

### Daily Standups (15 minutes)
- Yesterday's accomplishments
- Today's plan
- Blockers and dependencies

### Weekly Demo (30 minutes)
- Completed features
- Live demonstration
- User testing feedback
- Next week planning

### Code Review Process
1. Create pull request
2. Automated tests must pass
3. At least one team member review
4. Address feedback
5. Merge to main branch

---

**Ready to start implementation! Begin with Week 4, Day 1: Document Processing Foundation**