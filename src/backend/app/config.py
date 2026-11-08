from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./aroha.db"
    secret_key: str = "dev-only-secret-change-me-before-deploying-0123456789"
    token_encryption_key: str = ""
    access_token_minutes: int = 60
    cookie_name: str = "aroha_session"
    cookie_secure: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]
    news_feeds: list[str] = [
        "https://techcrunch.com/category/social/feed/",
        "https://www.socialmediatoday.com/feeds/news/",
    ]
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_redirect_uri: str = "http://localhost:8000/instagram/callback"


settings = Settings()
