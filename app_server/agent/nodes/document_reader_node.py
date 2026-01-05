
from typing import Dict, Any
from app_server.agent.state import ClaimAgentState
from app_server.utils.clients import azure_client, AZURE_DEPLOYMENT_NAME
from app_server.utils.helpers import safe_parse_json, ensure_azure_url_has_sas
import logging
import fitz # PyMuPDF
import base64
import requests
import io

def document_reader_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    Reads documents from Azure Blob Storage links provided in fnol_data.
    Uses Azure OpenAI Vision to extract data.
    """
    print("--- Document Reader Node ---")
    
    fnol_data = state.get("fnol_data", {})
    documents = fnol_data.get("documents", [])
    
    if not documents:
        print("ℹ️ No documents found to read.")
        return {"document_data": {"status": "skipped", "reason": "no_documents"}}

    def call_vision(image_url, doc_type_hint="unknown"):
        try:
            # Ensure URL has SAS token if it's Azure Blob
            signed_url = ensure_azure_url_has_sas(image_url)
            
            # Check if it's a PDF. GPT-4o Vision does not support PDF URLs directly.
            if signed_url.lower().split('?')[0].endswith('.pdf'):
                print(f"📄 PDF Detected: {image_url}. Converting first page to image...")
                pdf_resp = requests.get(signed_url)
                pdf_resp.raise_for_status()
                
                # Open PDF from memory
                doc = fitz.open(stream=pdf_resp.content, filetype="pdf")
                if len(doc) == 0:
                    raise Exception("Empty PDF document")
                
                page = doc[0]
                # High resolution pixmap (Matrix 2.0 = 2x zoom) for better OCR
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_bytes = pix.tobytes("jpg")
                doc.close()
                
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                image_data_url = f"data:image/jpeg;base64,{base64_image}"
                print("✅ PDF conversion successful.")
            else:
                image_data_url = signed_url

            prompt = f"""
You are a smart insurance claim document extraction assistant.
1. **Analyze the image content** to identify the document type.
2. The user labeled this as: '{doc_type_hint}'.
3. Extract relevant fields based on the document type.

Typical fields for Claims:
- Death Certificate: name of deceased, date of death, cause of death, registration number.
- Hospital Bill: hospital name, patient name, total amount, date of admission/discharge.
- Driving License: license number, expiry date, vehicle class.
- RC Copy: vehicle registration number, owner name, chassis number.

Return JSON only:
{{
  "document_type": "Detected Type",
  "extracted_data": {{ ...fields... }},
  "confidence": 0.0-1.0
}}
"""
            resp = azure_client.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }],
                max_tokens=1000,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return safe_parse_json(resp.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error reading document {image_url}: {e}")
            return {"error": str(e)}

    results = {}
    for idx, doc in enumerate(documents):
        filename = doc.get("filename", "unknown")
        url = doc.get("url")
        category = doc.get("category", "unknown")
        
        # Use a unique key to prevent collisions (e.g., 0_death-certificate)
        unique_key = f"{idx}_{category}"
        
        if url:
            print(f"📄 Reading document: {filename} ({category}) as {unique_key}")
            results[unique_key] = {
                "filename": filename,
                "category": category,
                "url": url,
                "extraction": call_vision(url, doc_type_hint=category)
            }
        else:
            print(f"⚠️ No URL for document: {filename} at index {idx}")

    res = {
        "document_data": {
            "status": "completed",
            "results": results
        }
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="document_processing")
    
    return res
