# config/settings.py
import os
import streamlit as st

class Settings:
    @staticmethod
    def get_secret(key, default=''):
        try:
            return st.secrets[key]
        except:
            return os.getenv(key, default)
    
    OPENAI_API_KEY = None
    USERS_DATA_DIR = "users_data"
    SAMPLE_RATE = 16000
    RECORDING_DURATION = 7
    MAX_RETRIES = 3
    AUTO_SAVE_INTERVAL = 300
    SESSION_TIMEOUT = 300
    DEBUG = True
    
    @classmethod
    def initialize(cls):
        cls.OPENAI_API_KEY = cls.get_secret('OPENAI_API_KEY', 'your-key-here')
        cls.USERS_DATA_DIR = cls.get_secret('USERS_DATA_DIR', 'users_data')
        cls.SAMPLE_RATE = int(cls.get_secret('SAMPLE_RATE', '16000'))
        cls.RECORDING_DURATION = int(cls.get_secret('RECORDING_DURATION', '7'))
        cls.MAX_RETRIES = int(cls.get_secret('MAX_RETRIES', '3'))
        cls.AUTO_SAVE_INTERVAL = int(cls.get_secret('AUTO_SAVE_INTERVAL', '300'))
        cls.SESSION_TIMEOUT = int(cls.get_secret('SESSION_TIMEOUT', '300'))
        cls.DEBUG = cls.get_secret('DEBUG', 'True').lower() == 'true'
        os.makedirs(cls.USERS_DATA_DIR, exist_ok=True)

settings = Settings()