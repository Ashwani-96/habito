# 🎙️ HabitVoice - AI-Powered Habit Tracker

Voice-based habit tracking application with AI-powered natural language processing.

## 🚀 Features

- 🎤 Voice command habit logging (local deployment)
- 📝 Text-based command input (cloud deployment)
- 📊 Comprehensive analytics dashboard
- 🔥 Streak tracking
- 🎯 Weekly goal setting
- 📈 Progress visualization
- 💾 Data export (CSV, JSON, Reports)

## 🌐 Live Demo

[Try it here](https://habito.streamlit.app) *(Update after deployment)*

## 🛠️ Technologies

- **Frontend:** Streamlit
- **AI/NLP:** OpenAI GPT-3.5 Turbo
- **Data Viz:** Plotly
- **Data Processing:** Pandas

## 📦 Installation (Local)

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/habitvoice.git
cd habitvoice

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo OPENAI_API_KEY=your-key-here > .env

# Run application
streamlit run app.py