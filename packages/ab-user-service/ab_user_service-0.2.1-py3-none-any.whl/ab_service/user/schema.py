"""Schema definitions for user-related operations."""

from pydantic import BaseModel, EmailStr, Field


class UpsertByOIDCRequest(BaseModel):
    """Request model for creating or updating a user based on OIDC information."""

    oidc_sub: str = Field(
        ...,
        title="OIDC Subject",
        description="The subject (unique user identifier) provided by the OIDC provider.",
    )
    oidc_iss: str = Field(
        ...,
        title="OIDC Issuer",
        description="The issuer URL or identifier of the OIDC provider.",
    )
    email: EmailStr | None = Field(
        None,
        title="Email Address",
        description="User’s email address from the identity provider, if available.",
    )
    display_name: str | None = Field(
        None,
        title="Display Name",
        description="Human-readable name shown in the UI.",
    )
    preferred_username: str | None = Field(
        None,
        title="Preferred Username",
        description="Username the user prefers to be known by (may differ from email).",
    )
