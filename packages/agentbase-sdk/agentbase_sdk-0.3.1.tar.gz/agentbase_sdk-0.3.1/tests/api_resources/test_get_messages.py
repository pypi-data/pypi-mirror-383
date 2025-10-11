# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agentbase import Agentbase, AsyncAgentbase
from tests.utils import assert_matches_type
from agentbase.types import GetMessageRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGetMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Agentbase) -> None:
        get_message = client.get_messages.retrieve(
            session="session",
        )
        assert_matches_type(GetMessageRetrieveResponse, get_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Agentbase) -> None:
        response = client.get_messages.with_raw_response.retrieve(
            session="session",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        get_message = response.parse()
        assert_matches_type(GetMessageRetrieveResponse, get_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Agentbase) -> None:
        with client.get_messages.with_streaming_response.retrieve(
            session="session",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            get_message = response.parse()
            assert_matches_type(GetMessageRetrieveResponse, get_message, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGetMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAgentbase) -> None:
        get_message = await async_client.get_messages.retrieve(
            session="session",
        )
        assert_matches_type(GetMessageRetrieveResponse, get_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAgentbase) -> None:
        response = await async_client.get_messages.with_raw_response.retrieve(
            session="session",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        get_message = await response.parse()
        assert_matches_type(GetMessageRetrieveResponse, get_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAgentbase) -> None:
        async with async_client.get_messages.with_streaming_response.retrieve(
            session="session",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            get_message = await response.parse()
            assert_matches_type(GetMessageRetrieveResponse, get_message, path=["response"])

        assert cast(Any, response.is_closed) is True
