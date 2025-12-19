"""Configuration module - loads environment variables."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    """Application branding configuration."""
    title: str


@dataclass
class SplitwiseConfig:
    """Splitwise API configuration."""
    api_key: str
    group_id: str


@dataclass
class GoogleDriveConfig:
    """Google Drive OAuth configuration."""
    client_id: str | None
    client_secret: str | None
    refresh_token: str | None
    folder_id: str | None
    
    @property
    def is_configured(self) -> bool:
        """Check if all required fields are set."""
        return all([self.client_id, self.client_secret, self.refresh_token, self.folder_id])


@dataclass
class EmailConfig:
    """Gmail SMTP configuration."""
    gmail_address: str | None
    gmail_app_password: str | None
    recipient_email: str | None
    
    @property
    def is_configured(self) -> bool:
        """Check if all required fields are set."""
        return all([self.gmail_address, self.gmail_app_password, self.recipient_email])


# Load configurations from environment
app = AppConfig(
    title=os.getenv("DASHBOARD_TITLE", "Family Expenses"),
)

splitwise = SplitwiseConfig(
    api_key=os.getenv("api_key", ""),
    group_id=os.getenv("group_id", ""),
)

gdrive = GoogleDriveConfig(
    client_id=os.getenv("GDRIVE_CLIENT_ID"),
    client_secret=os.getenv("GDRIVE_CLIENT_SECRET"),
    refresh_token=os.getenv("GDRIVE_REFRESH_TOKEN"),
    folder_id=os.getenv("GDRIVE_FOLDER_ID"),
)

email = EmailConfig(
    gmail_address=os.getenv("GMAIL_ADDRESS"),
    gmail_app_password=os.getenv("GMAIL_APP_PASSWORD"),
    recipient_email=os.getenv("RECIPIENT_EMAIL"),
)


def set_recipient_email(value: str) -> None:
    """Override recipient_email at runtime."""
    global email
    email = EmailConfig(
        gmail_address=email.gmail_address,
        gmail_app_password=email.gmail_app_password,
        recipient_email=value,
    )

