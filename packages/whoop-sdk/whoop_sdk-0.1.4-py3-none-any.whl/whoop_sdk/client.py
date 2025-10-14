"""
Main WHOOP SDK client for making API calls.
"""

import requests
from typing import Dict, Any, Optional
from .auth import AuthManager


class Whoop:
    """
    Main WHOOP SDK client for accessing WHOOP fitness data.
    
    Example usage:
        from whoop_sdk import Whoop
        
        whoop = Whoop()
        whoop.login()  # One-time authentication
        profile = whoop.get_profile()
        recovery = whoop.get_recovery()
    """
    
    BASE_URL = "https://api.prod.whoop.com/developer/v2"
    
    def __init__(self):
        """Initialize the WHOOP client with authentication."""
        self.auth = AuthManager()
    
    def login(self) -> bool:
        """
        Perform OAuth login to authenticate with WHOOP.
        
        Returns:
            bool: True if login was successful
            
        Note:
            This only needs to be called once. Tokens are saved automatically.
        """
        return self.auth.login()
    
    def reset_config(self) -> None:
        """
        Reset/clear all stored configuration and tokens.
        
        Use this if you need to re-authenticate with different credentials.
        """
        self.auth.reset_config()
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an authenticated request to the WHOOP API.
        
        Args:
            endpoint: API endpoint (e.g., '/user/profile/basic')
            params: Query parameters
            
        Returns:
            Dict containing the API response
            
        Raises:
            RuntimeError: If authentication fails
            requests.HTTPError: If API request fails
        """
        # Get access token (auto-refreshes if needed)
        access_token = self.auth.ensure_access_token()
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Make the request
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Get the user's basic profile information.
        
        Returns:
            Dict containing user profile data (user_id, email, first_name, last_name, etc.)
        """
        return self._make_request("/user/profile/basic")
    
    def get_recovery(self, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get recovery data for the user.
        
        Args:
            start: Start date in ISO format (e.g., '2024-01-01T00:00:00.000Z')
            end: End date in ISO format (e.g., '2024-01-31T23:59:59.999Z')
            limit: Number of recovery records to return (max 25, default 10)
            
        Returns:
            Dict containing recovery records
        """
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
            
        return self._make_request("/recovery", params=params)
    
    def get_sleep(self, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get sleep data for the user.
        
        Args:
            start: Start date in ISO format (e.g., '2024-01-01T00:00:00.000Z')
            end: End date in ISO format (e.g., '2024-01-31T23:59:59.999Z')
            limit: Number of sleep records to return (max 25, default 10)
            
        Returns:
            Dict containing sleep records
        """
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
            
        return self._make_request("/activity/sleep", params=params)
    
    def get_workout(self, start: Optional[str] = None, end: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get workout data for the user.
        
        Args:
            start: Start date in ISO format (e.g., '2024-01-01T00:00:00.000Z')
            end: End date in ISO format (e.g., '2024-01-31T23:59:59.999Z')
            limit: Number of workout records to return (max 25, default 10)
            
        Returns:
            Dict containing workout records
        """
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
            
        return self._make_request("/activity/workout", params=params)
    
