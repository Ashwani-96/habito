import streamlit as st
import time
import os
import sys
from datetime import datetime

# Initialize settings first
from config.settings import settings
settings.initialize()

# Check if running in cloud
IS_CLOUD = 'STREAMLIT_SERVER_PORT' in os.environ or 'streamlit' in sys.modules

# Import services
from services.ai_service import AIService
from services.habit_service import HabitService
from services.analytics_service import AnalyticsService
from services.export_service import ExportService
from services.auth_service import AuthService
from utils.helpers import get_smart_suggestions, show_help_instructions, check_session_timeout
from utils.constants import COMMON_HABITS

# Only import voice service if not in cloud
if not IS_CLOUD:
    try:
        from services.voice_service import VoiceService
        voice_service = VoiceService()
        VOICE_AVAILABLE = True
    except:
        VOICE_AVAILABLE = False
else:
    VOICE_AVAILABLE = False

# Initialize services
ai_service = AIService()
habit_service = HabitService()
analytics_service = AnalyticsService()
export_service = ExportService()
auth_service = AuthService()

# Streamlit Configuration
st.set_page_config(
    page_title="HabitVoice - Habit Tracker",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
session_vars = {
    'current_user': None,
    'habit_logs': [],
    'habit_goals': {},
    'show_dashboard': False,
    'show_goal_setting': False,
    'show_export': False,
    'pending_action': None,
    'last_save_time': time.time()
}

for var, default_value in session_vars.items():
    if var not in st.session_state:
        st.session_state[var] = default_value

# Main header
st.markdown('<div class="main-header"><h1>🎙️ HabitVoice - Habit Tracker</h1><p>AI-powered habit tracking companion</p></div>', unsafe_allow_html=True)

# Cloud deployment notice
if IS_CLOUD:
    st.info("🌐 **Cloud Mode:** Using text input. Voice commands available in local deployment.")

# User Management Sidebar
with st.sidebar:
    st.header("👤 User Management")
    
    existing_users = auth_service.get_all_users()
    
    if existing_users:
        user_option = st.radio("Choose option:", ["Select User", "New User"])
        
        if user_option == "Select User":
            selected_user = st.selectbox("Select User:", existing_users)
            current_user = selected_user
        else:
            new_user = st.text_input("Enter name:", placeholder="john")
            current_user = new_user.strip().lower() if new_user else None
    else:
        st.info("👋 Welcome! Create your first user:")
        current_user = st.text_input("Enter your name:", placeholder="john").strip().lower()

# Initialize user session
if current_user:
    if st.session_state.current_user != current_user:
        st.session_state.current_user = current_user
        st.session_state.habit_logs = auth_service.load_user_data(current_user)
        st.session_state.habit_goals = auth_service.load_user_goals(current_user)
        st.session_state.show_dashboard = False
    
    # Sidebar user info
    with st.sidebar:
        st.success(f"👤 **Active User:** {current_user.title()}")
        
        # Quick stats
        if st.session_state.habit_logs:
            total_logs = len([log for log in st.session_state.habit_logs if log.get("type") == "log"])
            unique_habits = len(set(log["habit"] for log in st.session_state.habit_logs))
            current_streaks = analytics_service.calculate_streaks(st.session_state.habit_logs)
            max_streak = max(current_streaks.values()) if current_streaks else 0
            
            st.metric("🎯 Total Completed", total_logs)
            st.metric("📚 Active Habits", unique_habits)
            st.metric("🔥 Best Streak", max_streak)
        
        # Smart suggestions
        suggestions = get_smart_suggestions(st.session_state.habit_logs)
        if suggestions:
            st.markdown("### 💡 Suggested Habits")
            suggestion_list = suggestions.get('suggestions', [])
            for habit in suggestion_list[:3]:
                if st.button(f"➕ {habit.title()}", key=f"suggest_{habit}"):
                    habit_service._handle_habit_confirmation(habit, "", "add", current_user)

else:
    st.warning("👤 **Please enter your name in the sidebar to start!**")
    st.stop()

# Check for session timeout
if check_session_timeout(st.session_state):
    st.warning("⏰ Confirmation timeout. Please try again.")

# Main welcome message
st.markdown(f"### Welcome back, **{current_user.title()}**! 👋")

if VOICE_AVAILABLE and not IS_CLOUD:
    st.write("🎤 Use voice commands or type below")
else:
    st.write("📝 Type your commands below (e.g., 'Add reading', 'I did workout', 'Show my progress')")

# Main action buttons
col1, col2, col3, col4 = st.columns(4)

# Text input for commands (works in cloud)
user_input = st.text_input(
    "💬 Type your command:",
    placeholder="e.g., 'Add reading and workout' or 'I did meditation for 10 minutes'",
    key="command_input"
)

if st.button("📝 Submit Command", type="primary", use_container_width=True):
    if user_input:
        with st.spinner("🧠 Processing with AI..."):
            parsed_command = ai_service.parse_voice_command(user_input)
        
        st.write("**🤖 AI Understanding:**")
        st.json(parsed_command.to_dict())
        
        # Handle special intents
        if parsed_command.intent == "streak_query":
            current_streaks = analytics_service.calculate_streaks(st.session_state.habit_logs)
            if parsed_command.habits:
                habit = parsed_command.habits[0]
                if habit in current_streaks:
                    st.info(f"🔥 **{habit.title()}** current streak: **{current_streaks[habit]} days**")
                else:
                    st.info(f"📊 **{habit.title()}** has no active streak. Start logging daily!")
            else:
                if current_streaks:
                    st.info("🔥 **Your Current Streaks:**")
                    for habit, streak in sorted(current_streaks.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"  • **{habit.title()}**: {streak} days")
                else:
                    st.info("📊 No active streaks. Start logging habits daily to build streaks!")
        
        elif parsed_command.intent == "progress_query":
            weekly_progress = analytics_service.check_weekly_progress(st.session_state.habit_logs, st.session_state.habit_goals)
            if weekly_progress:
                st.info("📊 **This Week's Progress:**")
                for habit, progress in weekly_progress.items():
                    status_emoji = "✅" if progress['completed'] >= progress['target'] else "🟡" if progress['completed'] > 0 else "⭕"
                    st.write(f"  {status_emoji} **{habit.title()}**: {progress['completed']}/{progress['target']} ({progress['percentage']:.0f}%)")
            else:
                st.info("🎯 Set some weekly goals to track your progress!")
        
        elif parsed_command.intent == "help":
            show_help_instructions()
        
        elif parsed_command.intent == "export":
            st.session_state.show_export = True
            st.success("💾 Opening export options!")
        
        else:
            habit_service.handle_habit_action(parsed_command.to_dict(), current_user)

# Additional buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 **Dashboard**", use_container_width=True):
        st.session_state.show_dashboard = True

with col2:
    if st.button("🎯 **Set Goals**", use_container_width=True):
        st.session_state.show_goal_setting = True

with col3:
    if st.button("💾 **Export Data**", use_container_width=True):
        st.session_state.show_export = True

# Goal Setting Section
if st.session_state.get('show_goal_setting'):
    st.markdown("---")
    st.subheader("🎯 Set Weekly Goals")
    
    user_habits = list(set(log["habit"] for log in st.session_state.habit_logs))
    
    if user_habits:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_habit = st.selectbox("Choose habit:", user_habits)
            from utils.constants import DEFAULT_GOALS
            goal_target = st.number_input("Times per week:", min_value=1, max_value=14, value=DEFAULT_GOALS.get(selected_habit, 7))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Set Goal", use_container_width=True):
                habit_service.set_habit_goal(current_user, selected_habit, goal_target)
                st.success(f"🎯 Goal set for **{selected_habit}**: {goal_target} times per week")
        
        with col2:
            if st.button("❌ Close", use_container_width=True):
                st.session_state.show_goal_setting = False
                st.rerun()
    else:
        st.info("📝 Start logging some habits first, then set goals for them!")

# Export Section
if st.session_state.get('show_export'):
    st.markdown("---")
    st.subheader("💾 Export Your Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 CSV Export")
        if st.button("Export CSV", use_container_width=True):
            csv_data = export_service.export_to_csv(st.session_state.habit_logs)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"{current_user}_habits_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.markdown("#### 📋 JSON Export")
        if st.button("Export JSON", use_container_width=True):
            json_data = export_service.export_to_json(st.session_state.habit_logs, st.session_state.habit_goals, current_user)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"{current_user}_habits_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col3:
        st.markdown("#### 📈 Progress Report")
        if st.button("Generate Report", use_container_width=True):
            report_data = export_service.generate_progress_report(st.session_state.habit_logs, st.session_state.habit_goals, current_user)
            st.download_button(
                label="⬇️ Download Report",
                data=report_data,
                file_name=f"{current_user}_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    if st.button("❌ Close Export", use_container_width=True):
        st.session_state.show_export = False
        st.rerun()

# Dashboard Section
if st.session_state.get('show_dashboard'):
    st.markdown("---")
    analytics_service.show_comprehensive_dashboard(st.session_state.habit_logs, st.session_state.habit_goals, current_user)
    
    if st.button("❌ Close Dashboard"):
        st.session_state.show_dashboard = False
        st.rerun()

# Recent Activity
elif st.session_state.habit_logs and not any([
    st.session_state.get('show_goal_setting'),
    st.session_state.get('show_export')
]):
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_logs = len([log for log in st.session_state.habit_logs if log.get("type") == "log"])
        st.metric("📈 Total Completions", total_logs)
    
    with col2:
        unique_habits = len(set(log["habit"] for log in st.session_state.habit_logs))
        st.metric("🎯 Active Habits", unique_habits)
    
    with col3:
        today = datetime.now().strftime("%Y-%m-%d")
        today_logs = len([log for log in st.session_state.habit_logs if log["time"].startswith(today)])
        st.metric("📅 Today", today_logs)
    
    with col4:
        current_streaks = analytics_service.calculate_streaks(st.session_state.habit_logs)
        max_streak = max(current_streaks.values()) if current_streaks else 0
        st.metric("🔥 Best Streak", max_streak)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📜 Recent Activity")
        recent_logs = st.session_state.habit_logs[-8:]
        
        for log in reversed(recent_logs):
            icon = "✅" if log.get("type") == "log" else "➕" if log.get("type") == "add" else "📝"
            timestamp = datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S").strftime("%m/%d %H:%M")
            st.markdown(f"{icon} **{log['action']}** _{timestamp}_")
    
    with col2:
        st.subheader("🔥 Current Streaks")
        if current_streaks:
            for habit, streak in sorted(current_streaks.items(), key=lambda x: x[1], reverse=True)[:5]:
                st.metric(f"{habit.title()}", f"{streak} days")
        else:
            st.info("Start logging daily! 🎯")

elif not st.session_state.habit_logs:
    st.markdown("---")
    st.info("🎯 **Welcome to HabitVoice!** Start by typing something like:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📝 **Try These Commands:**
        - *"Add reading and workout"*
        - *"I did meditation for 10 minutes"*
        - *"Set goal for reading 7 times per week"*
        - *"Show my progress"*
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 **Popular Starter Habits:**
        - Reading 📚
        - Workout 💪
        - Meditation 🧘
        - Journaling ✍️
        - Drinking Water 💧
        """)

# Auto-save
current_time = time.time()
if current_time - st.session_state.last_save_time > 300:
    if st.session_state.habit_logs:
        auth_service.save_user_data(current_user, st.session_state.habit_logs)
        auth_service.save_user_goals(current_user, st.session_state.habit_goals)
        st.session_state.last_save_time = current_time

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🎙️ <strong>HabitVoice</strong> - Your AI-powered habit tracking companion</p>
    <p>Built with ❤️ using Streamlit & OpenAI</p>
</div>
""", unsafe_allow_html=True)

with st.expander("💡 Need Help?"):
    show_help_instructions()