# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from phoebe_bird import Phoebe, AsyncPhoebe
from tests.utils import assert_matches_type
from phoebe_bird.types.data.observations.nearest import GeoSpecieListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGeoSpecies:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Phoebe) -> None:
        geo_specie = client.data.observations.nearest.geo_species.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
        )
        assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Phoebe) -> None:
        geo_specie = client.data.observations.nearest.geo_species.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
            back=1,
            dist=0,
            hotspot=True,
            include_provisional=True,
            max_results=1,
            spp_locale="sppLocale",
        )
        assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Phoebe) -> None:
        response = client.data.observations.nearest.geo_species.with_raw_response.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geo_specie = response.parse()
        assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Phoebe) -> None:
        with client.data.observations.nearest.geo_species.with_streaming_response.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geo_specie = response.parse()
            assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Phoebe) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `species_code` but received ''"):
            client.data.observations.nearest.geo_species.with_raw_response.list(
                species_code="",
                lat=-90,
                lng=-180,
            )


class TestAsyncGeoSpecies:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncPhoebe) -> None:
        geo_specie = await async_client.data.observations.nearest.geo_species.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
        )
        assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncPhoebe) -> None:
        geo_specie = await async_client.data.observations.nearest.geo_species.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
            back=1,
            dist=0,
            hotspot=True,
            include_provisional=True,
            max_results=1,
            spp_locale="sppLocale",
        )
        assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncPhoebe) -> None:
        response = await async_client.data.observations.nearest.geo_species.with_raw_response.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geo_specie = await response.parse()
        assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncPhoebe) -> None:
        async with async_client.data.observations.nearest.geo_species.with_streaming_response.list(
            species_code="speciesCode",
            lat=-90,
            lng=-180,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geo_specie = await response.parse()
            assert_matches_type(GeoSpecieListResponse, geo_specie, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncPhoebe) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `species_code` but received ''"):
            await async_client.data.observations.nearest.geo_species.with_raw_response.list(
                species_code="",
                lat=-90,
                lng=-180,
            )
