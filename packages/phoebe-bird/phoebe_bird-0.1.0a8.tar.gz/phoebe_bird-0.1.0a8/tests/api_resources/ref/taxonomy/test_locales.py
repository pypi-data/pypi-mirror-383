# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from phoebe_bird import Phoebe, AsyncPhoebe
from tests.utils import assert_matches_type
from phoebe_bird.types.ref.taxonomy import LocaleListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLocales:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Phoebe) -> None:
        locale = client.ref.taxonomy.locales.list()
        assert_matches_type(LocaleListResponse, locale, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Phoebe) -> None:
        locale = client.ref.taxonomy.locales.list(
            accept_language="en",
        )
        assert_matches_type(LocaleListResponse, locale, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Phoebe) -> None:
        response = client.ref.taxonomy.locales.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        locale = response.parse()
        assert_matches_type(LocaleListResponse, locale, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Phoebe) -> None:
        with client.ref.taxonomy.locales.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            locale = response.parse()
            assert_matches_type(LocaleListResponse, locale, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLocales:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncPhoebe) -> None:
        locale = await async_client.ref.taxonomy.locales.list()
        assert_matches_type(LocaleListResponse, locale, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncPhoebe) -> None:
        locale = await async_client.ref.taxonomy.locales.list(
            accept_language="en",
        )
        assert_matches_type(LocaleListResponse, locale, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncPhoebe) -> None:
        response = await async_client.ref.taxonomy.locales.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        locale = await response.parse()
        assert_matches_type(LocaleListResponse, locale, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncPhoebe) -> None:
        async with async_client.ref.taxonomy.locales.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            locale = await response.parse()
            assert_matches_type(LocaleListResponse, locale, path=["response"])

        assert cast(Any, response.is_closed) is True
