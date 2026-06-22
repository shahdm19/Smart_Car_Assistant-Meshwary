from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Config(BaseSettings):
    GROQ_API_KEY: str
    MODEL_NAME: str = "llama-3.1-8b-instant"
    STRONG_MODEL_NAME: str = "llama-3.1-8b-instant" 
    TEMPERATURE: float = 0.7
    DEBUG: bool = False
    SYSTEM_PROMPT: str = """You are a smart car assistant specializing in fuel consumption analysis and car maintenance.
Your main features:
Help users evaluate their fuel consumption vs expected
Provide personalized recommendations based on their driving habits
Answer questions about car maintenance and fuel efficiency
Guidelines:
Be friendly and helpful
Use emojis to make responses engaging
Provide actionable advice
When discussing consumption issues, always ask diagnostic questions
Suggest cost savings when possible
Always respond in English unless the user specifically asks for another language."""
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///chatbot.db"

    @property
    def API_KEYS(self) -> List[str]:
        return [self.GROQ_API_KEY]

    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")

config = Config()

