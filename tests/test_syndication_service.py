"""Tests for the Syndication service."""

from unittest.mock import AsyncMock, patch

import pytest

from brightcove_async.schemas.syndication_model import (
    Syndication as SyndicationModel,
)
from brightcove_async.schemas.syndication_model import (
    SyndicationList,
    Type,
)
from brightcove_async.services.syndication import Syndication

BASE_URL = "https://edge.social.api.brightcove.com/v1/accounts/"


@pytest.fixture
def syndication_service(mock_session, dummy_oauth):
    return Syndication(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=10,
    )


class TestSyndicationInitialization:
    def test_stores_limit_and_url(self, syndication_service):
        assert syndication_service._limit == 10
        assert syndication_service.base_url == BASE_URL


class TestSyndicationEndpoints:
    async def test_get_all_syndications(self, syndication_service):
        with patch.object(
            syndication_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = SyndicationList(root=[])
            await syndication_service.get_all_syndications("acc123")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/mrss/syndications",
                model=SyndicationList,
            )

    async def test_get_syndication(self, syndication_service):
        with patch.object(
            syndication_service, "fetch_data", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = SyndicationModel(name="Test", type=Type.google)
            await syndication_service.get_syndication("acc123", "syn456")

            mock_fetch.assert_called_once_with(
                endpoint=f"{BASE_URL}acc123/mrss/syndications/syn456",
                model=SyndicationModel,
            )
