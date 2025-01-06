from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Dict, List
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests: Dict[str, List[datetime]] = {}
        self.rate_limit = requests_per_minute
        self.window = timedelta(minutes=1)
        
    def check_rate_limit(self, client_id: str) -> bool:
        now = datetime.now()
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        
        if len(self.requests[client_id]) >= self.rate_limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
            
        self.requests[client_id].append(now)
        return True