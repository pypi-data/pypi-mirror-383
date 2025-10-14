# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, Iterable, Optional, cast

import httpx

from ..types import job_get_params, job_upsert_params, job_upsert_from_jsonl_params, job_retrieve_term_based_params
from .._types import Body, Omit, Query, Headers, NotGiven, FileTypes, SequenceNotStr, omit, not_given
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.job_get_response import JobGetResponse
from ..types.job_upsert_response import JobUpsertResponse
from ..types.job_upsert_from_jsonl_response import JobUpsertFromJSONLResponse
from ..types.job_retrieve_term_based_response import JobRetrieveTermBasedResponse

__all__ = ["JobsResource", "AsyncJobsResource"]


class JobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> JobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/pilfo/rainbows#accessing-raw-response-data-eg-headers
        """
        return JobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> JobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/pilfo/rainbows#with_streaming_response
        """
        return JobsResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        board_url_contains: Optional[str] | Omit = omit,
        board_urls: Optional[SequenceNotStr[str]] | Omit = omit,
        countries: Optional[Iterable[job_get_params.Country]] | Omit = omit,
        description_terms: Optional[job_get_params.DescriptionTerms] | Omit = omit,
        last_scraped_date_range: Optional[job_get_params.LastScrapedDateRange] | Omit = omit,
        null_columns: Optional[SequenceNotStr[str]] | Omit = omit,
        page_number: int | Omit = omit,
        page_size: int | Omit = omit,
        title_terms: Optional[job_get_params.TitleTerms] | Omit = omit,
        urls: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobGetResponse:
        """
        Find jobs based on various criteria.

        This endpoint allows you to search for jobs using multiple parameters such as
        board URLs, job titles, descriptions, countries, and more. The results are
        paginated for easier navigation.

        Args:
          board_url_contains: Selects for all board urls which contain it

          board_urls: Board urls to search

          countries: List of countries to filter jobs

          description_terms: Filter configuration for term-based searches

          last_scraped_date_range: Represents a period of time between two dates

          null_columns: List of columns that should be null

          page_number: Page number for pagination

          page_size: Number of results per page

          title_terms: Filter configuration for term-based searches

          urls: Specific job urls to fetch. If not None, all other parameters are ignored.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/jobs/get",
            body=maybe_transform(
                {
                    "board_url_contains": board_url_contains,
                    "board_urls": board_urls,
                    "countries": countries,
                    "description_terms": description_terms,
                    "last_scraped_date_range": last_scraped_date_range,
                    "null_columns": null_columns,
                    "page_number": page_number,
                    "page_size": page_size,
                    "title_terms": title_terms,
                    "urls": urls,
                },
                job_get_params.JobGetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobGetResponse,
        )

    def retrieve_term_based(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobRetrieveTermBasedResponse:
        """
        Search for jobs using natural language queries.

        This endpoint accepts natural language descriptions of job search criteria and
        converts them into structured filters before searching the database.

        Example queries:

        - "Find software engineering jobs in the US posted in March"
        - "Show me marketing positions in Europe from the last week"
        - "Get remote developer jobs that don't require management experience"

        Args:
          query: Natural language query to search for jobs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/jobs/retrieve_term_based",
            body=maybe_transform({"query": query}, job_retrieve_term_based_params.JobRetrieveTermBasedParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobRetrieveTermBasedResponse,
        )

    def upsert(
        self,
        *,
        jobs: Iterable[job_upsert_params.Job],
        batch_size: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobUpsertResponse:
        """
        Upsert (insert or update) a list of jobs.

        Args:
          jobs: List of jobs to upsert

          batch_size: Optional batch size for processing

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/jobs/upsert",
            body=maybe_transform(
                {
                    "jobs": jobs,
                    "batch_size": batch_size,
                },
                job_upsert_params.JobUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobUpsertResponse,
        )

    def upsert_from_jsonl(
        self,
        *,
        file: FileTypes,
        batch_size: int | Omit = omit,
        chunk_size: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobUpsertFromJSONLResponse:
        """Upsert jobs from a JSONL file in streaming chunks.

        The server does not keep the
        entire file in memory.

        Args: file: JSONL file to upload chunk_size: Number of jobs to accumulate before
        upserting (default: 20000) batch_size: Batch size for database operations
        (default: 20000)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/jobs/upsert_from_jsonl",
            body=maybe_transform(body, job_upsert_from_jsonl_params.JobUpsertFromJSONLParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "batch_size": batch_size,
                        "chunk_size": chunk_size,
                    },
                    job_upsert_from_jsonl_params.JobUpsertFromJSONLParams,
                ),
            ),
            cast_to=JobUpsertFromJSONLResponse,
        )


class AsyncJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/pilfo/rainbows#accessing-raw-response-data-eg-headers
        """
        return AsyncJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/pilfo/rainbows#with_streaming_response
        """
        return AsyncJobsResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        board_url_contains: Optional[str] | Omit = omit,
        board_urls: Optional[SequenceNotStr[str]] | Omit = omit,
        countries: Optional[Iterable[job_get_params.Country]] | Omit = omit,
        description_terms: Optional[job_get_params.DescriptionTerms] | Omit = omit,
        last_scraped_date_range: Optional[job_get_params.LastScrapedDateRange] | Omit = omit,
        null_columns: Optional[SequenceNotStr[str]] | Omit = omit,
        page_number: int | Omit = omit,
        page_size: int | Omit = omit,
        title_terms: Optional[job_get_params.TitleTerms] | Omit = omit,
        urls: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobGetResponse:
        """
        Find jobs based on various criteria.

        This endpoint allows you to search for jobs using multiple parameters such as
        board URLs, job titles, descriptions, countries, and more. The results are
        paginated for easier navigation.

        Args:
          board_url_contains: Selects for all board urls which contain it

          board_urls: Board urls to search

          countries: List of countries to filter jobs

          description_terms: Filter configuration for term-based searches

          last_scraped_date_range: Represents a period of time between two dates

          null_columns: List of columns that should be null

          page_number: Page number for pagination

          page_size: Number of results per page

          title_terms: Filter configuration for term-based searches

          urls: Specific job urls to fetch. If not None, all other parameters are ignored.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/jobs/get",
            body=await async_maybe_transform(
                {
                    "board_url_contains": board_url_contains,
                    "board_urls": board_urls,
                    "countries": countries,
                    "description_terms": description_terms,
                    "last_scraped_date_range": last_scraped_date_range,
                    "null_columns": null_columns,
                    "page_number": page_number,
                    "page_size": page_size,
                    "title_terms": title_terms,
                    "urls": urls,
                },
                job_get_params.JobGetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobGetResponse,
        )

    async def retrieve_term_based(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobRetrieveTermBasedResponse:
        """
        Search for jobs using natural language queries.

        This endpoint accepts natural language descriptions of job search criteria and
        converts them into structured filters before searching the database.

        Example queries:

        - "Find software engineering jobs in the US posted in March"
        - "Show me marketing positions in Europe from the last week"
        - "Get remote developer jobs that don't require management experience"

        Args:
          query: Natural language query to search for jobs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/jobs/retrieve_term_based",
            body=await async_maybe_transform(
                {"query": query}, job_retrieve_term_based_params.JobRetrieveTermBasedParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobRetrieveTermBasedResponse,
        )

    async def upsert(
        self,
        *,
        jobs: Iterable[job_upsert_params.Job],
        batch_size: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobUpsertResponse:
        """
        Upsert (insert or update) a list of jobs.

        Args:
          jobs: List of jobs to upsert

          batch_size: Optional batch size for processing

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/jobs/upsert",
            body=await async_maybe_transform(
                {
                    "jobs": jobs,
                    "batch_size": batch_size,
                },
                job_upsert_params.JobUpsertParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobUpsertResponse,
        )

    async def upsert_from_jsonl(
        self,
        *,
        file: FileTypes,
        batch_size: int | Omit = omit,
        chunk_size: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> JobUpsertFromJSONLResponse:
        """Upsert jobs from a JSONL file in streaming chunks.

        The server does not keep the
        entire file in memory.

        Args: file: JSONL file to upload chunk_size: Number of jobs to accumulate before
        upserting (default: 20000) batch_size: Batch size for database operations
        (default: 20000)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/jobs/upsert_from_jsonl",
            body=await async_maybe_transform(body, job_upsert_from_jsonl_params.JobUpsertFromJSONLParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "batch_size": batch_size,
                        "chunk_size": chunk_size,
                    },
                    job_upsert_from_jsonl_params.JobUpsertFromJSONLParams,
                ),
            ),
            cast_to=JobUpsertFromJSONLResponse,
        )


class JobsResourceWithRawResponse:
    def __init__(self, jobs: JobsResource) -> None:
        self._jobs = jobs

        self.get = to_raw_response_wrapper(
            jobs.get,
        )
        self.retrieve_term_based = to_raw_response_wrapper(
            jobs.retrieve_term_based,
        )
        self.upsert = to_raw_response_wrapper(
            jobs.upsert,
        )
        self.upsert_from_jsonl = to_raw_response_wrapper(
            jobs.upsert_from_jsonl,
        )


class AsyncJobsResourceWithRawResponse:
    def __init__(self, jobs: AsyncJobsResource) -> None:
        self._jobs = jobs

        self.get = async_to_raw_response_wrapper(
            jobs.get,
        )
        self.retrieve_term_based = async_to_raw_response_wrapper(
            jobs.retrieve_term_based,
        )
        self.upsert = async_to_raw_response_wrapper(
            jobs.upsert,
        )
        self.upsert_from_jsonl = async_to_raw_response_wrapper(
            jobs.upsert_from_jsonl,
        )


class JobsResourceWithStreamingResponse:
    def __init__(self, jobs: JobsResource) -> None:
        self._jobs = jobs

        self.get = to_streamed_response_wrapper(
            jobs.get,
        )
        self.retrieve_term_based = to_streamed_response_wrapper(
            jobs.retrieve_term_based,
        )
        self.upsert = to_streamed_response_wrapper(
            jobs.upsert,
        )
        self.upsert_from_jsonl = to_streamed_response_wrapper(
            jobs.upsert_from_jsonl,
        )


class AsyncJobsResourceWithStreamingResponse:
    def __init__(self, jobs: AsyncJobsResource) -> None:
        self._jobs = jobs

        self.get = async_to_streamed_response_wrapper(
            jobs.get,
        )
        self.retrieve_term_based = async_to_streamed_response_wrapper(
            jobs.retrieve_term_based,
        )
        self.upsert = async_to_streamed_response_wrapper(
            jobs.upsert,
        )
        self.upsert_from_jsonl = async_to_streamed_response_wrapper(
            jobs.upsert_from_jsonl,
        )
