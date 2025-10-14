import os
import json
import shutil
import time
import webbrowser
import urllib.parse
from pathlib import Path
import requests

class AuthManager:
    """Handles WHOOP OAuth authentication and token management."""

    AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
    TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
    CONFIG_PATH = Path.home() / ".whoop_sdk" / "config.json"
    SETTINGS_PATH = Path.home() / ".whoop_sdk" / "settings.json"

    def __init__(self):
        self.settings = self._load_settings()

        # Prefer environment variables, then fallback to local settings file
        self.client_id = os.getenv("WHOOP_CLIENT_ID") or self.settings.get("client_id")
        self.client_secret = os.getenv("WHOOP_CLIENT_SECRET") or self.settings.get("client_secret")
        self.redirect_uri = self.settings.get("redirect_uri") or "https://www.google.com"

        # If nothing found, prompt the user interactively (first run)
        if not self.client_id or not self.client_secret:
            print("🔧 WHOOP SDK setup required.")
            print("You can get these credentials from https://developer.whoop.com/")
            print()
            
            while True:
                try:
                    self.client_id = input("Enter your WHOOP Client ID: ").strip()
                    if not self.client_id:
                        print("❌ Client ID cannot be empty. Please try again.")
                        continue
                    
                    self.client_secret = input("Enter your WHOOP Client Secret: ").strip()
                    if not self.client_secret:
                        print("❌ Client Secret cannot be empty. Please try again.")
                        continue
                    
                    self.redirect_uri = input("Redirect URI [https://www.google.com]: ").strip() or "https://www.google.com"
                    
                    # Validate the inputs
                    if len(self.client_id) < 10:
                        print("❌ Client ID seems too short. Please check and try again.")
                        continue
                    
                    if len(self.client_secret) < 10:
                        print("❌ Client Secret seems too short. Please check and try again.")
                        continue
                    
                    break
                    
                except KeyboardInterrupt:
                    print("\n❌ Setup cancelled by user.")
                    raise RuntimeError("Setup cancelled - no credentials provided.")
                except Exception as e:
                    print(f"❌ Error during setup: {e}")
                    print("Please try again.")
                    continue
            
            self._save_settings({
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
            })
            print(f"✅ Credentials saved to {self.SETTINGS_PATH}")

        self.scopes = "offline read:profile read:recovery read:sleep read:workout"
        self.state = "whoop_sdk_state_12345"
        self.tokens = self._load_tokens()

    # ---------- Public Methods ----------

    def reset_config(self):
        """Reset/clear all stored configuration and tokens."""
        
        config_dir = self.CONFIG_PATH.parent
        
        if config_dir.exists():
            shutil.rmtree(config_dir)
            print("✅ Configuration and tokens cleared.")
            print("Next time you initialize AuthManager, you'll be prompted for new credentials.")
        else:
            print("ℹ️  No configuration found to clear.")

    def login(self):
        """Perform one-time OAuth login."""
        # Check if we already have valid tokens
        if self.tokens and self.tokens.get("access_token"):
            print("✅ You're already logged in!")
            print("If you need to re-authenticate, call auth.reset_config() first.")
            return True
        
        print("🌐 Opening WHOOP authorization page in your browser...")
        url = self._build_auth_url()
        webbrowser.open(url)

        print("\nOnce you approve access, you'll be redirected to:")
        print("   → https://www.google.com/?code=XXXX&state=whoop_sdk_state_12345")
        print("\n💡 Tip: Copy the entire URL and paste it here, or just the code part.")
        print("💡 To cancel, type 'cancel' or press Ctrl+C")
        
        while True:
            try:
                code = input("\n🔑 Paste the code from that URL (or 'cancel' to exit): ").strip()
                
                if code.lower() == 'cancel':
                    print("❌ Login cancelled by user.")
                    raise RuntimeError("Login cancelled - no tokens obtained.")
                
                if not code:
                    print("❌ Code cannot be empty. Please try again.")
                    continue
                
                # Extract code from full URL if user pasted the whole thing
                if "code=" in code:
                    code = code.split("code=")[1].split("&")[0]
                
                if len(code) < 10:
                    print("❌ Code seems too short. Please check and try again.")
                    continue
                
                print("🔄 Exchanging code for tokens...")
                tokens = self._exchange_code_for_tokens(code)
                self._save_tokens(tokens)
                print("\n✅ WHOOP SDK is now authorized and ready to use!")
                return True
                
            except KeyboardInterrupt:
                print("\n❌ Login cancelled by user.")
                raise RuntimeError("Login cancelled - no tokens obtained.")
            except Exception as e:
                print(f"❌ Login failed: {e}")
                print("Please check your code and try again.")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry not in ['y', 'yes']:
                    raise RuntimeError(f"Login failed: {e}")
                continue

    def ensure_access_token(self):
        """Return valid access token (auto-refresh if needed)."""
        if not self.tokens:
            raise RuntimeError("No tokens found. Run auth.login() first.")
        
        # Check if access token exists
        access_token = self.tokens.get("access_token")
        if not access_token:
            return self.refresh_access_token()
        
        # Check if token is expired (with 60 second safety buffer)
        expires_at = self.tokens.get("expires_at")
        if expires_at and time.time() >= (expires_at - 60):
            return self.refresh_access_token()
        
        return access_token

    def refresh_access_token(self):
        """Use the stored refresh token to get a new access token."""
        print("🔄 Refreshing access token...")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.tokens["refresh_token"],
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        resp = requests.post(self.TOKEN_URL, data=data)
        resp.raise_for_status()
        new_tokens = resp.json()
        self.tokens.update(new_tokens)
        self._save_tokens(self.tokens)
        print("✅ Access token refreshed.")
        return self.tokens["access_token"]

    # ---------- Internal Helpers ----------

    def _build_auth_url(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": self.state,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def _exchange_code_for_tokens(self, code: str):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        resp = requests.post(self.TOKEN_URL, data=data)
        resp.raise_for_status()
        return resp.json()

    def _save_tokens(self, tokens):
        # Calculate expiration timestamp if expires_in is provided
        if "expires_in" in tokens:
            tokens["expires_at"] = time.time() + tokens["expires_in"]
        
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_PATH, "w") as f:
            json.dump(tokens, f, indent=2)
        self.tokens = tokens

    def _load_tokens(self):
        if self.CONFIG_PATH.exists():
            with open(self.CONFIG_PATH) as f:
                return json.load(f)
        return {}

    def _load_settings(self):
        if self.SETTINGS_PATH.exists():
            with open(self.SETTINGS_PATH) as f:
                return json.load(f)
        return {}

    def _save_settings(self, data):
        self.SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=2)
