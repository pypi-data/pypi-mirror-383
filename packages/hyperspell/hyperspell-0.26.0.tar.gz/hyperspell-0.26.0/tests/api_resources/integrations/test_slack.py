# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hyperspell import Hyperspell, AsyncHyperspell
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSlack:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Hyperspell) -> None:
        slack = client.integrations.slack.list()
        assert_matches_type(object, slack, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Hyperspell) -> None:
        slack = client.integrations.slack.list(
            channels=["string"],
            exclude_archived=True,
            include_dms=True,
            include_group_dms=True,
            include_private=True,
        )
        assert_matches_type(object, slack, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Hyperspell) -> None:
        response = client.integrations.slack.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        slack = response.parse()
        assert_matches_type(object, slack, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Hyperspell) -> None:
        with client.integrations.slack.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            slack = response.parse()
            assert_matches_type(object, slack, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSlack:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncHyperspell) -> None:
        slack = await async_client.integrations.slack.list()
        assert_matches_type(object, slack, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncHyperspell) -> None:
        slack = await async_client.integrations.slack.list(
            channels=["string"],
            exclude_archived=True,
            include_dms=True,
            include_group_dms=True,
            include_private=True,
        )
        assert_matches_type(object, slack, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHyperspell) -> None:
        response = await async_client.integrations.slack.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        slack = await response.parse()
        assert_matches_type(object, slack, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHyperspell) -> None:
        async with async_client.integrations.slack.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            slack = await response.parse()
            assert_matches_type(object, slack, path=["response"])

        assert cast(Any, response.is_closed) is True
