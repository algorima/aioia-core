from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Storage
    STORAGE_ROOT: str = "/workspace/storage"
    SAVE_INPUTS: bool = False  # if True, save raw user inputs for debugging (be careful!)

    # LLM
    LLM_MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"
    LLM_MAX_NEW_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.2
    LLM_USE_4BIT: bool = False
    LLM_TRUST_REMOTE_CODE: bool = True

    # Custom ML model (PyTorch)
    CUSTOM_MODEL_DIR: str = "./ai_ml/fraud_detection/app/models/custom_model_ckpt"
    CUSTOM_MODEL_THRESHOLD_HIGH: float = 0.85
    CUSTOM_MODEL_THRESHOLD_LOW: float = 0.20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
