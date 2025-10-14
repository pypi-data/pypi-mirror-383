# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Query, Headers, NotGiven, not_given
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.integrations.calendar import Calendar

__all__ = ["GoogleCalendarResource", "AsyncGoogleCalendarResource"]


class GoogleCalendarResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GoogleCalendarResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hyperspell/python-sdk#accessing-raw-response-data-eg-headers
        """
        return GoogleCalendarResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GoogleCalendarResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hyperspell/python-sdk#with_streaming_response
        """
        return GoogleCalendarResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Calendar:
        """List available calendars for a user.

        This can be used to ie. populate a dropdown
        for the user to select a calendar.
        """
        return self._get(
            "/integrations/google_calendar/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Calendar,
        )


class AsyncGoogleCalendarResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGoogleCalendarResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hyperspell/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncGoogleCalendarResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGoogleCalendarResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hyperspell/python-sdk#with_streaming_response
        """
        return AsyncGoogleCalendarResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Calendar:
        """List available calendars for a user.

        This can be used to ie. populate a dropdown
        for the user to select a calendar.
        """
        return await self._get(
            "/integrations/google_calendar/list",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Calendar,
        )


class GoogleCalendarResourceWithRawResponse:
    def __init__(self, google_calendar: GoogleCalendarResource) -> None:
        self._google_calendar = google_calendar

        self.list = to_raw_response_wrapper(
            google_calendar.list,
        )


class AsyncGoogleCalendarResourceWithRawResponse:
    def __init__(self, google_calendar: AsyncGoogleCalendarResource) -> None:
        self._google_calendar = google_calendar

        self.list = async_to_raw_response_wrapper(
            google_calendar.list,
        )


class GoogleCalendarResourceWithStreamingResponse:
    def __init__(self, google_calendar: GoogleCalendarResource) -> None:
        self._google_calendar = google_calendar

        self.list = to_streamed_response_wrapper(
            google_calendar.list,
        )


class AsyncGoogleCalendarResourceWithStreamingResponse:
    def __init__(self, google_calendar: AsyncGoogleCalendarResource) -> None:
        self._google_calendar = google_calendar

        self.list = async_to_streamed_response_wrapper(
            google_calendar.list,
        )
