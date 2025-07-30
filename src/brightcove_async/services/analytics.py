import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.analytics_model import (
    GetAlltimeVideoViewsResponse,
    Timeline,
    TimelineWithDuration,
)

from brightcove_async.services.base import Base


class Analytics(Base):
    @property
    def base_url(self) -> str:
        return "https://analytics.api.brightcove.com/v1"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    async def get_account_engagement(self, account_id: str) -> Timeline:
        """Fetches account engagement metrics.

        :param account_id: Brightcove account ID.
        :return: Dictionary containing account engagement data.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/engagement/accounts/{account_id}",
            model=Timeline,
        )

    async def get_player_engagement(self, account_id: str, player_id: str) -> Timeline:
        """Fetches player engagement metrics.

        :param account_id: Brightcove account ID.
        :param player_id: Player ID for which to fetch engagement metrics.
        :return: Dictionary containing player engagement data.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/engagement/accounts/{account_id}/players/{player_id}",
            model=Timeline,
        )

    async def get_video_engagement(
        self, account_id: str, video_id: str
    ) -> TimelineWithDuration:
        """Fetches video engagement metrics.

        :param account_id: Brightcove account ID.
        :param video_id: Video ID for which to fetch engagement metrics.
        :return: Dictionary containing video engagement data.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/engagement/accounts/{account_id}/videos/{video_id}",
            model=TimelineWithDuration,
        )

    async def get_video_analytics(
        self,
        account_id: str,
        video_id: str,
        params: dict[str, str] | None = None,
    ) -> GetAlltimeVideoViewsResponse:
        """Fetches video analytics for a specific video.

        :param account_id: Brightcove account ID.
        :param video_id: Video ID for which to fetch analytics.
        :param params: Additional query parameters.
        :return: Dictionary containing video analytics data.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/alltime/accounts/{account_id}/videos/{video_id}",
            model=GetAlltimeVideoViewsResponse,
        )
