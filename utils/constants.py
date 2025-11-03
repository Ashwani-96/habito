# utils/constants.py

HABIT_CATEGORIES = {
    "🏃 Health & Fitness": ["workout", "yoga", "running", "gym", "walking", "stretching", "sports"],
    "🧠 Mental & Learning": ["reading", "meditating", "journaling", "learning", "studying", "gratitude"],
    "💻 Productivity": ["coding", "writing", "planning", "organizing", "learning english"],
    "🌱 Lifestyle": ["sleep early", "no phone", "drinking water", "healthy eating", "cleaning", "cooking"],
    "🎨 Creative": ["drawing", "music", "photography", "crafting", "dancing"],
    "👥 Social": ["calling family", "meeting friends", "networking", "volunteering"]
}

# Flatten categories for easy lookup
COMMON_HABITS = []
for category_habits in HABIT_CATEGORIES.values():
    COMMON_HABITS.extend(category_habits)

# Default goals for habits (per week)
DEFAULT_GOALS = {
    "workout": 5, "running": 4, "yoga": 6, "gym": 4,
    "reading": 7, "meditating": 7, "journaling": 7,
    "coding": 5, "learning": 5, "studying": 5,
    "drinking water": 7, "sleep early": 7, "healthy eating": 7
}

# Voice command patterns
GOAL_PATTERNS = [
    r"set goal (?:for )?(\w+) (\d+) times? (?:per|a|each) week",
    r"i want to do (\w+) (\d+) times? (?:per|a|each) week",
    r"goal for (\w+) is (\d+) (?:per|a|each) week",
    r"(\w+) goal (\d+) times? weekly",
    r"target (\w+) (\d+) times? (?:per|a) week"
]

STREAK_KEYWORDS = ["streak", "how many days", "consecutive", "in a row", "daily streak"]
PROGRESS_KEYWORDS = ["how am i doing", "weekly progress", "this week", "my progress", "progress report"]
DASHBOARD_KEYWORDS = ["progress", "dashboard", "stats", "analytics", "how am i doing", "show my", "report"]