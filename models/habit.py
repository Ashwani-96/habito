# models/habit.py
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Habit:
    habit: str
    action: str
    time: str
    type: str
    duration: str = ""
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'habit': self.habit,
            'action': self.action,
            'time': self.time,
            'type': self.type,
            'duration': self.duration,
            'user_id': self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

@dataclass
class HabitGoal:
    habit: str
    target_per_week: int
    created: str
    category: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'target_per_week': self.target_per_week,
            'created': self.created,
            'category': self.category
        }
    
    @classmethod
    def from_dict(cls, habit: str, data: Dict[str, Any]):
        return cls(habit=habit, **data)

@dataclass
class VoiceCommand:
    intent: str
    habits: list
    duration: str = ""
    target: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'intent': self.intent,
            'habits': self.habits,
            'duration': self.duration,
            'target': self.target
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)