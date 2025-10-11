"""Sample entrypoint for template package."""

from typing import Annotated

from ab_client_token_validator import Client as TokenValidatorClient
from ab_client_token_validator.api.token_validator import validate_token_validate_post
from ab_client_token_validator.models import ValidateTokenRequest

from ab_client_user.api.user import upsert_user_by_oidc_user_oidc_put
from ab_client_user.client import Client as UserClient
from ab_client_user.models import UpsertByOIDCRequest

from ab_core.dependency import Depends, inject
from ab_core.dependency.loaders import ObjectLoaderEnvironment

from .exceptions import IdentificationError
from .models import IdentityContext, User, ValidatedOIDCClaims


@inject
async def identify(
    token: str,
    token_validator_client: Annotated[
        TokenValidatorClient,
        Depends(ObjectLoaderEnvironment[TokenValidatorClient](env_prefix="TOKEN_VALIDATOR_CLIENT"), persist=True),
    ],
    user_client: Annotated[
        UserClient, Depends(ObjectLoaderEnvironment[UserClient](env_prefix="USER_CLIENT"), persist=True)
    ],
) -> IdentityContext:
    """Identity a user given a valid token."""
    # 1. validate the token
    async with token_validator_client as token_validator_client:
        claims = await validate_token_validate_post.asyncio(
            client=token_validator_client,
            body=ValidateTokenRequest(
                token=token,
            ),
        )
        if claims is None:
            raise IdentificationError("Token validation failed.")
        if type(claims).__name__ == "HTTPValidationError":
            raise ValueError(f"Bad token validation request: {claims}")

    # 2. upsert the user
    async with user_client as user_client:
        user = await upsert_user_by_oidc_user_oidc_put.asyncio(
            client=user_client,
            body=UpsertByOIDCRequest(
                oidc_sub=claims.sub,
                oidc_iss=claims.iss,
                email=claims.email,
                display_name=claims.given_name or claims.name or claims.nickname,
                preferred_username=claims.nickname or claims.name or claims.given_name,
            ),
        )
        if user is None:
            raise IdentificationError("User validation failed.")
        if type(user).__name__ == "HTTPValidationError":
            raise ValueError(f"Bad user validation request: {user}")

    return IdentityContext(
        token=token,
        claims=ValidatedOIDCClaims.model_validate(claims.to_dict()),
        user=User.model_validate(user.to_dict()),
    )
