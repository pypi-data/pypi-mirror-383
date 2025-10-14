"""Authentication management for KITECH Repository."""

import json
import stat
from datetime import datetime

from kitech_repository.core.config import Config


class AuthManager:
    """Manage authentication for KITECH Repository."""

    def __init__(self, config: Config | None = None):
        """Initialize authentication manager."""
        self.config = config or Config.load()
        self.app_key_file = self.config.config_dir / "app_key.json"

    def login(self, app_key: str, user_id: str = None, expires_at: str = None) -> bool:
        """Save authentication app key with metadata."""
        if not app_key.startswith("kt_"):
            raise ValueError("Invalid app key format. App key should start with 'kt_'")

        self.config.config_dir.mkdir(parents=True, exist_ok=True)

        app_key_data = {
            "app_key": app_key,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
        }

        self.app_key_file.write_text(json.dumps(app_key_data, indent=2))
        self.app_key_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600
        return True

    def logout(self) -> bool:
        """Remove authentication app key."""
        if self.app_key_file.exists():
            self.app_key_file.unlink()
            return True
        return False

    def get_app_key(self) -> str | None:
        """Get the stored authentication app key."""
        if self.app_key_file.exists():
            data = json.loads(self.app_key_file.read_text())
            return data.get("app_key")
        return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and app key is not expired."""
        if not self.app_key_file.exists():
            return False

        data = json.loads(self.app_key_file.read_text())
        app_key = data.get("app_key")
        if not app_key:
            return False

        # Check expiry if available
        expires_at = data.get("expires_at")
        if expires_at:
            expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now() > expiry:
                return False

        return True

    @property
    def headers(self) -> dict:
        """Get authentication headers for API requests."""
        app_key = self.get_app_key()
        if not app_key:
            raise ValueError("Not authenticated. Please login first.")

        return {
            "X-App-Key": app_key,
            "accept": "*/*",
        }
