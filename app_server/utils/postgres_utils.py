
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """
    Creates and returns a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return None

def fetch_policy_by_number(policy_number: str):
    """
    Fetches policy details from PostgreSQL using policyNumber.
    """
    query = "SELECT * FROM public.policy WHERE \"policyNumber\" = %s"
    
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (policy_number,))
            policy = cur.fetchone()
            return policy
    except Exception as e:
        print(f"❌ Error fetching policy {policy_number}: {e}")
        return None
    finally:
        conn.close()
