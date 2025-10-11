# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from agentbase import Agentbase, AsyncAgentbase

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAgent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_method_run(self, client: Agentbase) -> None:
        agent_stream = client.agent.run(
            message="message",
        )
        agent_stream.response.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_method_run_with_all_params(self, client: Agentbase) -> None:
        agent_stream = client.agent.run(
            message="message",
            session="session",
            background=True,
            callback={
                "url": "https://example.com",
                "headers": {"foo": "string"},
            },
            datastores=[
                {
                    "id": "id",
                    "name": "name",
                }
            ],
            final_output={
                "name": "name",
                "schema": {},
                "strict": True,
            },
            mcp_servers=[
                {
                    "server_name": "serverName",
                    "server_url": "https://example.com",
                }
            ],
            mode="flash",
            queries=[
                {
                    "description": "description",
                    "name": "name",
                    "query": "query",
                }
            ],
            rules=["string"],
            streaming_tokens=True,
            system="system",
            workflows=[
                {
                    "id": "id",
                    "description": "description",
                    "name": "name",
                    "steps": [
                        {
                            "id": "id",
                            "depends_on": ["string"],
                            "description": "description",
                            "name": "name",
                            "optional": True,
                            "output_schema": {},
                            "retry_policy": {
                                "backoff": "backoff",
                                "max_attempts": 0,
                            },
                        }
                    ],
                }
            ],
        )
        agent_stream.response.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_raw_response_run(self, client: Agentbase) -> None:
        response = client.agent.with_raw_response.run(
            message="message",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    def test_streaming_response_run(self, client: Agentbase) -> None:
        with client.agent.with_streaming_response.run(
            message="message",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncAgent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_method_run(self, async_client: AsyncAgentbase) -> None:
        agent_stream = await async_client.agent.run(
            message="message",
        )
        await agent_stream.response.aclose()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncAgentbase) -> None:
        agent_stream = await async_client.agent.run(
            message="message",
            session="session",
            background=True,
            callback={
                "url": "https://example.com",
                "headers": {"foo": "string"},
            },
            datastores=[
                {
                    "id": "id",
                    "name": "name",
                }
            ],
            final_output={
                "name": "name",
                "schema": {},
                "strict": True,
            },
            mcp_servers=[
                {
                    "server_name": "serverName",
                    "server_url": "https://example.com",
                }
            ],
            mode="flash",
            queries=[
                {
                    "description": "description",
                    "name": "name",
                    "query": "query",
                }
            ],
            rules=["string"],
            streaming_tokens=True,
            system="system",
            workflows=[
                {
                    "id": "id",
                    "description": "description",
                    "name": "name",
                    "steps": [
                        {
                            "id": "id",
                            "depends_on": ["string"],
                            "description": "description",
                            "name": "name",
                            "optional": True,
                            "output_schema": {},
                            "retry_policy": {
                                "backoff": "backoff",
                                "max_attempts": 0,
                            },
                        }
                    ],
                }
            ],
        )
        await agent_stream.response.aclose()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncAgentbase) -> None:
        response = await async_client.agent.with_raw_response.run(
            message="message",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism doesn't support text/event-stream responses")
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncAgentbase) -> None:
        async with async_client.agent.with_streaming_response.run(
            message="message",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
