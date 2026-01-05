from app_server.utils.mongodb_utils import get_claim_by_id
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

claim_id = "695b47689b78d486cbc6752d"
claim = get_claim_by_id(claim_id)

if claim:
    print(json.dumps(claim, indent=2, cls=DateTimeEncoder))
else:
    print(f"Claim {claim_id} not found.")
