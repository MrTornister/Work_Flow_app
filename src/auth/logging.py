from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import json

class AuthLogger:
    def __init__(self):
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.lockout_duration = timedelta(minutes=15)
        self.max_attempts = 5
        
        # Configure logging
        logging.basicConfig(
            filename='auth.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger('auth')
    
    def log_failed_attempt(self, username: str, ip_address: str):
        current_time = datetime.utcnow()
        
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
            
        self.failed_attempts[username].append(current_time)
        logging.warning(f"Failed login attempt for user {username} from IP {ip_address}")
        
    def is_account_locked(self, username: str) -> bool:
        if username not in self.failed_attempts:
            return False
            
        recent_attempts = [
            attempt for attempt in self.failed_attempts[username]
            if datetime.utcnow() - attempt < self.lockout_duration
        ]
        
        return len(recent_attempts) >= self.max_attempts

class SecurityLogger:
    def __init__(self):
        logging.basicConfig(
            filename='security.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger('security')

    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "severity": severity,
            "details": details
        }
        self.logger.log(
            logging.INFO if severity == "INFO" else logging.WARNING,
            json.dumps(event)
        )

    def log_auth_attempt(self, username: str, success: bool, ip_address: str):
        self.log_security_event(
            "authentication_attempt",
            {
                "username": username,
                "success": success,
                "ip_address": ip_address
            },
            "INFO" if success else "WARNING"
        )