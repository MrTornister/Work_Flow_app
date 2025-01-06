from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.auth.security import SecurityConfig
from src.auth.session import SessionConfig, get_session_data, SessionData
from datetime import datetime
import time

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = SecurityConfig.get_security_headers()
        for key, value in headers.items():
            response.headers[key] = value
        return response

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_data = get_session_data(request)
        if session_data:
            now = datetime.utcnow()
            session_data.last_activity = now
            request.session["session"] = session_data.to_dict()
        return await call_next(request)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old requests
        self.requests = {ip: times for ip, times in self.requests.items()
                        if current_time - times[-1] < 60}
        
        if client_ip in self.requests:
            times = self.requests[client_ip]
            if len(times) >= self.requests_per_minute:
                if current_time - times[0] < 60:
                    return Response(status_code=429, content="Too many requests")
                times.pop(0)
            times.append(current_time)
        else:
            self.requests[client_ip] = [current_time]
            
        return await call_next(request)

# Export middleware classes
security_middleware = SecurityMiddleware
rate_limit_middleware = RateLimitMiddleware
session_middleware = SessionMiddleware
error_handler_middleware = None  # Implement if needed