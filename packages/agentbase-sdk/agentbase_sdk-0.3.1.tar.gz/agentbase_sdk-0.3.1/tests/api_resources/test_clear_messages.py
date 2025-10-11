# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agentbase import Agentbase, AsyncAgentbase
from tests.utils import assert_matches_type
from agentbase.types import ClearMessageClearResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClearMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear(self, client: Agentbase) -> None:
        clear_message = client.clear_messages.clear(
            session="session",
        )
        assert_matches_type(ClearMessageClearResponse, clear_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear(self, client: Agentbase) -> None:
        response = client.clear_messages.with_raw_response.clear(
            session="session",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_message = response.parse()
        assert_matches_type(ClearMessageClearResponse, clear_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear(self, client: Agentbase) -> None:
        with client.clear_messages.with_streaming_response.clear(
            session="session",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_message = response.parse()
            assert_matches_type(ClearMessageClearResponse, clear_message, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClearMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear(self, async_client: AsyncAgentbase) -> None:
        clear_message = await async_client.clear_messages.clear(
            session="session",
        )
        assert_matches_type(ClearMessageClearResponse, clear_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear(self, async_client: AsyncAgentbase) -> None:
        response = await async_client.clear_messages.with_raw_response.clear(
            session="session",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_message = await response.parse()
        assert_matches_type(ClearMessageClearResponse, clear_message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear(self, async_client: AsyncAgentbase) -> None:
        async with async_client.clear_messages.with_streaming_response.clear(
            session="session",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_message = await response.parse()
            assert_matches_type(ClearMessageClearResponse, clear_message, path=["response"])

        assert cast(Any, response.is_closed) is True
