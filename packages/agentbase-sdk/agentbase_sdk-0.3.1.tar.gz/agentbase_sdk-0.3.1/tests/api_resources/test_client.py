# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agentbase import Agentbase, AsyncAgentbase

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClient:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_method_run_agent(self, client: Agentbase) -> None:
        client_stream = client.run_agent(
            message="message",
        )
        client_stream.response.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_method_run_agent_with_all_params(self, client: Agentbase) -> None:
        client_stream = client.run_agent(
            message="message",
            session="session",
            datastores=[
                {
                    "id": "id",
                    "name": "name",
                }
            ],
            mcp_servers=[
                {
                    "server_name": "serverName",
                    "server_url": "https://example.com",
                }
            ],
            mode="flash",
            rules=["string"],
            streaming_tokens=True,
            system="system",
        )
        client_stream.response.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_raw_response_run_agent(self, client: Agentbase) -> None:
        response = client.with_raw_response.run_agent(
            message="message",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_streaming_response_run_agent(self, client: Agentbase) -> None:
        with client.with_streaming_response.run_agent(
            message="message",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncClient:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_method_run_agent(self, async_client: AsyncAgentbase) -> None:
        client_stream = await async_client.run_agent(
            message="message",
        )
        await client_stream.response.aclose()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_method_run_agent_with_all_params(self, async_client: AsyncAgentbase) -> None:
        client_stream = await async_client.run_agent(
            message="message",
            session="session",
            datastores=[
                {
                    "id": "id",
                    "name": "name",
                }
            ],
            mcp_servers=[
                {
                    "server_name": "serverName",
                    "server_url": "https://example.com",
                }
            ],
            mode="flash",
            rules=["string"],
            streaming_tokens=True,
            system="system",
        )
        await client_stream.response.aclose()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_raw_response_run_agent(self, async_client: AsyncAgentbase) -> None:
        response = await async_client.with_raw_response.run_agent(
            message="message",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_streaming_response_run_agent(self, async_client: AsyncAgentbase) -> None:
        async with async_client.with_streaming_response.run_agent(
            message="message",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
