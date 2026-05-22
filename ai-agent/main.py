import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load .env file robustly from script directory or parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
env_paths = [
    os.path.join(script_dir, ".env"),
    os.path.join(os.path.dirname(script_dir), ".env")
]
for path in env_paths:
    if os.path.exists(path):
        load_dotenv(dotenv_path=path)
        break
else:
    load_dotenv()

# Set up path imports for serverless environments (like Vercel)
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Local Modules
from extraction_agent import extract_techpack
from costing_agent import process_costing
from excel_generator import generate_costing_excel

app = FastAPI(
    title="AI Garment Tech Pack Processing Backend",
    description="FastAPI orchestration endpoints for UiPath Maestro case workflow integration.",
    version="1.1"
)

# ----------------- PYDANTIC SCHEMAS -----------------

class ExtractionRequest(BaseModel):
    case_id: str = Field(..., example="TP-20260523-0001")
    pdf_url: str = Field(..., example="https://storage.example.com/techpacks/TP-20260523-0001.pdf")

class ExtractionResponse(BaseModel):
    case_id: str
    status: str
    confidence_score: float
    data: Dict[str, Any]
    next_action: str

class StyleData(BaseModel):
    style_name: str
    style_number: str
    garment_type: str
    fabric_composition: str
    fabric_gsm: Optional[float] = None
    fabric_width: float
    measurements: Dict[str, Dict[str, float]]
    bill_of_materials: List[Dict[str, Any]]

class CostingRequest(BaseModel):
    case_id: str
    style_data: StyleData
    order_quantity: Optional[Dict[str, int]] = None
    markup_percentage: Optional[float] = None


class CostingResponse(BaseModel):
    case_id: str
    status: str
    excel_filepath: str
    costing_sheet: Dict[str, Any]

# ----------------- API ENDPOINTS -----------------

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Convenience endpoint for the UI to upload actual PDFs for parsing.
    Saves the file to sample-data/ uploads folder.
    """
    try:
        if os.environ.get("VERCEL"):
            upload_dir = "/tmp"
        else:
            upload_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "sample-data"
            )
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, file.filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())
        return {
            "status": "SUCCESS", 
            "filepath": filepath, 
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.get("/api/download-excel/{case_id}")
async def download_excel(case_id: str):
    """
    Downloads the styled Excel spreadsheet generated for the given case ID.
    """
    if os.environ.get("VERCEL"):
        output_dir = "/tmp"
    else:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "outputs"
        )
    filepath = os.path.join(output_dir, f"costing_sheet_{case_id}.xlsx")
    if os.path.exists(filepath):
        return FileResponse(
            filepath, 
            filename=f"costing_sheet_{case_id}.xlsx", 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        raise HTTPException(status_code=404, detail=f"Costing sheet for Case ID {case_id} not found.")


@app.post("/api/extract-techpack", response_model=ExtractionResponse)
async def extract_techpack_endpoint(request: ExtractionRequest):
    """
    Stage 1: AI Extraction Agent.
    Parses a tech pack PDF (via URL or local path) and extracts structured garment information.
    """
    try:
        print(f"[{request.case_id}] Received extraction request for PDF: {request.pdf_url}")
        
        extracted_data = extract_techpack(request.pdf_url)
        confidence = extracted_data.get("confidence_score", 0.70)
        
        # Routing Decision Logic based on confidence threshold
        next_action = "HUMAN_REVIEW" if confidence >= 0.70 else "ESCALATE"
        
        return ExtractionResponse(
            case_id=request.case_id,
            status="SUCCESS",
            confidence_score=confidence,
            data=extracted_data,
            next_action=next_action
        )
    except Exception as e:
        print(f"[{request.case_id}] Extraction endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")


@app.post("/api/calculate-costing", response_model=CostingResponse)
async def calculate_costing_endpoint(request: CostingRequest):
    """
    Stage 3: Costing Agent.
    Runs geometric calculation logic, pulls standard pricing catalog, and generates FOB sheet.
    It automatically produces a styled Excel costing sheet in the project's outputs folder.
    """
    try:
        print(f"[{request.case_id}] Received costing calculation request for style: {request.style_data.style_name}")
        
        # Process Pydantic inputs into dictionary formats
        style_dict = request.style_data.model_dump()
        order_qty_dict = request.order_quantity
        markup_percentage = request.markup_percentage
        
        # Calculate Costing details
        costing_sheet = process_costing(style_dict, order_qty_dict, markup_percentage)
        
        # Ensure output folder exists for generating excel reports
        if os.environ.get("VERCEL"):
            output_dir = "/tmp"
        else:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "outputs"
            )
        os.makedirs(output_dir, exist_ok=True)
        
        # Write Styled Excel Report
        excel_filename = f"costing_sheet_{request.case_id}.xlsx"
        excel_filepath = os.path.join(output_dir, excel_filename)
        
        generate_costing_excel(costing_sheet, excel_filepath)
        print(f"[{request.case_id}] Costing spreadsheet written successfully: {excel_filepath}")
        
        return CostingResponse(
            case_id=request.case_id,
            status="SUCCESS",
            excel_filepath=excel_filepath,
            costing_sheet=costing_sheet
        )
    except Exception as e:
        print(f"[{request.case_id}] Costing calculation endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Costing calculation failed: {str(e)}")


# ----------------- UI / STATIC SITES SERVING -----------------

@app.get("/api/status")
async def get_status():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key.strip():
        api_key = os.environ.get("GeminiAPI", "")
    if not api_key.strip():
        api_key = os.environ.get("GEMINI_API", "")
    return {
        "status": "ONLINE",
        "system": "Garment Tech Pack Case Processing AI backend",
        "gemini_api_key_configured": len(api_key.strip()) > 0
    }


@app.get("/")
async def get_index():
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key.strip():
        api_key = os.environ.get("GeminiAPI", "")
    if not api_key.strip():
        api_key = os.environ.get("GEMINI_API", "")
    return {
        "status": "ONLINE",
        "system": "Garment Tech Pack Case Processing AI backend",
        "ui_hint": "Please create the static/index.html dashboard layout.",
        "gemini_api_key_configured": len(api_key.strip()) > 0
    }

# Mount static folder
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
