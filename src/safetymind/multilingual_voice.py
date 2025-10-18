"""
SafetyMind Multilingual Voice Module
Handles multilingual voice generation using ElevenLabs.
"""

import json
from typing import Dict, List, Optional, Any
from .config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, ELEVENLABS_API_KEY, VOICE_MODEL_ID
from elevenlabs import Voice, VoiceSettings, set_api_key, generate


class MultilingualVoiceManager:
    """Manages multilingual voice generation using ElevenLabs."""
    
    def __init__(self):
        self.elevenlabs_client = None
        self.current_language = DEFAULT_LANGUAGE
        self._initialize_elevenlabs()
    
    def _initialize_elevenlabs(self):
        """Initialize ElevenLabs client."""
        if ELEVENLABS_API_KEY:
            try:
                set_api_key(ELEVENLABS_API_KEY)
                self.elevenlabs_client = True
                print("✅ ElevenLabs multilingual client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize ElevenLabs: {e}")
                self.elevenlabs_client = None
        else:
            print("⚠️ ElevenLabs API key not found")
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages."""
        return SUPPORTED_LANGUAGES
    
    def set_language(self, language_code: str) -> bool:
        """Set the current language for voice generation."""
        if language_code in SUPPORTED_LANGUAGES:
            self.current_language = language_code
            print(f"✅ Language set to: {SUPPORTED_LANGUAGES[language_code]['name']}")
            return True
        else:
            print(f"❌ Unsupported language: {language_code}")
            return False
    
    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language using Groq."""
        try:
            from .groq_analysis import GroqClient
            groq_client = GroqClient()
            
            language_name = SUPPORTED_LANGUAGES.get(target_language, {}).get('name', target_language)
            
            prompt = f"""
            Translate the following safety incident text to {language_name}.
            Keep the technical terms and safety terminology accurate.
            Maintain the professional tone and structure.
            
            Text to translate: "{text}"
            
            Return only the translated text, no additional explanations.
            """
            
            response = groq_client.chat_completion(prompt)
            return response.strip()
            
        except Exception as e:
            print(f"❌ Translation failed: {e}")
            return text  # Return original text if translation fails
    
    def generate_multilingual_voice(self, text: str, language_code: Optional[str] = None) -> Optional[bytes]:
        """Generate voice in the specified language."""
        if not self.elevenlabs_client:
            print("❌ ElevenLabs client not available")
            return None
        
        try:
            # Use specified language or current language
            lang_code = language_code or self.current_language
            
            if lang_code not in SUPPORTED_LANGUAGES:
                print(f"❌ Unsupported language: {lang_code}")
                return None
            
            language_config = SUPPORTED_LANGUAGES[lang_code]
            voice_id = language_config["voice_id"]
            
            # Translate text if not in English and target language is not English
            if lang_code != "en":
                translated_text = self.translate_text(text, lang_code)
                print(f"🌍 Translated to {language_config['name']}: {translated_text[:50]}...")
            else:
                translated_text = text
            
            # Generate speech using ElevenLabs multilingual model
            audio = generate(
                text=translated_text,
                voice=voice_id,
                model=VOICE_MODEL_ID
            )
            
            # Convert generator to bytes
            audio_bytes = b"".join(audio)
            print(f"✅ Generated {language_config['name']} voice: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Multilingual voice generation failed: {e}")
            return None
    
    def generate_safety_alert(self, alert_text: str, language_code: Optional[str] = None) -> Optional[bytes]:
        """Generate safety alert in multiple languages."""
        if not self.elevenlabs_client:
            return None
        
        try:
            lang_code = language_code or self.current_language
            
            # Add urgency to the alert
            urgent_prefix = {
                "en": "URGENT SAFETY ALERT: ",
                "es": "ALERTA DE SEGURIDAD URGENTE: ",
                "fr": "ALERTE DE SÉCURITÉ URGENTE: ",
                "de": "DRINGENDE SICHERHEITSWARNUNG: ",
                "ar": "تنبيه أمني عاجل: ",
                "pt": "ALERTA DE SEGURANÇA URGENTE: ",
                "zh": "紧急安全警报："
            }
            
            prefix = urgent_prefix.get(lang_code, urgent_prefix["en"])
            full_alert = prefix + alert_text
            
            return self.generate_multilingual_voice(full_alert, lang_code)
            
        except Exception as e:
            print(f"❌ Safety alert generation failed: {e}")
            return None
    
    def generate_training_content(self, content: str, language_code: Optional[str] = None) -> Optional[bytes]:
        """Generate training content in specified language."""
        if not self.elevenlabs_client:
            return None
        
        try:
            lang_code = language_code or self.current_language
            
            # Add training context
            training_prefix = {
                "en": "Safety Training: ",
                "es": "Capacitación de Seguridad: ",
                "fr": "Formation Sécurité: ",
                "de": "Sicherheitsschulung: ",
                "ar": "تدريب السلامة: ",
                "pt": "Treinamento de Segurança: ",
                "zh": "安全培训："
            }
            
            prefix = training_prefix.get(lang_code, training_prefix["en"])
            full_content = prefix + content
            
            return self.generate_multilingual_voice(full_content, lang_code)
            
        except Exception as e:
            print(f"❌ Training content generation failed: {e}")
            return None
    
    def generate_incident_analysis(self, analysis: str, language_code: Optional[str] = None) -> Optional[bytes]:
        """Generate incident analysis in specified language."""
        if not self.elevenlabs_client:
            return None
        
        try:
            lang_code = language_code or self.current_language
            
            # Add analysis context
            analysis_prefix = {
                "en": "Incident Analysis: ",
                "es": "Análisis de Incidente: ",
                "fr": "Analyse d'Incident: ",
                "de": "Vorfallanalyse: ",
                "ar": "تحليل الحادث: ",
                "pt": "Análise de Incidente: ",
                "zh": "事件分析："
            }
            
            prefix = analysis_prefix.get(lang_code, analysis_prefix["en"])
            full_analysis = prefix + analysis
            
            return self.generate_multilingual_voice(full_analysis, lang_code)
            
        except Exception as e:
            print(f"❌ Incident analysis generation failed: {e}")
            return None


# Global multilingual voice manager instance
multilingual_voice_manager = MultilingualVoiceManager()


def get_supported_languages() -> Dict[str, Dict[str, str]]:
    """Get list of supported languages."""
    return multilingual_voice_manager.get_supported_languages()


def set_voice_language(language_code: str) -> bool:
    """Set the current language for voice generation."""
    return multilingual_voice_manager.set_language(language_code)


def get_current_voice_language() -> str:
    """Get the current language code."""
    return multilingual_voice_manager.get_current_language()


def generate_multilingual_voice(text: str, language_code: Optional[str] = None) -> Optional[bytes]:
    """Generate voice in the specified language."""
    return multilingual_voice_manager.generate_multilingual_voice(text, language_code)


def generate_safety_alert(text: str, language_code: Optional[str] = None) -> Optional[bytes]:
    """Generate safety alert in specified language."""
    return multilingual_voice_manager.generate_safety_alert(text, language_code)


def generate_training_content(text: str, language_code: Optional[str] = None) -> Optional[bytes]:
    """Generate training content in specified language."""
    return multilingual_voice_manager.generate_training_content(text, language_code)


def generate_incident_analysis(text: str, language_code: Optional[str] = None) -> Optional[bytes]:
    """Generate incident analysis in specified language."""
    return multilingual_voice_manager.generate_incident_analysis(text, language_code)
