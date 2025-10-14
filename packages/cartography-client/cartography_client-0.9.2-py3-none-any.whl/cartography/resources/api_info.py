# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import Body, Query, Headers, NotGiven, not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.api_info_retrieve_response import APIInfoRetrieveResponse

__all__ = ["APIInfoResource", "AsyncAPIInfoResource"]


class APIInfoResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> APIInfoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return APIInfoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> APIInfoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return APIInfoResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIInfoRetrieveResponse:
        """Root endpoint with API information"""
        return self._get(
            "/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIInfoRetrieveResponse,
        )


class AsyncAPIInfoResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAPIInfoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/evrimai/cartography-client#accessing-raw-response-data-eg-headers
        """
        return AsyncAPIInfoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAPIInfoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/evrimai/cartography-client#with_streaming_response
        """
        return AsyncAPIInfoResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIInfoRetrieveResponse:
        """Root endpoint with API information"""
        return await self._get(
            "/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIInfoRetrieveResponse,
        )


class APIInfoResourceWithRawResponse:
    def __init__(self, api_info: APIInfoResource) -> None:
        self._api_info = api_info

        self.retrieve = to_raw_response_wrapper(
            api_info.retrieve,
        )


class AsyncAPIInfoResourceWithRawResponse:
    def __init__(self, api_info: AsyncAPIInfoResource) -> None:
        self._api_info = api_info

        self.retrieve = async_to_raw_response_wrapper(
            api_info.retrieve,
        )


class APIInfoResourceWithStreamingResponse:
    def __init__(self, api_info: APIInfoResource) -> None:
        self._api_info = api_info

        self.retrieve = to_streamed_response_wrapper(
            api_info.retrieve,
        )


class AsyncAPIInfoResourceWithStreamingResponse:
    def __init__(self, api_info: AsyncAPIInfoResource) -> None:
        self._api_info = api_info

        self.retrieve = async_to_streamed_response_wrapper(
            api_info.retrieve,
        )
