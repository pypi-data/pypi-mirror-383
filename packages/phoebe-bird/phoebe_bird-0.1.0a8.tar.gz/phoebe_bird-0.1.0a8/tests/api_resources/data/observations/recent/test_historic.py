# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from phoebe_bird import Phoebe, AsyncPhoebe
from tests.utils import assert_matches_type
from phoebe_bird.types.data.observations.recent import HistoricListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHistoric:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Phoebe) -> None:
        historic = client.data.observations.recent.historic.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
        )
        assert_matches_type(HistoricListResponse, historic, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Phoebe) -> None:
        historic = client.data.observations.recent.historic.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
            cat="species",
            detail="simple",
            hotspot=True,
            include_provisional=True,
            max_results=1,
            r=["string"],
            rank="mrec",
            spp_locale="sppLocale",
        )
        assert_matches_type(HistoricListResponse, historic, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Phoebe) -> None:
        response = client.data.observations.recent.historic.with_raw_response.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        historic = response.parse()
        assert_matches_type(HistoricListResponse, historic, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Phoebe) -> None:
        with client.data.observations.recent.historic.with_streaming_response.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            historic = response.parse()
            assert_matches_type(HistoricListResponse, historic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Phoebe) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `region_code` but received ''"):
            client.data.observations.recent.historic.with_raw_response.list(
                d=1,
                region_code="",
                y=0,
                m=1,
            )


class TestAsyncHistoric:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncPhoebe) -> None:
        historic = await async_client.data.observations.recent.historic.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
        )
        assert_matches_type(HistoricListResponse, historic, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncPhoebe) -> None:
        historic = await async_client.data.observations.recent.historic.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
            cat="species",
            detail="simple",
            hotspot=True,
            include_provisional=True,
            max_results=1,
            r=["string"],
            rank="mrec",
            spp_locale="sppLocale",
        )
        assert_matches_type(HistoricListResponse, historic, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncPhoebe) -> None:
        response = await async_client.data.observations.recent.historic.with_raw_response.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        historic = await response.parse()
        assert_matches_type(HistoricListResponse, historic, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncPhoebe) -> None:
        async with async_client.data.observations.recent.historic.with_streaming_response.list(
            d=1,
            region_code="regionCode",
            y=0,
            m=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            historic = await response.parse()
            assert_matches_type(HistoricListResponse, historic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncPhoebe) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `region_code` but received ''"):
            await async_client.data.observations.recent.historic.with_raw_response.list(
                d=1,
                region_code="",
                y=0,
                m=1,
            )
