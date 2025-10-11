"""Identity Context Models."""

from ab_client_token_validator.models import ValidatedOIDCClaims as AttrsOIDCClaims
from ab_client_user.models import User as AttrsUser
from pydantic import BaseModel, Field

from ab_core.dependency.pydanticize import pydanticize_type

User: type[BaseModel] = pydanticize_type(AttrsUser)
ValidatedOIDCClaims: type[BaseModel] = pydanticize_type(AttrsOIDCClaims)


class IdentityContext(BaseModel):
    """Per-request identity context resolved from the bearer token."""

    token: str = Field(..., description="Raw Bearer token")
    claims: ValidatedOIDCClaims = Field(..., description="Claims from validated token")
    user: User = Field(..., description="The current user")
