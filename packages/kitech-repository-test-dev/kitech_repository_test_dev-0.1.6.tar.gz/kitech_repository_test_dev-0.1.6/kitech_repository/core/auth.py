"""Authentication management for KITECH Repository."""

import json
from pathlib import Path
from typing import Optional

from kitech_repository.core.config import Config


class AuthManager:
    """Manage authentication for KITECH Repository."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize authentication manager."""
        self.config = config or Config.load()
        self.token_file = self.config.config_dir / "token.json"

    def login(self, token: str, user_id: str = None, expires_at: str = None) -> bool:
        """Save authentication token with metadata."""
        if not token.startswith("kt_"):
            raise ValueError("Invalid token format. Token should start with 'kt_'")

        self.config.config_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        token_data = {
            "token": token,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,  # From server if available
        }

        self.token_file.write_text(json.dumps(token_data, indent=2))
        return True

    def logout(self) -> bool:
        """Remove authentication token."""
        if self.token_file.exists():
            self.token_file.unlink()
            return True
        return False

    def get_token(self) -> Optional[str]:
        """Get the stored authentication token."""
        if self.token_file.exists():
            data = json.loads(self.token_file.read_text())
            return data.get("token")
        return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and token is not expired."""
        token = self.get_token()
        if not token:
            return False

        # Check if token is expired (if we have expiry info)
        if self.token_file.exists():
            data = json.loads(self.token_file.read_text())
            expires_at = data.get("expires_at")
            if expires_at:
                from datetime import datetime
                expiry = datetime.fromisoformat(expires_at)
                if datetime.now() > expiry:
                    return False
        return True

    @property
    def headers(self) -> dict:
        """Get authentication headers for API requests."""
        token = self.get_token()
        if not token:
            raise ValueError("Not authenticated. Please login first.")

        return {
            "X-App-Key": token,
            "accept": "*/*",
        }