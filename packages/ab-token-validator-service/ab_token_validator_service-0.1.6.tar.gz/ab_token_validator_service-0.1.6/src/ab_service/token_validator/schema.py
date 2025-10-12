"""Schema for token request."""

from pydantic import BaseModel, SecretStr


class ValidateTokenRequest(BaseModel):
    """Schema for token request."""

    token: SecretStr
