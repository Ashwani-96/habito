# services/voice_service.py
import streamlit as st
import speech_recognition as sr
import time
from config.settings import settings

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def record_speech(self, duration: int = None) -> str:
        """Record speech with error handling and retries"""
        if duration is None:
            duration = settings.RECORDING_DURATION
            
        return self._robust_voice_recording(duration, settings.MAX_RETRIES)
    
    def _robust_voice_recording(self, duration: int, max_retries: int) -> str:
        """Robust voice recording with error handling and retries"""
        
        for attempt in range(max_retries):
            try:
                # Check microphone availability
                with sr.Microphone() as source:
                    st.info(f"🎤 Recording for {duration} seconds... (Attempt {attempt + 1})")
                    
                    # Adjust for ambient noise
                    with st.spinner("🔧 Calibrating microphone..."):
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    # Record audio with progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    audio = self.recognizer.record(source, duration=duration)
                    
                    for i in range(duration):
                        progress_bar.progress((i + 1) / duration)
                        status_text.text(f"Recording... {duration - i - 1} seconds remaining")
                        time.sleep(1)
                    
                    progress_bar.progress(1.0)
                    status_text.text("✅ Recording complete!")
                
                # Convert speech to text
                with st.spinner("🧠 Converting speech to text..."):
                    text = self.recognizer.recognize_google(audio, language="en-US")
                    st.success("✅ Speech recognized successfully!")
                    st.write(f"**🎯 You said:** '{text}'")
                    return text
                    
            except sr.UnknownValueError:
                st.warning(f"⚠️ Could not understand audio clearly (Attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    st.info("💡 Please speak more clearly and try again...")
                    time.sleep(1)
                else:
                    return self._fallback_text_input()
                    
            except sr.RequestError as e:
                st.warning(f"⚠️ Speech service error (Attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    st.info("🔄 Retrying connection...")
                    time.sleep(2)
                else:
                    st.error("❌ Unable to connect to speech recognition service.")
                    return ""
                    
            except OSError as e:
                st.error(f"❌ Microphone access error: {e}")
                st.info("💡 **Troubleshooting:**\n- Check microphone permissions\n- Ensure microphone is connected\n- Try refreshing the page")
                return ""
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    return ""
        
        return ""
    
    def _fallback_text_input(self) -> str:
        """Fallback to text input when voice fails"""
        st.error("❌ Unable to understand speech after multiple attempts.")
        fallback_text = st.text_input(
            "💬 Type your command instead:", 
            placeholder="e.g., 'I did reading for 1 hour'",
            key=f"fallback_input_{time.time()}"
        )
        if fallback_text and st.button("Submit Text Command"):
            return fallback_text
        return ""