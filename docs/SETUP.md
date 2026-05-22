# Setup and Local Running Guide

Follow these steps to deploy and test the AI-Powered Garment Tech Pack backend locally.

---

## Prerequisites

1. **Python 3.8+** installed on your system.
2. An **Anthropic/Gemini/Google AI Studio** account (optional). We use the **Google Gemini API** free tier.
3. If you don't have a Gemini API key, you can run the system out-of-the-box. The server automatically falls back to high-fidelity mock extraction responses corresponding to the mock PDFs, so your demonstration will still function.

---

## 1. Installation

1. Navigate to the `ai-agent` directory in your terminal:
   ```bash
   cd ai-agent
   ```
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Configuration (.env)

Open `ai-agent/.env` and optionally set your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
If you do not have an API key, keep it blank. The backend will detect this and automatically load high-fidelity simulated extractions based on the input PDF name.

---

## 3. Generate Sample PDF Tech Packs

To compile the sample PDFs (Clean Polo Shirt and Incomplete Tee) for testing:
1. Run the data generator script:
   ```bash
   python ../sample-data/generate_sample_data.py
   ```
2. This creates two files under `/sample-data/`:
   - `sample_techpack_1.pdf` (Clean specsheet)
   - `sample_techpack_2.pdf` (Messy/Incomplete specsheet)

---

## 4. Run the FastAPI Server

Start the API backend server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The server will start on `http://localhost:8000`. You can access the interactive Swagger API documentation at `http://localhost:8000/docs`.

---

## 5. Local API Testing

You can use `curl` or any API client (e.g. Postman) to test the endpoints.

### Test A: Extraction Endpoint (Clean Tech Pack)
```bash
curl -X POST "http://localhost:8000/api/extract-techpack" \
     -H "Content-Type: application/json" \
     -d "{\"case_id\": \"TP-20260523-0001\", \"pdf_url\": \"../sample-data/sample_techpack_1.pdf\"}"
```
*Expected Response*: Status `SUCCESS`, confidence score `0.88`, next_action `HUMAN_REVIEW`, and parsed polo specifications inside `data`.

### Test B: Extraction Endpoint (Messy Tech Pack)
```bash
curl -X POST "http://localhost:8000/api/extract-techpack" \
     -H "Content-Type: application/json" \
     -d "{\"case_id\": \"TP-20260523-0002\", \"pdf_url\": \"../sample-data/sample_techpack_2.pdf\"}"
```
*Expected Response*: Status `SUCCESS`, confidence score `0.65` (under 0.70 threshold), next_action `ESCALATE`, and low confidence flags inside `low_confidence_fields`.

### Test C: Costing and Excel Sheet Generation
```bash
curl -X POST "http://localhost:8000/api/calculate-costing" \
     -H "Content-Type: application/json" \
     -d "{
       \"case_id\": \"TP-20260523-0001\",
       \"style_data\": {
         \"style_name\": \"Classic Polo Shirt\",
         \"style_number\": \"FB-2026-P001\",
         \"garment_type\": \"Polo Shirt\",
         \"fabric_composition\": \"100% Cotton Pique\",
         \"fabric_gsm\": 200,
         \"fabric_width\": 60,
         \"measurements\": {
           \"chest\": {\"S\": 38, \"M\": 40, \"L\": 42, \"XL\": 44},
           \"length\": {\"S\": 27, \"M\": 28, \"L\": 29, \"XL\": 30}
         },
         \"bill_of_materials\": [
           {\"item\": \"Main fabric - Cotton Pique\", \"unit\": \"yards\", \"consumption_per_piece\": 1.8},
           {\"item\": \"Rib fabric - collar/cuffs\", \"unit\": \"yards\", \"consumption_per_piece\": 0.3},
           {\"item\": \"Buttons - 3 hole\", \"unit\": \"pieces\", \"consumption_per_piece\": 3},
           {\"item\": \"Thread - main\", \"unit\": \"meters\", \"consumption_per_piece\": 180}
         ]
       },
       \"order_quantity\": {
         \"S\": 1000,
         \"M\": 1500,
         \"L\": 1200,
         \"XL\": 800
       }
     }"
```
*Expected Response*: Status `SUCCESS`, JSON costing summary, and `excel_filepath` pointing to a newly created file inside `/outputs/costing_sheet_TP-20260523-0001.xlsx`. Go open that file to inspect the styled Excel output!
