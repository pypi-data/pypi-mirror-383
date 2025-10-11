"""
ASPERA FastAPI Backend
======================
REST API per parsing, esecuzione e gestione programmi Aspera.

Endpoints:
  POST /parse        - Parse codice Aspera → AST
  POST /run          - Esegui programma Aspera
  GET  /examples     - Lista esempi disponibili
  GET  /examples/{name} - Ottieni esempio specifico
  POST /validate     - Valida AST
  GET  /health       - Health check
  GET  /stats        - Statistiche sistema

Author: Christian Quintino De Luca - RTH Italia
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import logging
import os
from datetime import datetime

from aspera.lang.parser import parse_aspera, validate_ast, ParseError
from aspera.runtime.thresholds import get_thresholds
from aspera.sdk.client import create_engine, run_observation, serialize_state
from aspera.sdk.utils import ast_to_summary

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ASPERA API",
    description="Linguaggio Cognitivo Ibrido - REST API",
    version="0.10.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware per permettere richieste da frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specificare domini precisi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS (Pydantic)
# ============================================================================

class ParseRequest(BaseModel):
    """Request per parse endpoint"""
    code: str = Field(..., description="Codice Aspera da parsare")
    validate: bool = Field(True, description="Validare AST contro schema")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 'concept "test" { definition: "a test"; baseline: 0.5; }',
                "validate": True
            }
        }


class ParseResponse(BaseModel):
    """Response per parse endpoint"""
    success: bool
    ast: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RunRequest(BaseModel):
    """Request per run endpoint"""
    code: Optional[str] = Field(None, description="Codice Aspera (alternativo ad ast)")
    ast: Optional[Dict[str, Any]] = Field(None, description="AST già parsato")
    signals: Dict[str, Any] = Field(..., description="Segnali di input")
    context: Optional[Dict[str, Any]] = Field(None, description="Contesto aggiuntivo")
    mode: str = Field("auto", description="Modalità LLM: 'auto' (default, usa Groq se GROQ_API_KEY presente), 'mock', o 'groq'")
    explain: bool = Field(True, description="Generare spiegazione")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 'concept "fiducia" { definition: "trust"; baseline: 0.5; }\ninference "test" { when: signals.x > 0.5; then: increase concept:"fiducia" by 0.1; confidence: 0.8; }',
                "signals": {"x": 0.7},
                "context": {"experiences": {"shared": 3}},
                "mode": "mock",
                "explain": True
            }
        }


class RunResponse(BaseModel):
    """Response per run endpoint"""
    success: bool
    step_result: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    state_snapshot: Optional[Dict[str, Any]] = None
    audit_trace: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ValidateRequest(BaseModel):
    """Request per validate endpoint"""
    ast: Dict[str, Any] = Field(..., description="AST da validare")


class ValidateResponse(BaseModel):
    """Response per validate endpoint"""
    success: bool
    valid: bool
    errors: Optional[List[str]] = None


class ExampleInfo(BaseModel):
    """Info su un esempio"""
    name: str
    path: str
    description: str
    concepts_count: int
    inferences_count: int
    intentions_count: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "ASPERA API",
        "version": "0.10.0",
        "description": "Linguaggio Cognitivo Ibrido",
        "author": "Christian Quintino De Luca - RTH Italia",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "aspera-api"
    }


@app.post("/parse", response_model=ParseResponse)
async def parse_endpoint(request: ParseRequest):
    """
    Parse codice Aspera e ritorna AST.

    - **code**: Codice sorgente Aspera
    - **validate**: Se true, valida AST contro schema
    """
    try:
        logger.info("Parsing Aspera code...")
        
        # Parse
        ast = parse_aspera(request.code)
        
        # Validate se richiesto
        if request.validate:
            try:
                validate_ast(ast)
                logger.info("AST validation successful")
            except Exception as e:
                logger.warning(f"AST validation failed: {e}")
                return ParseResponse(
                    success=False,
                    error=f"Validation failed: {str(e)}"
                )
        
        # Genera summary
        summary = ast_to_summary(ast)
        
        logger.info("Parse successful")
        return ParseResponse(
            success=True,
            ast=ast,
            summary=summary
        )
        
    except ParseError as e:
        logger.error(f"Parse error: {e}")
        return ParseResponse(
            success=False,
            error=f"Parse error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in parse: {e}")
        return ParseResponse(
            success=False,
            error=f"Internal error: {str(e)}"
        )


@app.post("/run", response_model=RunResponse)
async def run_endpoint(request: RunRequest):
    """
    Esegue programma Aspera con signals e context.

    - **code** o **ast**: Sorgente Aspera o AST già parsato
    - **signals**: Dictionary con segnali di input
    - **context**: Context aggiuntivo (opzionale)
    - **mode**: 'auto' (default, usa Groq se GROQ_API_KEY presente), 'mock' per testing, 'groq' forza Groq
    - **explain**: Genera spiegazione testuale
    """
    try:
        logger.info(f"Running Aspera program (mode={request.mode})...")
        
        # Determina source
        if request.code:
            source = request.code
            logger.info("Using code source")
        elif request.ast:
            source = request.ast
            logger.info("Using AST source")
        else:
            return RunResponse(
                success=False,
                error="Must provide either 'code' or 'ast'"
            )
        
        # Crea engine
        if request.mode == "auto":
            engine = create_engine(source, auto_detect=True)
            logger.info("Engine created (auto-detect mode)")
        else:
            use_mock = (request.mode == "mock")
            engine = create_engine(source, use_mock_llm=use_mock, auto_detect=False)
            logger.info(f"Engine created (mode: {request.mode})")
        
        # Esegui osservazione
        result = run_observation(
            engine,
            signals=request.signals,
            context=request.context,
            explain=request.explain
        )
        
        logger.info("Execution completed successfully")
        return RunResponse(
            success=True,
            step_result=result["step_result"],
            actions=result["actions"],
            explanation=result.get("explanation"),
            state_snapshot=result["state_snapshot"],
            audit_trace=result["audit_trace"]
        )
        
    except ParseError as e:
        logger.error(f"Parse error in run: {e}")
        return RunResponse(
            success=False,
            error=f"Parse error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        return RunResponse(
            success=False,
            error=f"Execution error: {str(e)}"
        )


@app.post("/validate", response_model=ValidateResponse)
async def validate_endpoint(request: ValidateRequest):
    """
    Valida AST contro JSON schema.

    - **ast**: AST dictionary da validare
    """
    try:
        logger.info("Validating AST...")
        validate_ast(request.ast)
        logger.info("Validation successful")
        return ValidateResponse(
            success=True,
            valid=True
        )
    except Exception as e:
        logger.warning(f"Validation failed: {e}")
        return ValidateResponse(
            success=True,
            valid=False,
            errors=[str(e)]
        )


@app.get("/examples")
async def list_examples():
    """
    Lista tutti gli esempi disponibili.
    """
    try:
        examples_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "lang", "examples"
        )
        
        examples = []
        
        # Empathetic
        empathetic_path = os.path.join(examples_dir, "empathetic.aspera")
        if os.path.exists(empathetic_path):
            with open(empathetic_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast = parse_aspera(code)
            summary = ast_to_summary(ast)
            examples.append({
                "name": "empathetic",
                "path": "aspera/lang/examples/empathetic.aspera",
                "description": "Agente empatico che costruisce fiducia e cooperazione",
                "concepts_count": len(summary["concepts"]),
                "inferences_count": len(summary["inferences"]),
                "intentions_count": len(summary["intentions"])
            })
        
        # Collaborative
        collaborative_path = os.path.join(examples_dir, "collaborative.aspera")
        if os.path.exists(collaborative_path):
            with open(collaborative_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast = parse_aspera(code)
            summary = ast_to_summary(ast)
            examples.append({
                "name": "collaborative",
                "path": "aspera/lang/examples/collaborative.aspera",
                "description": "Problem solver collaborativo con gestione obiettivi multipli",
                "concepts_count": len(summary["concepts"]),
                "inferences_count": len(summary["inferences"]),
                "intentions_count": len(summary["intentions"])
            })
        
        # Analytical
        analytical_path = os.path.join(examples_dir, "analytical.aspera")
        if os.path.exists(analytical_path):
            with open(analytical_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast = parse_aspera(code)
            summary = ast_to_summary(ast)
            examples.append({
                "name": "analytical",
                "path": "aspera/lang/examples/analytical.aspera",
                "description": "Reasoner analitico con inferenza logica rigorosa",
                "concepts_count": len(summary["concepts"]),
                "inferences_count": len(summary["inferences"]),
                "intentions_count": len(summary["intentions"])
            })
        
        logger.info(f"Found {len(examples)} examples")
        return {
            "success": True,
            "count": len(examples),
            "examples": examples
        }
        
    except Exception as e:
        logger.error(f"Error listing examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/examples/{name}")
async def get_example(name: str):
    """
    Ottieni codice sorgente e AST di un esempio specifico.

    - **name**: Nome esempio (empathetic, collaborative, analytical)
    """
    try:
        examples_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "lang", "examples"
        )
        
        filepath = os.path.join(examples_dir, f"{name}.aspera")
        
        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=404,
                detail=f"Example '{name}' not found"
            )
        
        # Leggi codice
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Parse
        ast = parse_aspera(code)
        summary = ast_to_summary(ast)
        
        logger.info(f"Retrieved example: {name}")
        return {
            "success": True,
            "name": name,
            "code": code,
            "ast": ast,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """
    Statistiche sistema ASPERA.
    """
    return {
        "success": True,
        "stats": {
            "api_version": "0.10.0",
            "parser_version": "0.10.0",
            "runtime_version": "0.10.0",
            "supported_llm_modes": ["mock", "groq"],
            "examples_available": 3
        }
    }


@app.post("/feedback/threshold")
async def feedback_threshold(payload: Dict[str, Any]):
    """
    Registra feedback per soglia simbolica (epsilon-greedy).
    Body:
      - key: string (es. "concept.cart_abandon_risk")
      - success: bool
      - observed_score: float (opzionale)
      - default: float (opzionale, default 0.5)
    """
    key = payload.get("key")
    if not isinstance(key, str) or not key:
        raise HTTPException(status_code=400, detail="missing key")
    success = bool(payload.get("success", False))
    observed = payload.get("observed_score")
    default = float(payload.get("default", 0.5))

    reg = get_thresholds()
    _ = reg.get(key, default)
    reg.record_feedback(key, success, observed)
    return {"ok": True, "stats": reg.export().get(key, {})}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload file .aspera e ritorna AST.

    - **file**: File .aspera da uploadare
    """
    try:
        # Leggi contenuto
        content = await file.read()
        code = content.decode('utf-8')
        
        logger.info(f"Uploaded file: {file.filename}")
        
        # Parse
        ast = parse_aspera(code)
        summary = ast_to_summary(ast)
        
        return {
            "success": True,
            "filename": file.filename,
            "ast": ast,
            "summary": summary
        }
        
    except ParseError as e:
        logger.error(f"Parse error in upload: {e}")
        raise HTTPException(status_code=400, detail=f"Parse error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Eseguito all'avvio dell'API"""
    logger.info("="*60)
    logger.info("ASPERA API Starting...")
    logger.info("Version: 0.10.0")
    logger.info("Author: Christian Quintino De Luca - RTH Italia")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Eseguito allo shutdown dell'API"""
    logger.info("ASPERA API Shutting down...")


# ============================================================================
# MAIN (per esecuzione diretta)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("ASPERA_API_HOST", "0.0.0.0")
    port = int(os.getenv("ASPERA_API_PORT", 8000))
    
    logger.info(f"Starting ASPERA API on {host}:{port}")
    
    uvicorn.run(
        "aspera.web.api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

