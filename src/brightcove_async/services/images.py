from urllib.parse import quote

import aiohttp

from brightcove_async.protocols import OAuthClientProtocol
from brightcove_async.schemas.params import ImageTransformParams
from brightcove_async.services.base import Base


class Images(Base):
    """Brightcove Image API service.

    The Image API resizes, crops, and/or rotates an image served from a
    Brightcove CDN. It is authenticated by an account-specific image token
    embedded in the request path (obtained from Brightcove Support) rather
    than via OAuth, and it returns the raw image bytes.

    Supported image formats: png, jpg, gif.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        oauth: OAuthClientProtocol,
        base_url: str,
        limit: int = 10,
    ) -> None:
        super().__init__(session=session, oauth=oauth, base_url=base_url, limit=limit)

    async def transform_image(
        self,
        account_id: str,
        image_token: str,
        image_url: str,
        params: ImageTransformParams | None = None,
    ) -> bytes:
        """Return a transformed image as raw bytes.

        Args:
            account_id: Brightcove account ID.
            image_token: Account image token allowing transformations
                (obtained from Brightcove Support).
            image_url: The source image URL. It is percent-encoded for you,
                so pass the plain URL.
            params: Optional transformation parameters (resize, crop, rotate,
                fallback, fill area, watermark, nocache).

        Returns:
            The transformed image file contents as bytes.
        """
        encoded_url = quote(image_url, safe="")
        endpoint = (
            f"{self.base_url}/image/v1/{account_id}/{image_token}/url/{encoded_url}"
        )
        # Keep the token out of any raised error / log message.
        error_endpoint = (
            f"{self.base_url}/image/v1/{account_id}/[REDACTED]/url/{encoded_url}"
        )
        query = params.serialize_params() if params else None
        return await self._get_bytes(
            endpoint, params=query, error_endpoint=error_endpoint
        )
