# models/user.py
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class User:
    username: str
    created_at: str
    last_active: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'username': self.username,
            'created_at': self.created_at,
            'last_active': self.last_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)
    
    @classmethod
    def create_new(cls, username: str):
        now = datetime.now().isoformat()
        return cls(username=username, created_at=now, last_active=now)