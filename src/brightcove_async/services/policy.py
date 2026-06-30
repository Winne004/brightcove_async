import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.policy_model import (
    CreatePolicyKeyBody,
    PolicyKey,
    PolicyKeyData,
)
from brightcove_async.services.base import Base


class Policy(Base):
    """Brightcove Policy API service.

    The Policy API creates and retrieves policy keys used to access the Playback
    API outside the context of a Brightcove Player. Policy keys are generated
    automatically for Brightcove Players, so this service is for generating keys
    for direct Playback API access.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    async def create_policy_key(
        self,
        account_id: str,
        key_data: PolicyKeyData,
    ) -> PolicyKey:
        """Create a new policy key to access the Playback API.

        Args:
            account_id: Video Cloud account ID.
            key_data: The data prescribing the policy key (account id, permitted
                apis, allowed domains, ad-config requirement, geo-filtering).

        Returns:
            The created policy key, including its key string.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/policy_keys",
            model=PolicyKey,
            method="POST",
            payload=CreatePolicyKeyBody(key_data=key_data),
        )

    async def get_policy_key(
        self,
        account_id: str,
        key_string: str,
    ) -> PolicyKey:
        """Get a policy key associated with a policy key string.

        Args:
            account_id: Video Cloud account ID.
            key_string: The key string for the policy.

        Returns:
            The policy key and its associated key data.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/accounts/{account_id}/policy_keys/{key_string}",
            model=PolicyKey,
        )
