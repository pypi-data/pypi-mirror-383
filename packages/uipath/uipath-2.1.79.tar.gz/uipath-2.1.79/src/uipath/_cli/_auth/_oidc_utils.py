import base64
import hashlib
import json
import os
from urllib.parse import urlencode

from ._models import AuthConfig
from ._url_utils import build_service_url


def generate_code_verifier_and_challenge():
    """Generate PKCE code verifier and challenge."""
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")

    code_challenge_bytes = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(code_challenge_bytes).decode("utf-8").rstrip("=")
    )

    return code_verifier, code_challenge


def get_state_param() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")


class OidcUtils:
    @classmethod
    def get_auth_config(cls) -> AuthConfig:
        with open(
            os.path.join(os.path.dirname(__file__), "auth_config.json"), "r"
        ) as f:
            auth_config = json.load(f)

        port = auth_config.get("port", 8104)

        redirect_uri = auth_config["redirect_uri"].replace(
            "__PY_REPLACE_PORT__", str(port)
        )

        return AuthConfig(
            client_id=auth_config["client_id"],
            redirect_uri=redirect_uri,
            scope=auth_config["scope"],
            port=port,
        )

    @classmethod
    def get_auth_url(cls, domain: str) -> tuple[str, str, str]:
        """Get the authorization URL for OAuth2 PKCE flow.

        Args:
            domain (str): The UiPath domain to authenticate against (e.g. 'alpha', 'cloud')

        Returns:
            tuple[str, str]: A tuple containing:
                - The authorization URL with query parameters
                - The code verifier for PKCE flow
        """
        code_verifier, code_challenge = generate_code_verifier_and_challenge()
        auth_config = cls.get_auth_config()
        state = get_state_param()
        query_params = {
            "client_id": auth_config["client_id"],
            "redirect_uri": auth_config["redirect_uri"],
            "response_type": "code",
            "scope": auth_config["scope"],
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        query_string = urlencode(query_params)
        url = build_service_url(domain, f"/identity_/connect/authorize?{query_string}")
        return url, code_verifier, state
