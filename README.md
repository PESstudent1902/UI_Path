# AI-Powered Garment Tech Pack Case Management System

An automated, AI-driven technical specification (tech pack) extraction and costing response engine built for the **UiPath Maestro Case Management Track (Track 1)**.

Indian garment exporters receive hundreds of complex, multi-page tech pack PDFs each season from global buyers. Processing each tech pack manually takes 3 to 5 hours of a merchandiser's time. This system automates ingestion and parsing using the **Google Gemini API**, applies geometric calculation rules to estimate fabric consumption, integrates a human review loop via **UiPath Action Center**, and generates styled client-ready costing spreadsheets in under 30 minutes.

---

## Key Features

1. **AI-Driven Data Extraction**: Integrates Google's **Gemini API** (`gemini-1.5-flash`) to parse semi-structured technical specifications from raw text (extracted via `pdfplumber`) into structured JSON models.
2. **Confidence Scoring & Routing**: Automatically computes an extraction confidence score. If crucial fields are missing or unclear (confidence < 0.70), it flags the case for manual high-priority review.
3. **Geometric Fabric Costing**: Establishes initial fabric consumption requirements using geometric calculations calibrated for T-shirts, Polo shirts, dresses, jackets, and trousers.
4. **Interactive Action Center Schema**: Includes schemas defining the merchandiser verification forms within UiPath Action Center.
5. **Corporate Excel Costing Reports**: Generates professional, styled, and formula-backed Excel costing sheets for the exporter merchandising team and buyer.

---

## File Structure

```
/uipath-maestro-techpack/
├── /uipath-workflows/
│   └── workflow_outlines.md           # Stage 0-4 UiPath workflow definitions
├── /ai-agent/
│   ├── main.py                        # FastAPI application endpoints
│   ├── extraction_agent.py            # Gemini text extraction & confidence checks
│   ├── costing_agent.py               # Geometric math and database lookups
│   ├── excel_generator.py             # openpyxl excel builder with premium styling
│   ├── requirements.txt               # Python package dependencies
│   └── .env                           # Server environment configurations
├── /action-center-forms/
│   └── TechPackReviewForm.json        # Action Center human form layout schema
├── /sample-data/
│   ├── generate_sample_data.py        # ReportLab PDF compiler for demo samples
│   ├── pricing_database.json          # Standard material and CMT rates database
│   ├── sample_techpack_1.pdf          # Generated clean tech pack (Success flow)
│   └── sample_techpack_2.pdf          # Generated messy tech pack (Exception flow)
├── /docs/
│   ├── SETUP.md                       # Local installation and run guidelines
│   ├── DEMO_SCRIPT.md                 # 5-7 minute presentation walkthrough script
│   └── ARCHITECTURE.md                # System sequence and architecture diagram
└── README.md                          # Project overview
```

---

## High-Level Sequence Workflow

```
[Email PDF] → [UiPath Intake Robot] 
                     ↓ (Create Maestro Case)
              [FastAPI: /api/extract-techpack] 
                     ↓ (Runs Gemini API Extraction)
        [Confidence Check]
         ├── >= 0.70 ──> [UiPath Action Center: Human Review Form] ── (Approve) ──> [FastAPI: /api/calculate-costing] ──> [Excel cost sheets] ──> [Send Response]
         └──  < 0.70 ──> [High-Priority Human Review Escalation]
```

Please see the [docs/SETUP.md](file:///C:/Users/Vansh/.gemini/antigravity/scratch/uipath-maestro-techpack/docs/SETUP.md) file to spin up the local server, compile test data, and run verification scripts.
