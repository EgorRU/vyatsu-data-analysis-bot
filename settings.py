"""
Конфигурация приложения на pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс для хранения и валидации настроек приложения.
    """
    
    # Настройки бота
    BOT_TOKEN: str
    PROVIDER_TOKEN: str
    
    # Платёжный провайдер Telegram
    PRICE_RUB: float
    
    # Ссылка на поддержку
    SUPPORT_LINK: str

    # Список админов (через запятую): 123,456
    ADMIN_IDS: str = ""

    class Config(SettingsConfigDict):
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Экземпляр настроек для импорта в других модулях
settings = Settings()