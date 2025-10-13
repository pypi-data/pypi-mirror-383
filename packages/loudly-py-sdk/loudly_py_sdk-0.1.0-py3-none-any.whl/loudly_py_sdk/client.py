import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from .exceptions import LoudlyAPIError

# Load .env variables automatically
load_dotenv()


class LoudlyClient:
    DEFAULT_BASE_URL = "https://api.loudly.com/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        timeout: float = 10.0,
        base_url: Optional[str] = None,
    ):
        if config:
            api_key = config.get("apiKey", api_key)

        self.api_key = api_key or os.getenv("LOUDLY_API_KEY")
        self.timeout = timeout
        self.base_url = base_url or self.DEFAULT_BASE_URL

        self.session = requests.Session()
        if self.api_key:
            self._set_auth_header(self.api_key)

    # -------------------
    # Fluent setters
    # -------------------
    def with_api_key(self, api_key: str) -> "LoudlyClient":
        self._set_auth_header(api_key)
        return self

    def with_timeout(self, timeout: float) -> "LoudlyClient":
        self.timeout = timeout
        return self

    def with_base_url(self, base_url: str) -> "LoudlyClient":
        self.base_url = base_url
        return self

    # -------------------
    # Internal helpers
    # -------------------
    def _set_auth_header(self, api_key: str):
        self.api_key = api_key
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _ensure_api_key(self):
        if not self.api_key:
            raise ValueError(
                "No API key set. Use api_key=..., config={'apiKey': ...}, "
                "LOUDLY_API_KEY in a .env file, or .with_api_key()."
            )

    def _request(self, method: str, path: str, params=None, json=None, headers=None):
        self._ensure_api_key()
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers,
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # -------------------
    # API Methods
    # -------------------

    # 1. Genres
    def list_genres(self) -> List[Dict[str, Any]]:
        self._ensure_api_key()
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
        }
        url = "https://soundtracks.loudly.com/api/ai/genres"
        
        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # 2. Structures
    def list_structures(self) -> List[Dict[str, Any]]:
        self._ensure_api_key()
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
        }
        url = "https://soundtracks.loudly.com/api/ai/structures"
        
        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # 3. Random prompt
    def get_random_prompt(self) -> Dict[str, Any]:
        self._ensure_api_key()
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
        }
        url = "https://soundtracks.loudly.com/api/ai/prompt/random"
        
        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # 4. Song tags
    def get_song_tags(
        self,
        mood: Optional[List[str]] = None,
        genre: Optional[List[str]] = None,
        key: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        self._ensure_api_key()
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
        }
        url = "https://soundtracks.loudly.com/api/songs/tags"
        payload = {}
        if mood: payload["mood"] = mood
        if genre: payload["genre"] = genre
        if key: payload["key"] = key
        
        try:
            resp = requests.get(url, headers=headers, json=payload, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # 5. List songs
    def list_songs(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        self._ensure_api_key()
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
        }
        params = {"page": page, "per_page": per_page}
        url = "https://soundtracks.loudly.com/api/songs"
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # 6. Song Generation
    def generate_ai_song(
        self,
        genre: str,
        genre_blend: str = "",
        duration: Optional[int] = None,
        energy: Optional[str] = "",
        bpm: Optional[int] = None,
        key_root: Optional[str] = "",
        key_quality: Optional[str] = "",
        instruments: Optional[str] = "",
        structure_id: Optional[int] = None,
        test: Optional[bool] = False
    ) -> Dict[str, Any]:
        """Generate AI song using form data"""
        
        if not genre:
            raise ValueError("genre is required")
        
        self._ensure_api_key()
        
        url = "https://soundtracks.loudly.com/api/ai/songs"
        
        # Prepare form data - only include non-empty values
        data = {"genre": genre}
        
        if genre_blend:
            data["genre_blend"] = genre_blend
        if duration is not None:
            data["duration"] = str(duration)
        if energy:
            data["energy"] = energy
        if bpm is not None:
            data["bpm"] = str(bpm)
        if key_root:
            data["key_root"] = key_root
        if key_quality:
            data["key_quality"] = key_quality
        if instruments:
            data["instruments"] = instruments
        if structure_id is not None:
            data["structure_id"] = str(structure_id)
        if test is not None:
            data["test"] = str(test).lower()
        
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
            # Don't set Content-Type - requests will set it automatically for form data
        }
        
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # 7. Song generation from prompt
    def generate_song_from_prompt(
        self,
        prompt: str,
        duration: Optional[int] = None,
        test: Optional[bool] = False,
        structure_id: Optional[int] = None
    ) -> Dict[str, Any]:
        
        if not prompt:
            raise ValueError("Prompt is required")
        
        self._ensure_api_key()
        
        url = "https://soundtracks.loudly.com/api/ai/prompt/songs"
        
        data = {"prompt": prompt}
        
        if duration is not None:
            data["duration"] = str(duration)  
        
        if test is not None:
            data["test"] = str(test).lower() 
        
        if structure_id is not None:
            data["structure_id"] = str(structure_id)
        
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
        }
        
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")
        
        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)
        
        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    # 8. Limits Account
    def get_limits(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        self._ensure_api_key()
        headers = {
            "API-KEY": self.api_key,
            "Accept": "application/json"
        }
        # Use the soundtracks.loudly.com domain for limits as well
        url = "https://soundtracks.loudly.com/api/account/limits"
        
        params: Dict[str, Any] = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise LoudlyAPIError(-1, f"Network error: {e}")

        if not resp.ok:
            try:
                err = resp.json()
                message = err.get("error", err.get("message", resp.text))
            except ValueError:
                message = resp.text
            raise LoudlyAPIError(resp.status_code, message, response=resp)

        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}