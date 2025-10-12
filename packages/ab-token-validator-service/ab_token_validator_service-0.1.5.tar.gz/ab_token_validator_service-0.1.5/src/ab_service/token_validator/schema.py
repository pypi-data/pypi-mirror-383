"""Schema for token request."""

from pydantic import BaseModel


class ValidateTokenRequest(BaseModel):
    """Schema for token request."""

    token: str
