"""Router for token validation."""

from typing import Annotated

from ab_core.dependency import Depends
from ab_core.token_validator.schema.validated_token import ValidatedOIDCClaims
from ab_core.token_validator.token_validators import TokenValidator
from fastapi import APIRouter

from ..schema import ValidateTokenRequest

router = APIRouter(
    prefix="/validate",
    tags=["Token Validator"],
)


@router.post(
    "",
    response_model=ValidatedOIDCClaims,
)
async def validate_token(
    request: ValidateTokenRequest,
    token_validator: Annotated[TokenValidator, Depends(TokenValidator, persist=True)],
):
    """Validate a token."""
    return await token_validator.validate(request.token)
