import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.analytics_model.alltime_videos import (
    AllTimeVideoAnalyticsResponse,
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

    async def get_video_analytics(
        self,
        account_id: str,
        video_id: str,
        params: dict[str, str] | None = None,
    ) -> AllTimeVideoAnalyticsResponse:
        """Fetches video analytics for a specific video.

        :param account_id: Brightcove account ID.
        :param video_id: Video ID for which to fetch analytics.
        :param params: Additional query parameters.
        :return: Dictionary containing video analytics data.
        """
        return await self.fetch_data(
            endpoint=f"{self.base_url}/alltime/accounts/{account_id}/videos/{video_id}",
            model=AllTimeVideoAnalyticsResponse,
        )
