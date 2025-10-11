import requests
import os
from typing import Dict, Optional

class PixelVaultClient:
    """
    Python client for the AKIRU PixelVault API.

    Args:
        api_key (str): Your API key.
        user_id (str): Your user ID.
        api_version (str): API version (default "1").
        verbose (bool): If True, prints debug info (default False).
    """

    BASE_URL = "https://image.api.team-akiru.site/api/v1"

    def __init__(self, api_key: str, user_id: str, api_version: str = "1", verbose: bool = False):
        self.api_key = api_key
        self.user_id = user_id
        self.api_version = api_version
        self.verbose = verbose
        self.headers = {
            "X-API-KEY": self.api_key,
            "X-USER-ID": self.user_id,
            "X-API-VERSION": self.api_version
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            if self.verbose:
                # Hide API key and full URL in debug logs
                safe_headers = self.headers.copy()
                safe_headers["X-API-KEY"] = "****"
                print(f"[DEBUG] {method} /{endpoint} | headers={safe_headers} | kwargs keys={list(kwargs.keys())}")
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def check_storage(self) -> Dict:
        """Retrieve storage usage info."""
        return self._request("GET", "storage")

    def list_images(self, limit: Optional[int] = None) -> Dict:
        """List all images with optional limit."""
        params = {"limit": limit} if limit else None
        return self._request("GET", "images", params=params)

    def upload_image(self, file_path: str) -> Dict:
        """Upload a single image from file path."""
        if not os.path.isfile(file_path):
            return {"error": f"File not found: {file_path}"}
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self._request("POST", "upload", files=files)

    def delete_image(self, image_id: str) -> Dict:
        """Delete a specific image by its ID."""
        return self._request("DELETE", f"images/{image_id}")

    def delete_all_images(self) -> Dict:
        """Delete all images from the account (use with caution)."""
        return self._request("DELETE", "images/all")