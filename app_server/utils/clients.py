
import os
from pymongo import MongoClient
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Clients
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Abhijit:RStoKAluIWB4x1Pg@cluster0.zvgvv7n.mongodb.net/")
mongo_client = MongoClient(MONGO_URI)
DB_NAME = os.getenv("DB_NAME", "insurance_ai")
db = mongo_client[DB_NAME]

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY") # Matches .env variable name
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")

azure_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview" # Standard version for vision
)
