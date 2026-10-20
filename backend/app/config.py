import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
    class Settings(BaseSettings):
        OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
        EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        DB_PATH: str = os.getenv("DB_PATH", "app.db")
        CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_data")
        PACKET_TRACER_BRIDGE_URL: str = os.getenv("PACKET_TRACER_BRIDGE_URL", "http://localhost:39000")

        class Config:
            env_file = ".env"
            extra = "allow"
except ImportError:
    class Settings:
        OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
        EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        DB_PATH: str = os.getenv("DB_PATH", "app.db")
        CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./chroma_data")
        PACKET_TRACER_BRIDGE_URL: str = os.getenv("PACKET_TRACER_BRIDGE_URL", "http://localhost:39000")

settings = Settings()
