import requests
import os
import json
import re
import base64
from urllib.parse import urlparse, urlunparse, quote

# Try to load SAS from env
AZURE_SAS_TOKEN = os.getenv("AZURE_SAS_TOKEN", "")

def call_mcp_tool(tool_name: str, arg: str, mcp_base_url: str = "http://localhost:9000") -> dict:
    """
    Helper to call the MCP API.
    """
    url = f"{mcp_base_url}/{tool_name}/{arg}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling MCP tool {tool_name}: {e}")
        return {}

def ensure_azure_url_has_sas(url: str, sas_token: str = AZURE_SAS_TOKEN) -> str:
    """
    Ensure Azure Blob Storage URL has a valid SAS token.
    """
    if not url or not isinstance(url, str):
        return url
        
    if 'blob.core.windows.net' in url:
        parsed = urlparse(url)
        encoded_path = quote(parsed.path, safe='/')
        base_url = urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, '', ''))
        
        if parsed.query and ('sig=' in parsed.query or 'sv=' in parsed.query):
            return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))
            
        elif sas_token:
            clean_sas = sas_token.lstrip('?&')
            return f"{base_url}?{clean_sas}"
            
    return url

def safe_parse_json(text):
    text = re.sub(r"^```[a-zA-Z]*", "", text)
    text = re.sub(r"```$", "", text).strip()
    m = re.search(r"\{[\s\S]*\}", text)
    try:
        if m:
            return json.loads(m.group(0))
        return json.loads(text)
    except Exception:
        return {"raw": text}

def parse_currency(value) -> float:
    """
    Robustly parse currency string to float.
    Handles: "1,00,000", "₹ 50000", "$1000", etc.
    """
    if not value:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    # Remove common currency symbols and commas
    clean_val = str(value).replace(",", "").replace("₹", "").replace("$", "").replace(" ", "")
    try:
        return float(clean_val)
    except ValueError:
        return 0.0
