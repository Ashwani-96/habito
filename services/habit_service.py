# services/habit_service.py
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
from services.auth_service import AuthService
from utils.constants import COMMON_HABITS, DEFAULT_GOALS
from utils.helpers import get_habit_category

class HabitService:
    def __init__(self):
        self.auth_service = AuthService()
    
    def handle_habit_action(self, command_data: Dict[str, Any], current_user: str):
        """Process habit commands with confirmation system"""
        intent = command_data.get("intent", "log")
        habits = command_data.get("habits", [])
        duration = command_data.get("duration", "")
        target = command_data.get("target", 0)
        
        # Handle different intents
        if intent == "dashboard":
            st.session_state.show_dashboard = True
            st.success("📊 Opening your comprehensive dashboard!")
            return
        
        elif intent == "set_goal":
            if habits and target > 0:
                habit = habits[0]
                self.set_habit_goal(current_user, habit, target)
                st.success(f"🎯 Set goal for **{habit}**: {target} times per week")
            else:
                st.warning("⚠️ Please specify a habit and target number for goal setting.")
            return
        
        elif intent in ["streak_query", "progress_query", "help", "export", "confirm", "cancel"]:
            # Handle these in the analytics service or main app
            return intent, command_data
        
        # Handle habit-related actions with confirmation
        if not habits:
            st.warning("⚠️ No valid habits recognized. Try mentioning: " + ", ".join(COMMON_HABITS[:5]) + "...")
            return
        
        # For habit actions, show confirmation
        habit = habits[0]  # Take first habit for simplicity
        
        if intent in ["add", "log", "delete"]:
            self._handle_habit_confirmation(habit, duration, intent, current_user)
        else:
            # Direct execution for query
            if intent == "query":
                self._query_habit(habit, current_user)
    
    def _handle_habit_confirmation(self, habit: str, duration: str = "", action_type: str = "log", user: str = ""):
        """Show confirmation dialog for habit actions"""
        if action_type == "log":
            action_text = f"Completed {habit}"
            if duration:
                action_text += f" for {duration}"
            icon = "✅"
        elif action_type == "add":
            action_text = f"Add {habit} to your habits"
            icon = "➕"
        elif action_type == "delete":
            action_text = f"Delete {habit} and all its logs"
            icon = "🗑️"
        else:
            action_text = f"{action_type} {habit}"
            icon = "🔄"
        
        st.session_state.pending_action = {
            'habit': habit,
            'duration': duration,
            'action_text': action_text,
            'action_type': action_type,
            'user': user,
            'timestamp': datetime.now().timestamp()
        }
        
        st.warning(f"🤔 **Confirm Action:**\n{icon} {action_text}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, do it!", key="confirm_yes", use_container_width=True):
                self._execute_confirmed_action()
        
        with col2:
            if st.button("❌ No, cancel", key="confirm_no", use_container_width=True):
                st.session_state.pop('pending_action', None)
                st.info("❌ Action cancelled")
                st.rerun()
    
    def _execute_confirmed_action(self):
        """Execute the confirmed action"""
        if 'pending_action' not in st.session_state:
            return
        
        action = st.session_state.pending_action
        habit = action['habit']
        duration = action['duration']
        action_type = action['action_type']
        user = action['user']
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if action_type == "log":
            action_text = f"Completed {habit}"
            if duration:
                action_text += f" for {duration}"
            
            st.session_state.habit_logs.append({
                "habit": habit,
                "action": action_text,
                "time": now,
                "type": "log",
                "duration": duration
            })
            st.success(f"✅ Logged: **{action_text}**")
            
        elif action_type == "add":
            existing_habits = [log["habit"] for log in st.session_state.habit_logs]
            if habit not in existing_habits:
                st.session_state.habit_logs.append({
                    "habit": habit,
                    "action": f"Added habit: {habit}",
                    "time": now,
                    "type": "add"
                })
                st.success(f"➕ Added habit: **{habit}**")
                
                # Set default goal if available
                if habit in DEFAULT_GOALS:
                    self.set_habit_goal(user, habit, DEFAULT_GOALS[habit])
                    st.info(f"🎯 Set default goal: {DEFAULT_GOALS[habit]} times per week")
            else:
                st.info(f"ℹ️ **{habit}** already exists in your habits!")
        
        elif action_type == "delete":
            initial_count = len(st.session_state.habit_logs)
            st.session_state.habit_logs = [
                log for log in st.session_state.habit_logs 
                if log["habit"] != habit
            ]
            removed_count = initial_count - len(st.session_state.habit_logs)
            
            if removed_count > 0:
                st.success(f"🗑️ Deleted **{habit}** ({removed_count} entries removed)")
                # Also remove from goals
                if 'habit_goals' in st.session_state and habit in st.session_state.habit_goals:
                    del st.session_state.habit_goals[habit]
                    self.auth_service.save_user_goals(user, st.session_state.habit_goals)
            else:
                st.warning(f"⚠️ No entries found for **{habit}**")
        
        # Save data and clean up
        self.auth_service.save_user_data(user, st.session_state.habit_logs)
        st.session_state.pop('pending_action', None)
        
        # Auto-rerun to update UI
        st.rerun()
    
    def set_habit_goal(self, user: str, habit: str, target_per_week: int = 7):
        """Set weekly goal for a habit"""
        if 'habit_goals' not in st.session_state:
            st.session_state.habit_goals = self.auth_service.load_user_goals(user)
        
        st.session_state.habit_goals[habit] = {
            'target_per_week': target_per_week,
            'created': datetime.now().isoformat(),
            'category': get_habit_category(habit)
        }
        
        # Save to file
        self.auth_service.save_user_goals(user, st.session_state.habit_goals)
    
    def _query_habit(self, habit: str, user: str):
        """Query specific habit logs"""
        logs = [log for log in st.session_state.habit_logs if habit in log["habit"]]
        if logs:
            st.info(f"📊 **{habit.title()}** - Found {len(logs)} entries:")
            for log in logs[-5:]:
                st.write(f"  • {log['action']} - {log['time']}")
        else:
            st.warning(f"❌ No records found for **{habit}**")