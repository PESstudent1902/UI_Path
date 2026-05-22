# UiPath Studio Workflow Specifications

This document outlines the layout, variables, and activity properties for the four core UiPath Robot workflows (`.xaml` files) that orchestrate case stages, files, and email interactions.

---

## 1. EmailIntakeRobot.xaml (Stage 0 Intake)

**Purpose**: Polls the inbox, filters incoming mail, downloads PDFs, and prepares metadata.

### Workflow Logic
1. **Get IMAP Mail Messages** (or *Use Outlook 365 Mail* / *Gmail Activity*):
   - `Filter`: `"Subject: 'Tech Pack' OR Subject: 'Technical Specification'"`
   - `OnlyUnreadMessages`: `True`
   - `Top`: `10`
   - Output: `listMessages` (List of MailMessage)
2. **For Each** `mail` in `listMessages`:
   - Check if `mail.Attachments` has any `.pdf` files.
   - **If Yes**:
     - **Save Mail Attachments**:
       - `Folder`: `"C:\Users\Vansh\Documents\UiPath\TechPackIntake\TempPDFs\"`
       - Output: `extractedPDFs` (IEnumerable of String)
     - For each `pdfPath` in `extractedPDFs`:
       - **Invoke Workflow File**: `CaseCreationRobot.xaml` (passing `pdfPath`, `mail.From.Address`, `mail.Subject`)
     - **Move Mail Message**: Archive processed email to a "Processed" folder.
   - **If No**:
     - **Send SMTP Mail Message** (or Reply):
       - To: `mail.From.Address`
       - Subject: `"RE: " + mail.Subject`
       - Body: `"Thank you for contacting us. We noticed that your email did not contain a PDF Technical Specification sheet attachment. Please reply to this message attaching a valid Tech Pack PDF so our systems can begin processing."`

---

## 2. CaseCreationRobot.xaml (Maestro Case Ingestion)

**Purpose**: Standardizes Case ID formatting, uploads PDFs to storage, and writes case details into Maestro.

### Arguments
- `in_pdfPath` (String)
- `in_senderEmail` (String)
- `in_emailSubject` (String)

### Workflow Logic
1. **Assign Case ID**:
   - `caseSuffix` = `DateTime.Now.ToString("yyyyMMDD")` + `"-"` + `New Random().Next(1000, 9999).ToString()`
   - `caseId` = `"TP-" + caseSuffix`
2. **Upload PDF to Storage** (e.g. AWS S3 Buckets / Azure Blob Storage / Orchestrator Storage Buckets):
   - **Upload Storage Bucket File**:
     - `BucketName`: `"TechPacks"`
     - `Path`: `in_pdfPath`
     - `Key`: `caseId + ".pdf"`
     - Output: `pdfUrl`
3. **Initialize Case Schema Dictionary**:
   - Create `caseData` (Dictionary of String, Object) containing:
     - `"case_id"`: `caseId`
     - `"buyer_email"`: `in_senderEmail`
     - `"buyer_name"`: `in_emailSubject.Replace("Tech Pack", "").Trim()`
     - `"pdf_url"`: `pdfUrl`
     - `"stage"`: `"AI_EXTRACTION"`
     - `"status"`: `"IN_PROGRESS"`
4. **Create Case Activity (UiPath Maestro)**:
   - `CaseTemplate`: `"TechPackProcessing"`
   - `CaseId`: `caseId`
   - `CaseData`: `JsonConvert.SerializeObject(caseData)`
5. **HTTP Request to FastAPI Agent**:
   - `Endpoint`: `"http://localhost:8000/api/extract-techpack"`
   - `Method`: `POST`
   - `Body`: `"{'case_id': '" + caseId + "', 'pdf_url': '" + pdfUrl + "'}"`
   - Output: `apiResponse` (JSON string)
6. **Deserialize JSON** (`apiResponse`):
   - Extract `confidence_score` and `next_action`.
7. **Orchestrator Case Routing**:
   - **Update Case Status / Transition**:
     - Move case to `HUMAN_REVIEW` stage.
     - If `next_action == "ESCALATE"`:
       - **Create Form Task** (Action Center): Set Priority = `High`, Role = `Supervisor`
     - Else:
       - **Create Form Task** (Action Center): Set Priority = `Normal`, Role = `Merchandiser`

---

## 3. OutputGenerationRobot.xaml (Stage 4 Closing Robot)

**Purpose**: Triggers when the case is approved, requests costing calculations, saves the generated Excel, and emails the buyer.

### Workflow Logic
1. **Get Case Data (UiPath Maestro)**:
   - Pull the approved fields (BOM, Measurements, style variables) submitted from the Action Center task.
2. **HTTP Request (FastAPI Costing Endpoint)**:
   - `Endpoint`: `"http://localhost:8000/api/calculate-costing"`
   - `Method`: `POST`
   - `Body`: Send approved JSON.
   - Output: `costingResponse`
3. **Parse Costing Response**:
   - Deserialize `costingResponse` to extract `excel_filepath` and `fob_price_per_piece`.
4. **Send Email Response to Buyer**:
   - **Send SMTP Mail Message**:
     - To: `buyer_email` (from case metadata)
     - Subject: `"Garment Quotation Proposal - Style: " + style_name + " (" + style_number + ")"`
     - Body: 
       `"Dear " + buyer_name + ",\n\n"` +
       `"We have successfully completed the technical evaluation and costing matrix for your garment style: " + style_name + " (" + style_number + ").\n\n"` +
       `"Our final calculated FOB Price per piece is: USD " + fob_price_per_piece.ToString() + ".\n\n"` +
       `"Please find attached a comprehensive detail costing sheet outlining bill of materials, geometric fabric consumption, and order volumes.\n\n"` +
       `"We look forward to confirming your purchase order.\n\n"` +
       `"Best regards,\n"` +
       `"Merchandising Team\n"` +
       `"Indian Garment Exporters Ltd."`
     - `Attachments`: Add the file at `excel_filepath`.
5. **Close Case (UiPath Maestro)**:
   - **Update Case Status**: Set to `"COMPLETED"`, Close case card.

---

## 4. RFIEmailRobot.xaml (Exception Workflow)

**Purpose**: Runs when the merchandiser rejects the case inside Action Center, selecting the RFI button option.

### Workflow Logic
1. **Get Case Data**:
   - Read the list of `clarification_questions` entered or edited by the merchandiser in the Action Center form.
2. **Send SMTP Mail Message** (RFI Request):
   - To: `buyer_email`
   - Subject: `"Information Required: Technical Specifications Clarification - " + style_number`
   - Body: 
     `"Dear " + buyer_name + ",\n\n"` +
     `"Our technical design team reviewed the tech pack for style " + style_name + " (" + style_number + ") and requires some additional specifications before we can compile costing quotes.\n\n"` +
     `"Please review and reply with clarifications for the following items:\n"` +
     `clarification_questions_list` + `"\n\n"` +
     `"We will resume processing immediately upon receiving your feedback.\n\n"` +
     `"Best regards,\n"` +
     `"Merchandising Team"`
3. **Update Case Status (UiPath Maestro)**:
   - Transition stage to `"PENDING_BUYER_RESPONSE"`.
   - Update Case Status = `"SUSPENDED"`.
