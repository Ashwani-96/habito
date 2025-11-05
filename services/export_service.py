# services/export_service.py
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from services.analytics_service import AnalyticsService

class ExportService:
    def __init__(self):
        self.analytics = AnalyticsService()
    
    def export_to_csv(self, habit_logs: List[dict]) -> str:
        """Export habit data to CSV format"""
        df = pd.DataFrame(habit_logs)
        return df.to_csv(index=False)

    def export_to_json(self, habit_logs: List[dict], habit_goals: Dict[str, dict], current_user: str) -> str:
        """Export habit data to JSON format"""
        export_data = {
            'user': current_user,
            'export_date': datetime.now().isoformat(),
            'habits': habit_logs,
            'goals': habit_goals,
            'summary': {
                'total_completions': len([log for log in habit_logs if log.get('type') == 'log']),
                'unique_habits': len(set(log['habit'] for log in habit_logs)),
                'current_streaks': self.analytics.calculate_streaks(habit_logs)
            }
        }
        return json.dumps(export_data, indent=2)

    def generate_progress_report(self, habit_logs: List[dict], habit_goals: Dict[str, dict], current_user: str) -> str:
        """Generate a comprehensive progress report"""
        logged_habits = [log for log in habit_logs if log.get('type') == 'log']
        current_streaks = self.analytics.calculate_streaks(habit_logs)
        longest_streaks = self.analytics.get_longest_streaks(habit_logs)
        weekly_progress = self.analytics.check_weekly_progress(habit_logs, habit_goals)
        
        report = f"""
HABITVOICE PROGRESS REPORT
User: {current_user.title()}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

==================== SUMMARY ====================
Total Completions: {len(logged_habits)}
Unique Habits: {len(set(log['habit'] for log in logged_habits))}
Days Active: {pd.DataFrame(logged_habits)['time'].apply(lambda x: x[:10]).nunique() if logged_habits else 0}
Total Streak Days: {sum(current_streaks.values())}

==================== CURRENT STREAKS ====================
"""
        
        if current_streaks:
            for habit, streak in sorted(current_streaks.items(), key=lambda x: x[1], reverse=True):
                report += f"{habit.title()}: {streak} days\n"
        else:
            report += "No active streaks\n"
        
        report += "\n==================== LONGEST STREAKS ====================\n"
        if longest_streaks:
            for habit, streak in sorted(longest_streaks.items(), key=lambda x: x[1], reverse=True):
                report += f"{habit.title()}: {streak} days\n"
        else:
            report += "No streak records yet\n"
        
        report += "\n==================== WEEKLY PROGRESS ====================\n"
        if weekly_progress:
            for habit, progress in weekly_progress.items():
                report += f"{habit.title()}: {progress['completed']}/{progress['target']} ({progress['percentage']:.0f}%)\n"
        else:
            report += "No weekly goals set\n"
        
        return report