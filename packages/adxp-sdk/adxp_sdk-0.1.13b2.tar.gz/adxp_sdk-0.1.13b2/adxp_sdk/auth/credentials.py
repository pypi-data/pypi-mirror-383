from typing import Optional
from datetime import datetime, timedelta
import requests
from requests.exceptions import RequestException
from pydantic import BaseModel, PrivateAttr, model_validator, SecretStr
from typing_extensions import Self
from abc import ABC, abstractmethod
import warnings


class BaseCredentials(BaseModel, ABC):
    """
    Abstract base class for authentication credentials.

    This class provides a common interface for different types of credentials
    that can be used with the A.X Platform API.
    """

    @abstractmethod
    def get_headers(self) -> dict:
        """
        Returns the headers required for API requests.

        Returns:
            dict: Headers containing the authentication information
        """
        pass


class ApiKeyCredentials(BaseCredentials):
    """
    Authentication credentials for the A.X Platform API using API key.

    Attributes:
        api_key (str): API key

    Example:
        ```python
        credentials = ApiKeyCredentials(api_key="your_api_key")
        headers = credentials.get_headers()
        ```
    """

    api_key: str
    base_url: str

    def get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}


class TokenCredentials(BaseCredentials):
    """
    Authentication credentials for the A.X Platform API.

    Attributes:
        username (str): User name
        password (str): User password
        project (str): Project name. it is used as client_id in keycloak
        base_url (str): Base URL of the API

    Example:
        ```python
        credentials = TokenCredentials(
            username="user",
            password="password",
            project="project_name",
            base_url="https://aip.sktai.io"
        )
        token = credentials.authenticate()
        headers = credentials.get_headers()
        ```
    """

    username: str
    password: SecretStr
    project: str
    base_url: str

    _token: Optional[str] = PrivateAttr(default=None)
    _auth_time: Optional[datetime] = PrivateAttr(default=None)
    _token_expiry_minutes: int = PrivateAttr(default=20)
    _grant_type: str = PrivateAttr(default="password")

    @model_validator(mode="after")
    def auto_authenticate(self) -> Self:
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
        self.authenticate()
        return self

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def is_token_expired(self) -> bool:
        if not self._auth_time:
            return True
        expiry_time = self._auth_time + timedelta(minutes=self._token_expiry_minutes)
        return datetime.now() > expiry_time

    def _perform_auth(self) -> str:
        login_url = f"{self.base_url}/api/v1/auth/login"
        login_data = {
            "grant_type": self._grant_type,
            "username": self.username,
            "password": self.password.get_secret_value(),
            "client_id": self.project,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        try:
            res = requests.post(login_url, data=login_data, headers=headers)
            if res.status_code == 201:
                self._token = res.json().get("access_token")
                self._auth_time = datetime.now()
                if self._token is None:
                    raise RuntimeError("Authentication failed: No token received")
                return self._token
            raise RuntimeError(f"Authentication failed: {res.status_code}, {res.text}")
        except RequestException as e:
            raise RuntimeError(
                f"Error occurred during authentication request: {str(e)}"
            )

    def authenticate(self) -> str:
        """
        Authenticates with the API server and retrieves a token.
        If the token is expired, it automatically attempts to refresh.

        Returns:
            str: Authentication token

        Raises:
            RuntimeError: If authentication fails
        """
        if self._token and not self.is_token_expired:
            return self._token

        else:
            return self._perform_auth()

    def get_headers(self) -> dict:
        """
        Returns the headers required for API requests.

        Returns:
            dict: Headers containing the authentication token
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self._token is None or self.is_token_expired:
            self.authenticate()

        headers["Authorization"] = f"Bearer {self._token}"

        return headers

    @staticmethod
    def exchange_token(base_url: str, token: str, project_name: str) -> dict:
        """
        Exchange an existing token for another client.

        Args:
            base_url (str): API base URL
            token (str): Existing access token
            to_exchange_client_name (str): Target client name

        Returns:
            dict: Full JSON response
        """
        url = f"{base_url}/api/v1/auth/token/exchange"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        params = {"to_exchange_client_name": project_name}

        try:
            res = requests.get(url, params=params, headers=headers)
            res.raise_for_status()
            return res.json()
        except RequestException as e:
            raise RuntimeError(f"Error during token exchange request: {str(e)}")


class Credentials(TokenCredentials):
    """
    Deprecated: Use TokenCredentials instead.

    This class is kept for backward compatibility but will be removed in a future version.
    Please use TokenCredentials instead.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Credentials is deprecated and will be removed in a future version. "
            "Please use TokenCredentials instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
