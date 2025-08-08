from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс для хранения и валидации настроек приложения."""
    
    # Настройки бота
    BOT_TOKEN: str
    BOT_URL: str
    
    # Настройки платежной системы
    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str
    PRICE_RUB: float
    
    # Ссылка на поддержку
    SUPPORT_LINK: str

    class Config(SettingsConfigDict):
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Экземпляр настроек для импорта в других модулях
settings = Settings()