# services/ai_service.py
import re
import json
import streamlit as st
from typing import Dict, Any
from config.settings import settings
from utils.constants import COMMON_HABITS, GOAL_PATTERNS, STREAK_KEYWORDS, PROGRESS_KEYWORDS, DASHBOARD_KEYWORDS
from models.habit import VoiceCommand

# OpenAI Setup
try:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    OPENAI_VERSION = "new"
except ImportError:
    import openai
    openai.api_key = settings.OPENAI_API_KEY
    OPENAI_VERSION = "legacy"

class AIService:
    def __init__(self):
        self.client = client if OPENAI_VERSION == "new" else None
    
    def parse_voice_command(self, raw_text: str) -> VoiceCommand:
        """Parse voice command using enhanced AI parsing"""
        try:
            # Try enhanced parsing first
            parsed_data = self._enhanced_voice_parsing(raw_text)
            return VoiceCommand(**parsed_data)
        except Exception as e:
            if settings.DEBUG:
                st.warning(f"⚠️ AI parsing failed: {e}. Using fallback.")
            return VoiceCommand(**self._simple_parse(raw_text))
    
    def _enhanced_voice_parsing(self, raw_text: str) -> Dict[str, Any]:
        """Enhanced voice command parsing with multiple intents"""
        text_lower = raw_text.lower().strip()
        
        # Goal setting patterns
        for pattern in GOAL_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                habit, target = match.groups()
                if habit in COMMON_HABITS:
                    return {
                        "intent": "set_goal",
                        "habits": [habit],
                        "target": int(target),
                        "duration": ""
                    }
        
        # Streak query patterns
        if any(keyword in text_lower for keyword in STREAK_KEYWORDS):
            for habit in COMMON_HABITS:
                if habit in text_lower:
                    return {"intent": "streak_query", "habits": [habit], "duration": "", "target": 0}
            return {"intent": "streak_query", "habits": [], "duration": "", "target": 0}
        
        # Progress query patterns
        if any(keyword in text_lower for keyword in PROGRESS_KEYWORDS):
            return {"intent": "progress_query", "habits": [], "duration": "", "target": 0}
        
        # Dashboard patterns
        if any(keyword in text_lower for keyword in DASHBOARD_KEYWORDS):
            return {"intent": "dashboard", "habits": [], "duration": "", "target": 0}
        
        # Confirmation responses
        if any(word in text_lower for word in ["yes", "confirm", "correct", "that's right", "yep"]):
            return {"intent": "confirm", "habits": [], "duration": "", "target": 0}
        
        if any(word in text_lower for word in ["no", "cancel", "wrong", "not correct", "nope"]):
            return {"intent": "cancel", "habits": [], "duration": "", "target": 0}
        
        # Help/instructions
        if any(word in text_lower for word in ["help", "how to use", "instructions", "what can i say"]):
            return {"intent": "help", "habits": [], "duration": "", "target": 0}
        
        # Export data
        if any(word in text_lower for word in ["export", "download", "backup", "save data"]):
            return {"intent": "export", "habits": [], "duration": "", "target": 0}
        
        # Fall back to OpenAI parsing
        return self._call_openai_parse(raw_text)
    
    def _call_openai_parse(self, raw_text: str) -> Dict[str, Any]:
        """Enhanced OpenAI parsing with better prompts"""
        try:
            prompt = f"""
            Parse this voice command for a habit tracker: "{raw_text}"
            
            Available habits: {', '.join(COMMON_HABITS)}
            
            Return JSON with these fields:
            - intent: 'add', 'log', 'delete', 'query', 'dashboard', 'set_goal', 'streak_query', 'progress_query'
            - habits: list of habit names (only from available habits)
            - duration: time mentioned (e.g., "1 hour", "30 minutes") or empty string
            - target: number for goal setting, or 0
            
            Intent guidelines:
            - 'add': "add reading", "create workout habit"
            - 'log': "I did reading", "completed workout", "finished meditation for 1 hour"
            - 'delete': "delete reading", "remove workout"
            - 'query': "show reading logs", "check workout progress"
            - 'dashboard': "show progress", "my stats", "dashboard"
            - 'set_goal': "goal for reading is 5 per week"
            - 'streak_query': "what's my reading streak"
            - 'progress_query': "how am I doing this week"
            
            Examples:
            {{"intent": "log", "habits": ["reading"], "duration": "1 hour", "target": 0}}
            {{"intent": "set_goal", "habits": ["workout"], "duration": "", "target": 5}}
            {{"intent": "dashboard", "habits": [], "duration": "", "target": 0}}
            """

            messages = [
                {"role": "system", "content": "You are a habit tracking assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ]

            if OPENAI_VERSION == "new":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=200
                )
                response_text = response.choices[0].message.content.strip()
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=200
                )
                response_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            if response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            data = json.loads(response_text)
            
            # Validate and filter habits
            if "habits" in data:
                data["habits"] = [h.lower().strip() for h in data["habits"] if h.strip()]
                data["habits"] = [h for h in data["habits"] if h in COMMON_HABITS]
            
            # Ensure all required fields exist
            data.setdefault("target", 0)
            data.setdefault("duration", "")
            
            return data
        
        except Exception as e:
            if settings.DEBUG:
                st.warning(f"⚠️ OpenAI parsing failed: {e}. Using simple parsing.")
            return self._simple_parse(raw_text)
    
    def _simple_parse(self, text: str) -> Dict[str, Any]:
        """Simple fallback parsing"""
        text_lower = text.lower()
        
        # Check intents
        if any(word in text_lower for word in DASHBOARD_KEYWORDS):
            return {"intent": "dashboard", "habits": [], "duration": "", "target": 0}
        elif "add" in text_lower or "create" in text_lower:
            intent = "add"
            target = 0
        elif "delete" in text_lower or "remove" in text_lower:
            intent = "delete"
            target = 0
        elif "goal" in text_lower and any(char.isdigit() for char in text_lower):
            intent = "set_goal"
            # Extract number for target
            numbers = re.findall(r'\d+', text_lower)
            target = int(numbers[0]) if numbers else 7
        else:
            intent = "log"
            target = 0
        
        # Find habits
        habits = [habit for habit in COMMON_HABITS if habit in text_lower]
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(hour|minute|min)s?', text_lower)
        duration = duration_match.group(0) if duration_match else ""
        
        return {
            "intent": intent, 
            "habits": habits, 
            "duration": duration,
            "target": target
        }