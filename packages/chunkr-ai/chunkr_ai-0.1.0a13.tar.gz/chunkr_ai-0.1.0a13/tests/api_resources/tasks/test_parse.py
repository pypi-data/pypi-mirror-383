# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from chunkr_ai import Chunkr, AsyncChunkr
from tests.utils import assert_matches_type
from chunkr_ai.types.tasks import ParseGetResponse, ParseCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestParse:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Chunkr) -> None:
        parse = client.tasks.parse.create(
            file="file",
        )
        assert_matches_type(ParseCreateResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Chunkr) -> None:
        parse = client.tasks.parse.create(
            file="file",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            file_name="file_name",
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "form_region": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "graphical_item": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "legend": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "line_number": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page_number": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "unknown": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(ParseCreateResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Chunkr) -> None:
        response = client.tasks.parse.with_raw_response.create(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = response.parse()
        assert_matches_type(ParseCreateResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Chunkr) -> None:
        with client.tasks.parse.with_streaming_response.create(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = response.parse()
            assert_matches_type(ParseCreateResponse, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Chunkr) -> None:
        parse = client.tasks.parse.get(
            task_id="task_id",
        )
        assert_matches_type(ParseGetResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Chunkr) -> None:
        parse = client.tasks.parse.get(
            task_id="task_id",
            base64_urls=True,
            include_chunks=True,
        )
        assert_matches_type(ParseGetResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Chunkr) -> None:
        response = client.tasks.parse.with_raw_response.get(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = response.parse()
        assert_matches_type(ParseGetResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Chunkr) -> None:
        with client.tasks.parse.with_streaming_response.get(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = response.parse()
            assert_matches_type(ParseGetResponse, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Chunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.tasks.parse.with_raw_response.get(
                task_id="",
            )


class TestAsyncParse:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.create(
            file="file",
        )
        assert_matches_type(ParseCreateResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.create(
            file="file",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            file_name="file_name",
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "form_region": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "graphical_item": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "legend": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "line_number": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "page_number": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
                "unknown": {
                    "crop_image": "All",
                    "description": True,
                    "extended_context": True,
                    "format": "Html",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(ParseCreateResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncChunkr) -> None:
        response = await async_client.tasks.parse.with_raw_response.create(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = await response.parse()
        assert_matches_type(ParseCreateResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncChunkr) -> None:
        async with async_client.tasks.parse.with_streaming_response.create(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = await response.parse()
            assert_matches_type(ParseCreateResponse, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.get(
            task_id="task_id",
        )
        assert_matches_type(ParseGetResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.get(
            task_id="task_id",
            base64_urls=True,
            include_chunks=True,
        )
        assert_matches_type(ParseGetResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncChunkr) -> None:
        response = await async_client.tasks.parse.with_raw_response.get(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = await response.parse()
        assert_matches_type(ParseGetResponse, parse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncChunkr) -> None:
        async with async_client.tasks.parse.with_streaming_response.get(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = await response.parse()
            assert_matches_type(ParseGetResponse, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncChunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.tasks.parse.with_raw_response.get(
                task_id="",
            )
