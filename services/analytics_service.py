# services/analytics_service.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from collections import Counter
from typing import Dict, List
from utils.helpers import get_habit_category
from utils.constants import HABIT_CATEGORIES

class AnalyticsService:
    def calculate_streaks(self, habit_logs: List[dict]) -> Dict[str, int]:
        """Calculate current streaks for each habit"""
        if not habit_logs:
            return {}
        
        streaks = {}
        today = date.today()
        
        # Get all unique habits that have been logged
        logged_habits = [log for log in habit_logs if log.get("type") == "log"]
        unique_habits = set(log["habit"] for log in logged_habits)
        
        for habit in unique_habits:
            # Get all dates this habit was logged
            habit_dates = []
            for log in logged_habits:
                if log["habit"] == habit:
                    try:
                        log_date = datetime.strptime(log["time"][:10], "%Y-%m-%d").date()
                        habit_dates.append(log_date)
                    except:
                        continue
            
            # Remove duplicates and sort in descending order
            habit_dates = sorted(set(habit_dates), reverse=True)
            
            # Calculate consecutive streak from today backwards
            streak = 0
            current_date = today
            
            for habit_date in habit_dates:
                if habit_date == current_date:
                    streak += 1
                    current_date -= timedelta(days=1)
                elif habit_date < current_date:
                    # There's a gap, check if it's just yesterday
                    if current_date - habit_date == timedelta(days=1) and streak == 0:
                        # Yesterday's habit, start streak from yesterday
                        streak = 1
                        current_date = habit_date - timedelta(days=1)
                    else:
                        break
            
            if streak > 0:
                streaks[habit] = streak
        
        return streaks

    def get_longest_streaks(self, habit_logs: List[dict]) -> Dict[str, int]:
        """Calculate longest streaks for each habit"""
        if not habit_logs:
            return {}
        
        longest_streaks = {}
        logged_habits = [log for log in habit_logs if log.get("type") == "log"]
        unique_habits = set(log["habit"] for log in logged_habits)
        
        for habit in unique_habits:
            # Get all dates this habit was logged
            habit_dates = []
            for log in logged_habits:
                if log["habit"] == habit:
                    try:
                        log_date = datetime.strptime(log["time"][:10], "%Y-%m-%d").date()
                        habit_dates.append(log_date)
                    except:
                        continue
            
            # Sort dates
            habit_dates = sorted(set(habit_dates))
            
            # Find longest consecutive streak
            if not habit_dates:
                continue
                
            max_streak = 1
            current_streak = 1
            
            for i in range(1, len(habit_dates)):
                if habit_dates[i] - habit_dates[i-1] == timedelta(days=1):
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
            
            longest_streaks[habit] = max_streak
        
        return longest_streaks

    def check_weekly_progress(self, habit_logs: List[dict], habit_goals: Dict[str, dict]) -> Dict[str, dict]:
        """Check progress towards weekly goals"""
        if not habit_goals:
            return {}
        
        # Get this week's start (Monday)
        today = datetime.now()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count completions this week
        weekly_counts = {}
        for log in habit_logs:
            if log.get("type") == "log":
                try:
                    log_datetime = datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S")
                    if log_datetime >= week_start:
                        habit = log["habit"]
                        weekly_counts[habit] = weekly_counts.get(habit, 0) + 1
                except:
                    continue
        
        # Calculate progress for each goal
        progress = {}
        for habit, goal_data in habit_goals.items():
            completed = weekly_counts.get(habit, 0)
            target = goal_data['target_per_week']
            percentage = min(100, (completed / target) * 100) if target > 0 else 0
            
            progress[habit] = {
                'completed': completed,
                'target': target,
                'percentage': percentage,
                'status': 'completed' if completed >= target else 'in_progress' if completed > 0 else 'not_started'
            }
        
        return progress

    def show_comprehensive_dashboard(self, habit_logs: List[dict], habit_goals: Dict[str, dict], current_user: str):
        """Show comprehensive dashboard with all metrics and visualizations"""
        if not habit_logs:
            st.warning("📊 No data to display yet. Start logging some habits!")
            return
        
        st.header(f"📊 {current_user.title()}'s Complete Progress Dashboard")
        st.markdown("---")
        
        # Prepare data
        df = pd.DataFrame(habit_logs)
        df['time'] = pd.to_datetime(df['time'])
        df['date'] = df['time'].dt.date
        
        # Filter logged habits
        logged_habits = df[df['type'] == 'log'].copy() if 'type' in df.columns else df.copy()
        
        if logged_habits.empty:
            st.warning("📈 No completed habits to analyze yet!")
            return
        
        # Key metrics
        self._show_key_metrics(logged_habits)
        
        # Streaks section
        self._show_streaks_section(habit_logs)
        
        # Goals progress
        self._show_goals_progress(habit_logs, habit_goals)
        
        # Habit analysis
        self._show_habit_analysis(logged_habits)
        
        # Time analysis
        self._show_time_analysis(logged_habits)
        
        # Category analysis
        self._show_category_analysis(logged_habits)
        
        # Achievements
        self._show_achievements(logged_habits, habit_logs)

    def _show_key_metrics(self, logged_habits: pd.DataFrame):
        """Show key metrics row"""
        st.subheader("🎯 Key Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_completions = len(logged_habits)
            st.metric("📈 Total Completions", total_completions)
        
        with col2:
            unique_habits = logged_habits['habit'].nunique()
            st.metric("📚 Active Habits", unique_habits)
        
        with col3:
            days_active = logged_habits['date'].nunique()
            st.metric("📅 Days Active", days_active)
        
        with col4:
            current_streaks = self.calculate_streaks(st.session_state.habit_logs)
            total_streak = sum(current_streaks.values())
            st.metric("🔥 Total Streak Days", total_streak)
        
        with col5:
            if days_active > 0:
                avg_per_day = round(total_completions / days_active, 1)
            else:
                avg_per_day = 0
            st.metric("⚡ Avg/Day", avg_per_day)
        
        st.markdown("---")

    def _show_streaks_section(self, habit_logs: List[dict]):
        """Show streak analysis section"""
        st.subheader("🔥 Streak Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Current Streaks")
            current_streaks = self.calculate_streaks(habit_logs)
            if current_streaks:
                streak_df = pd.DataFrame(list(current_streaks.items()), columns=['Habit', 'Current Streak'])
                streak_df = streak_df.sort_values('Current Streak', ascending=False)
                
                fig_current = px.bar(
                    streak_df, 
                    x='Current Streak', 
                    y='Habit',
                    orientation='h',
                    title="Current Active Streaks",
                    color='Current Streak',
                    color_continuous_scale='Reds'
                )
                fig_current.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_current, use_container_width=True)
            else:
                st.info("🎯 No active streaks. Start logging daily to build streaks!")
        
        with col2:
            st.markdown("#### Longest Streaks")
            longest_streaks = self.get_longest_streaks(habit_logs)
            if longest_streaks:
                longest_df = pd.DataFrame(list(longest_streaks.items()), columns=['Habit', 'Longest Streak'])
                longest_df = longest_df.sort_values('Longest Streak', ascending=False)
                
                fig_longest = px.bar(
                    longest_df, 
                    x='Longest Streak', 
                    y='Habit',
                    orientation='h',
                    title="Personal Best Streaks",
                    color='Longest Streak',
                    color_continuous_scale='Greens'
                )
                fig_longest.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_longest, use_container_width=True)
            else:
                st.info("📊 Streak records will appear as you build longer streaks!")

    def _show_goals_progress(self, habit_logs: List[dict], habit_goals: Dict[str, dict]):
        """Show weekly goals progress"""
        st.subheader("🎯 Weekly Goals Progress")
        weekly_progress = self.check_weekly_progress(habit_logs, habit_goals)
        
        if weekly_progress:
            goal_data = []
            for habit, progress in weekly_progress.items():
                goal_data.append({
                    'Habit': habit.title(),
                    'Completed': progress['completed'],
                    'Target': progress['target'],
                    'Progress %': progress['percentage'],
                    'Status': progress['status']
                })
            
            goal_df = pd.DataFrame(goal_data)
            
            # Progress bars
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_goals = px.bar(
                    goal_df,
                    x='Habit',
                    y=['Completed', 'Target'],
                    title="This Week's Progress vs Goals",
                    barmode='group',
                    color_discrete_map={'Completed': '#2E8B57', 'Target': '#FFA500'}
                )
                fig_goals.update_layout(height=400)
                st.plotly_chart(fig_goals, use_container_width=True)
            
            with col2:
                st.markdown("#### Goal Status")
                for _, row in goal_df.iterrows():
                    status_color = {
                        'completed': '🟢',
                        'in_progress': '🟡', 
                        'not_started': '🔴'
                    }.get(row['Status'], '⚪')
                    
                    st.markdown(f"{status_color} **{row['Habit']}**: {row['Completed']}/{row['Target']} ({row['Progress %']:.0f}%)")
        else:
            st.info("🎯 Set some weekly goals to track your progress!")

    def _show_habit_analysis(self, logged_habits: pd.DataFrame):
        """Show habit completion analysis"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Habit Distribution")
            habit_counts = logged_habits['habit'].value_counts()
            
            fig_pie = px.pie(
                values=habit_counts.values,
                names=habit_counts.index,
                title="Completion Distribution"
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Top Habits")
            top_habits = habit_counts.head(10)
            
            fig_bar = px.bar(
                x=top_habits.values,
                y=top_habits.index,
                orientation='h',
                title="Most Completed Habits",
                color=top_habits.values,
                color_continuous_scale="viridis"
            )
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    def _show_time_analysis(self, logged_habits: pd.DataFrame):
        """Show time-based analysis"""
        st.subheader("📅 Time-based Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily activity over time
            st.markdown("#### Daily Activity Trend")
            daily_counts = logged_habits.groupby('date').size().reset_index(name='count')
            daily_counts['date'] = pd.to_datetime(daily_counts['date'])
            
            fig_daily = px.line(
                daily_counts,
                x='date',
                y='count',
                title="Daily Habit Completions",
                markers=True
            )
            fig_daily.update_layout(height=300)
            st.plotly_chart(fig_daily, use_container_width=True)
        
        with col2:
            # Day of week analysis
            st.markdown("#### Best Days of Week")
            logged_habits['day_of_week'] = logged_habits['time'].dt.day_name()
            day_counts = logged_habits['day_of_week'].value_counts()
            
            # Reorder days
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = day_counts.reindex(day_order, fill_value=0)
            
            fig_day = px.bar(
                x=day_counts.index,
                y=day_counts.values,
                title="Most Productive Days",
                color=day_counts.values,
                color_continuous_scale="blues"
            )
            fig_day.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_day, use_container_width=True)

    def _show_category_analysis(self, logged_habits: pd.DataFrame):
        """Show habit categories analysis"""
        st.subheader("📚 Habit Categories")
        
        category_counts = {}
        for _, row in logged_habits.iterrows():
            category = get_habit_category(row['habit'])
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_cat_pie = px.pie(
                    values=list(category_counts.values()),
                    names=list(category_counts.keys()),
                    title="Habits by Category"
                )
                st.plotly_chart(fig_cat_pie, use_container_width=True)
            
            with col2:
                fig_cat_bar = px.bar(
                    x=list(category_counts.values()),
                    y=list(category_counts.keys()),
                    orientation='h',
                    title="Category Completion Count",
                    color=list(category_counts.values()),
                    color_continuous_scale="plasma"
                )
                fig_cat_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_cat_bar, use_container_width=True)

    def _show_achievements(self, logged_habits: pd.DataFrame, all_logs: List[dict]):
        """Show achievements and milestones"""
        st.subheader("🏅 Achievements & Milestones")
        
        achievements = []
        
        total_completions = len(logged_habits)
        unique_habits = logged_habits['habit'].nunique()
        days_active = logged_habits['date'].nunique()
        current_streaks = self.calculate_streaks(all_logs)
        max_streak = max(current_streaks.values()) if current_streaks else 0
        
        # Calculate achievements
        if total_completions >= 10:
            achievements.append("🎯 Completed 10+ habits!")
        if total_completions >= 50:
            achievements.append("🏆 Habit Champion - 50+ completions!")
        if total_completions >= 100:
            achievements.append("🌟 Habit Master - 100+ completions!")
        
        if unique_habits >= 5:
            achievements.append("📚 Multi-tasker - Tracking 5+ habits!")
        if unique_habits >= 10:
            achievements.append("🎨 Diverse Tracker - 10+ different habits!")
        
        if days_active >= 7:
            achievements.append("📅 Week Warrior - Active for 7+ days!")
        if days_active >= 30:
            achievements.append("🗓️ Monthly Master - Active for 30+ days!")
        
        if max_streak >= 7:
            achievements.append("🔥 Week Streak - 7+ day streak!")
        if max_streak >= 21:
            achievements.append("⚡ Habit Formation - 21+ day streak!")
        if max_streak >= 66:
            achievements.append("💎 Diamond Streak - 66+ day streak!")
        
        if achievements:
            cols = st.columns(min(len(achievements), 3))
            for i, achievement in enumerate(achievements):
                with cols[i % 3]:
                    st.success(achievement)
        else:
            st.info("🎯 Keep going! Achievements will unlock as you progress.")