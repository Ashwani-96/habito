# utils/helpers.py
import streamlit as st
from typing import List, Dict, Any
from utils.constants import HABIT_CATEGORIES, COMMON_HABITS

def get_habit_category(habit: str) -> str:
    for category, habits in HABIT_CATEGORIES.items():
        if habit in habits:
            return category
    return "🔄 Other"

def get_smart_suggestions(habit_logs: List[dict]) -> Dict[str, Any]:
    if not habit_logs:
        return {
            "suggestions": ["reading", "workout", "meditating", "journaling", "drinking water"],
            "reason": "Popular habits for beginners"
        }
    
    user_habits = set(log["habit"] for log in habit_logs if log.get("type") == "log")
    
    if not user_habits:
        return {
            "suggestions": ["reading", "workout", "meditating"],
            "reason": "Recommended starter habits"
        }
    
    suggestions = []
    user_categories = set()
    
    for habit in user_habits:
        category = get_habit_category(habit)
        user_categories.add(category)
    
    for category in user_categories:
        if category in HABIT_CATEGORIES:
            for habit in HABIT_CATEGORIES[category]:
                if habit not in user_habits and habit not in suggestions:
                    suggestions.append(habit)
                    if len(suggestions) >= 3:
                        break
    
    popular_habits = ["reading", "workout", "meditating", "journaling", "drinking water"]
    for habit in popular_habits:
        if habit not in user_habits and habit not in suggestions:
            suggestions.append(habit)
            if len(suggestions) >= 5:
                break
    
    return {
        "suggestions": suggestions[:5],
        "reason": "Based on your habits"
    }

def show_help_instructions():
    st.markdown("## 💡 HabitVoice Help & Instructions")
    
    with st.expander("🎤 Voice Commands", expanded=True):
        st.markdown("""
        ### 📊 **Dashboard & Progress:**
        - *"Show my progress"* - Open comprehensive dashboard
        - *"Show dashboard"* - View all analytics
        - *"How am I doing?"* - Quick progress overview
        - *"What's my reading streak?"* - Check specific habit streak
        - *"Show my weekly progress"* - View goal progress
        
        ### ➕ **Adding Habits:**
        - *"Add reading and workout"* - Add multiple habits
        - *"Create meditation habit"* - Add single habit
        
        ### ✅ **Logging Activities:**
        - *"I did reading for 1 hour"* - Log with duration
        - *"Completed workout and meditation"* - Log multiple
        - *"Finished yoga"* - Simple completion
        
        ### 🎯 **Goal Setting:**
        - *"Set goal for reading 5 times per week"* - Set weekly target
        
        ### 🗑️ **Deleting Habits:**
        - *"Delete workout"* - Remove habit
        
        ### 💾 **Data Management:**
        - *"Export my data"* - Download backup
        - *"Help"* - Show this help
        """)
    
    with st.expander("🎯 Supported Habits"):
        for category, habits in HABIT_CATEGORIES.items():
            st.markdown(f"**{category}**: {', '.join(habits)}")

def check_session_timeout(session_state) -> bool:
    import time
    if hasattr(session_state, 'pending_action') and session_state.pending_action:
        if isinstance(session_state.pending_action, dict):
            if time.time() - session_state.pending_action.get('timestamp', 0) > 300:
                session_state.pending_action = None
                return True
    return False