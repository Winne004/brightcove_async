from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class PolicyGeo(BaseModel):
    """Geo-filtering properties for a policy key."""

    model_config = ConfigDict(populate_by_name=True)

    countries: list[str] | None = Field(
        default=None,
        description="Array of ISO 3166 2- or 4-letter country codes in lower-case.",
    )
    exclude_countries: bool | None = Field(
        default=None,
        description="If true, the countries array is treated as a list of countries "
        "excluded from viewing. If false, it is a list of countries included for "
        "viewing.",
    )


class PolicyKeyData(BaseModel):
    """The data prescribing a policy key.

    Used both as the request body payload when creating a policy key and as the
    ``key-data`` map returned for created/retrieved keys. Only ``account_id`` is
    required when creating a key; the remaining fields are optional.
    """

    model_config = ConfigDict(populate_by_name=True)

    account_id: str = Field(
        validation_alias="account-id",
        serialization_alias="account-id",
        description="The Video Cloud account id.",
    )
    apis: list[str] | None = Field(
        default=None,
        description='Array of APIs permitted for this key (currently "search" is the '
        "only available value - it must be included to use the search functionality "
        "for the Playback API).",
    )
    allowed_domains: list[str] | None = Field(
        default=None,
        validation_alias="allowed-domains",
        serialization_alias="allowed-domains",
        description="For domain restriction, the domains this key will work on.",
    )
    require_ad_config: bool | None = Field(
        default=None,
        validation_alias="require-ad-config",
        serialization_alias="require-ad-config",
        description="Whether Playback API requests require an ad-config-id URL "
        "parameter for server-side ad insertion.",
    )
    geo: PolicyGeo | None = Field(
        default=None,
        description="Map of geo-filtering properties.",
    )


class CreatePolicyKeyBody(BaseModel):
    """Request body for creating a policy key."""

    model_config = ConfigDict(populate_by_name=True)

    key_data: PolicyKeyData = Field(
        validation_alias="key-data",
        serialization_alias="key-data",
        description="Data for the policy key.",
    )


class PolicyKey(BaseModel):
    """A policy key and its associated key data.

    Returned both when creating a policy key and when retrieving one. The
    ``key_string`` field accepts either ``key-string`` or ``key_string`` from the
    API response.
    """

    model_config = ConfigDict(populate_by_name=True)

    key_string: str = Field(
        validation_alias=AliasChoices("key-string", "key_string"),
        serialization_alias="key-string",
        description="The policy key string.",
    )
    key_data: PolicyKeyData = Field(
        validation_alias="key-data",
        serialization_alias="key-data",
        description="Map of key data prescribing the policy.",
    )
