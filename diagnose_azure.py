
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import requests

load_dotenv()

def test_config():
    print("--- Azure OpenAI Diagnostic Test ---")
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
    sas = os.getenv("AZURE_SAS_TOKEN")

    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    print(f"Key set: {'Yes' if key and 'your' not in key else 'No (Placeholder detected)'}")
    print(f"SAS Token set: {'Yes' if sas else 'No'}")

    if not endpoint or "your" in endpoint:
        print("❌ ERROR: AZURE_OPENAI_ENDPOINT is still a placeholder!")
        return

    if not key or "your" in key:
        print("❌ ERROR: AZURE_OPENAI_API_KEY is still a placeholder!")
        return

    # Test Image Access
    test_image_url = "https://insurancedocuments.blob.core.windows.net/insurance-docs/claims/pending/6/death-certificate/32f0329a-b92f-45ab-8fea-065497dc01e1.pdf"
    
    if sas:
        sas = sas.strip('"').strip("'").lstrip('?&')
        signed_url = f"{test_image_url}?{sas}"
        print(f"\nTesting Image URL: {signed_url}")
        
        try:
            head_resp = requests.head(signed_url)
            print(f"Image Access Status: {head_resp.status_code}")
            if head_resp.status_code != 200:
                print(f"❌ ERROR: Cannot access image. Check SAS token permissions/expiry. Reason: {head_resp.reason}")
        except Exception as e:
            print(f"❌ ERROR: Network error while checking image: {e}")

    # Test Azure OpenAI Vision with the PDF URL
    print("\nTesting Azure OpenAI Vision with PDF URL...")
    try:
        resp = client.chat.completions.create(
            model=deployment,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this document?"},
                    {"type": "image_url", "image_url": {"url": signed_url}}
                ]
            }],
            max_tokens=50
        )
        print("✅ SUCCESS: Vision call worked!")
    except Exception as e:
        print(f"❌ ERROR: Vision call failed (Expected for PDF): {e}")
    except Exception as e:
        print(f"❌ ERROR: Azure OpenAI connection failed: {e}")

if __name__ == "__main__":
    test_config()
