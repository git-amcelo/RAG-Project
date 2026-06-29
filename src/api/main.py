"""
FastAPI Backend for RAG Chat Application
Weeks 4-5: REST API with async support

Implements:
- Document upload and processing
- Chat interactions with streaming
- Document management
- Model selection and comparison
- Health monitoring
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uvicorn
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.document_processor import DocumentProcessor
from src.rag_chain import RAGChain, ChainConfig
from src.model_config import ModelType, ModelSelector


# Pydantic models for API
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    use_memory: bool = Field(True, description="Use conversation memory")
    model_preference: Optional[str] = Field(None, description="Model preference (bge-small or e5-base)")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str
    question: str
    sources: List[Dict[str, Any]]
    processing_time: float
    model_used: str
    num_documents_retrieved: int

class DocumentInfo(BaseModel):
    """Document information model"""
    document_id: str
    file_name: str
    file_type: str
    num_chunks: int
    processed_at: str
    file_size: int

class ModelComparisonResponse(BaseModel):
    """Model comparison response"""
    model1_name: str
    model2_name: str
    dimensions_comparison: Dict[str, int]
    performance_comparison: Dict[str, float]
    recommendations: Dict[str, List[str]]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    models_loaded: List[str]
    documents_processed: int
    uptime: str


# Initialize FastAPI app
app = FastAPI(
    title="RAG Chat API",
    description="Retrieval Augmented Generation Chat API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
document_processor = None
rag_chains = {}  # Store multiple RAG chains for different models
model_selector = None
active_model = ModelType.BGE_SMALL

# API startup
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global document_processor, rag_chains, model_selector, active_model

    print("\n" + "="*60)
    print("  RAG Chat API Starting Up")
    print("="*60)

    # Initialize document processor
    document_processor = DocumentProcessor()
    
    # Clear old documents on startup for a clean slate
    print("🧹 Clearing old documents...")
    import shutil
    for d in [document_processor.upload_dir, document_processor.processed_dir]:
        if d.exists():
            for item in d.glob("*"):
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"Failed to delete {item}: {e}")
                    
    print("✓ Document processor initialized (Clean Slate)")

    # Initialize model selector
    model_selector = ModelSelector()
    print("✓ Model selector initialized")

    # Initialize default RAG chain
    config = ChainConfig(model_type=active_model)
    rag_chains[active_model] = RAGChain(config)
    print(f"✓ RAG chain initialized with {active_model.value}")

    # Initialize E5-base chain as well
    e5_config = ChainConfig(model_type=ModelType.E5_BASE)
    rag_chains[ModelType.E5_BASE] = RAGChain(e5_config)
    print(f"✓ RAG chain initialized with {ModelType.E5_BASE.value}")

    print("="*60)
    print("  API Ready to Accept Requests")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n🔄 API Shutting down...")


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns API status and statistics
    """
    import time

    # Get statistics
    documents = document_processor.list_processed_documents() if document_processor else []
    models_loaded = list(rag_chains.keys())

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded=[model.value for model in models_loaded],
        documents_processed=len(documents),
        uptime=f"{int(time.time())}s"  # Simplified uptime
    )


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document

    Supports PDF and DOCX files
    """
    if not document_processor:
        raise HTTPException(status_code=503, detail="Service not ready")

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.docx']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Use PDF or DOCX"
        )

    try:
        # Save uploaded file
        upload_path = document_processor.upload_dir / file.filename
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process document
        result = document_processor.process_document(str(upload_path))

        if not result["success"]:
            raise HTTPException(status_code=422, detail=result["error"])

        # Save processed document
        document_processor.save_processed_document(result)

        # Index in all RAG chains
        chunks = result["chunks"]
        for model_type, rag_chain in rag_chains.items():
            try:
                rag_chain.index_documents(chunks)
            except Exception as e:
                print(f"Warning: Could not index in {model_type.value}: {e}")

        return {
            "success": True,
            "document_id": result["document_id"],
            "file_name": result["file_name"],
            "num_chunks": result["num_chunks"],
            "processing_time": result["processing_time"],
            "message": "Document uploaded and processed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for question answering

    Supports conversation memory and model selection
    """
    # Get model to use
    model_to_use = active_model

    if request.model_preference:
        if request.model_preference == "e5-base":
            model_to_use = ModelType.E5_BASE
        elif request.model_preference == "bge-small":
            model_to_use = ModelType.BGE_SMALL

    # Get RAG chain
    if model_to_use not in rag_chains:
        raise HTTPException(status_code=503, detail=f"Model {model_to_use.value} not available")

    rag_chain = rag_chains[model_to_use]

    try:
        # Get response
        result = rag_chain.answer_question(
            request.message,
            use_memory=request.use_memory
        )

        return ChatResponse(
            answer=result["answer"],
            question=result["question"],
            sources=result["source_documents"],
            processing_time=result["processing_time"],
            model_used=result["model_used"],
            num_documents_retrieved=result["num_documents_retrieved"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all processed documents
    """
    if not document_processor:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        documents = document_processor.list_processed_documents()
        return [
            DocumentInfo(
                document_id=doc["document_id"],
                file_name=doc["file_name"],
                file_type=doc["file_type"],
                num_chunks=doc["num_chunks"],
                processed_at=doc["processed_at"],
                file_size=doc["file_size"]
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a processed document

    Removes document from storage and all vector stores
    """
    if not document_processor:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        # Delete from storage
        success = document_processor.delete_processed_document(document_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

        # TODO: Remove from vector stores
        # This would require reindexing or removing specific chunks

        return {
            "success": True,
            "message": f"Document {document_id} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/models/compare", response_model=ModelComparisonResponse)
async def compare_models():
    """
    Compare BGE-small and E5-base models

    Returns performance metrics and recommendations
    """
    if not model_selector:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        # Get model comparison
        comparison = model_selector.compare_models(ModelType.BGE_SMALL, ModelType.E5_BASE)

        return ModelComparisonResponse(
            model1_name=comparison["model1"]["name"],
            model2_name=comparison["model2"]["name"],
            dimensions_comparison={
                "model1": comparison["model1"]["dimensions"],
                "model2": comparison["model2"]["dimensions"]
            },
            performance_comparison=comparison["performance"],
            recommendations=comparison["recommendation"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@app.get("/models/stats")
async def get_model_stats():
    """
    Get statistics for current model (LLM + embeddings)
    """
    global active_model

    if active_model not in rag_chains:
        raise HTTPException(status_code=503, detail="Model not available")

    try:
        stats = rag_chains[active_model].get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/models/switch")
async def switch_model(model_name: str):
    """
    Switch active model

    Supports: bge-small, e5-base
    """
    global active_model

    if model_name == "e5-base":
        new_model = ModelType.E5_BASE
    elif model_name == "bge-small":
        new_model = ModelType.BGE_SMALL
    else:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model_name}")

    if new_model not in rag_chains:
        raise HTTPException(status_code=503, detail=f"Model {model_name} not initialized")

    try:
        active_model = new_model
        return {
            "success": True,
            "active_model": active_model.value,
            "message": f"Switched to {active_model.value}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Switch failed: {str(e)}")


@app.get("/models/active")
async def get_active_model():
    """
    Get currently active model
    """
    return {
        "active_model": active_model.value,
        "available_models": [model.value for model in rag_chains.keys()]
    }


def main():
    """Run the API server"""
    print("\n" + "="*60)
    print("  RAG Chat API Server")
    print("="*60)
    print("Starting server on http://0.0.0.0:8000")
    print("API documentation: http://0.0.0.0:8000/docs")
    print("="*60 + "\n")

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()