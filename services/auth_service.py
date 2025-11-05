# services/auth_service.py
import os
import json
from typing import List, Optional
from config.settings import settings
from models.user import User
from models.habit import Habit, HabitGoal

class AuthService:
    def __init__(self):
        self.users_dir = settings.USERS_DATA_DIR
    
    def get_user_file(self, username: str) -> str:
        """Get the file path for user's habit data"""
        return os.path.join(self.users_dir, f"{username}_habits.json")

    def get_goals_file(self, username: str) -> str:
        """Get the file path for user's goals"""
        return os.path.join(self.users_dir, f"{username}_goals.json")

    def load_user_data(self, username: str) -> List[dict]:
        """Load user's habit data from file"""
        user_file = self.get_user_file(username)
        if os.path.exists(user_file):
            try:
                with open(user_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_user_data(self, username: str, data: List[dict]) -> bool:
        """Save user's habit data to file"""
        user_file = self.get_user_file(username)
        try:
            with open(user_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            if settings.DEBUG:
                print(f"Save failed: {e}")
            return False

    def load_user_goals(self, username: str) -> dict:
        """Load user's goals from file"""
        goals_file = self.get_goals_file(username)
        if os.path.exists(goals_file):
            try:
                with open(goals_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_user_goals(self, username: str, goals: dict) -> bool:
        """Save user's goals to file"""
        goals_file = self.get_goals_file(username)
        try:
            with open(goals_file, 'w') as f:
                json.dump(goals, f, indent=2)
            return True
        except Exception as e:
            if settings.DEBUG:
                print(f"Goals save failed: {e}")
            return False

    def get_all_users(self) -> List[str]:
        """Get list of all registered users"""
        users = []
        if os.path.exists(self.users_dir):
            for filename in os.listdir(self.users_dir):
                if filename.endswith('_habits.json'):
                    username = filename.replace('_habits.json', '')
                    users.append(username)
        return sorted(users)

    def create_user(self, username: str) -> bool:
        """Create a new user"""
        try:
            self.save_user_data(username, [])
            self.save_user_goals(username, {})
            return True
        except:
            return False