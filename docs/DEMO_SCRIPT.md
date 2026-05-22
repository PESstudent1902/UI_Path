# Hackathon Presentation Demo Script

**Project Title**: AI-Powered Garment Tech Pack Case Management System  
**Track**: Track 1 - UiPath Maestro Case Management  
**Time Limit**: 5-7 Minutes  

Use this script to guide the judges through the live demo. It highlights automation handoffs, exception routing, and human-in-the-loop control.

---

## Act 1: Intake & Case Initialization (60 Seconds)

1. **Introduction**:
   - *"Hello judges, today we are showcasing an end-to-end Case Management system for garment exporters. Manual processing of international tech packs takes 3 to 5 hours of a merchandiser's time. Our system automates ingestion, extracts details, reviews edge cases, and responds with a costing sheet in under 5 minutes."*
2. **Intake Flow (Stage 0)**:
   - Show the mock email in the inbox from `buyer@fashionbrand.com` with `sample_techpack_1.pdf` attached.
   - Run or explain the intake workflow (`EmailIntakeRobot`):
     - *"When the email arrives, a UiPath email trigger wakes up, uploads the PDF to S3/Blob storage, parses metadata, and registers a brand new Maestro case: Case ID `TP-20260523-0001`."*
   - Show the Maestro Case Dashboard. A new card is created in the `AI_EXTRACTION` column.

---

## Act 2: AI Extraction & Confidence Check (60 Seconds)

1. **AI Extraction API (Stage 1)**:
   - *"As the case enters Stage 1, Maestro invokes our FastAPI agent, triggering extraction."*
   - Execute the extraction curl request (or show Swagger UI).
   - *"Under the hood, our parser extracts the text from the PDF. Google's Gemini API is called, returning a structured JSON document mapping measurements, fabric specs, and materials."*
2. **Confidence Routing**:
   - *"The extraction agent automatically scores confidence. Our first test case has all parameters. The score is 88%. This meets our 70% threshold, so the case automatically advances to Stage 2: Human Review."*
   - *"If we run this on a messy tech pack with missing GSM weight (like Sample 2), the confidence score drops to 65%. The system catches this, routing it immediately to a high-priority manual escalation form in UiPath Action Center."*

---

## Act 3: Human Review Form (90 Seconds)

1. **Task Review (Stage 2)**:
   - Open the **UiPath Action Center Task List** and click on the "Tech Pack Review" task.
   - Show the layout (which matches `TechPackReviewForm.json`):
     - Read-only Case details, AI confidence, and the PDF download link on the left side.
     - Editable fields for measurements, style values, and bill of materials on the right.
   - *"The merchandiser remains in control. They verify that the measurements table is correct. Let's make a manual adjustment—changing the sleeve size from 8.5 to 8.7 inches based on client notes."*
   - *"Note the AI-generated clarification questions. The system flagged that the button color and packaging criteria were missing from the brief."*
2. **Action Decisions**:
   - Point out the options:
     - **Save Draft**: Saves work to review later.
     - **Reject & Send RFI**: Close the case and email the clarification questions to the buyer.
     - **Approve and Continue**: Update case and calculate costing.
   - Click **Approve and Continue**:
     - *"Upon clicking approve, the workflow writes back the verified parameters to Maestro and transitions the case to Stage 3: Costing."*

---

## Act 4: Costing Agent Math (60 Seconds)

1. **Geometric Formula Calculation (Stage 3)**:
   - *"Once approved, our Costing Agent API is invoked. Rather than requiring heavy, expensive CAD software integrations, it uses an industry-validated geometric approximation formula."*
   - Explain the math:
     - *"It uses Medium chest and body lengths, adjusts for fabric width, applies a garment type multiplier (1.15 for Polos), and adds a 10% cutting wastage margin."*
2. **BOM Lookup**:
   - *"It performs a fuzzy text-matching search against our local pricing catalog to calculate fabric cost, thread cost, labels, and buttons."*
   - Show the costing response payload (or Swagger dashboard):
     - CMT Rate: $3.20 (standard polo rate).
     - Markup: 15%.
     - Final FOB price: $19.94.

---

## Act 5: Output Excel & Closure (60 Seconds)

1. **Spreadsheet Exporter (Stage 4)**:
   - *"Stage 4 starts the final robot workflow to export the output sheets and email the client. It uses python's openpyxl library to create a custom-styled Excel sheet."*
   - Open the output directory and double-click to load the generated spreadsheet (`outputs/costing_sheet_TP-20260523-0001.xlsx`).
   - Highlight the premium details to the judges:
     - Double lines on total boundaries, soft green highlight fill on final prices, structured tables, and bold labels.
     - Formatted currencies and counts.
2. **Email Delivery**:
   - Show the final outbound email draft:
     - *"The robot emails the buyer at `buyer@fashionbrand.com` with the styled costing sheet and RFI questions attached. The Maestro case is set to COMPLETED and closed. Total time elapsed: less than 5 minutes."*

---

## Act 6: Wrap-Up & Value Pitch (30 Seconds)

- *"To summarize: We have implemented all Track 1 constraints. We demonstrated robust API-based agent orchestrations, automated confidence metrics, custom Action Center schemas, and professional Excel exports. This workflow reduces merchandiser processing overhead by over 90%, transforming hours of manual entry into simple verification. Thank you, and we welcome your questions!"*
