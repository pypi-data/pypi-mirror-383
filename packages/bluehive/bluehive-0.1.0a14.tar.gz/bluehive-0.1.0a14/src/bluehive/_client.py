# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import fax, hl7, health, orders, version, database, employees, providers, integrations
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import BlueHiveError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.employers import employers

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "BlueHive",
    "AsyncBlueHive",
    "Client",
    "AsyncClient",
]


class BlueHive(SyncAPIClient):
    health: health.HealthResource
    version: version.VersionResource
    providers: providers.ProvidersResource
    database: database.DatabaseResource
    fax: fax.FaxResource
    employers: employers.EmployersResource
    hl7: hl7.Hl7Resource
    orders: orders.OrdersResource
    employees: employees.EmployeesResource
    integrations: integrations.IntegrationsResource
    with_raw_response: BlueHiveWithRawResponse
    with_streaming_response: BlueHiveWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous BlueHive client instance.

        This automatically infers the `api_key` argument from the `BLUEHIVE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("BLUEHIVE_API_KEY")
        if api_key is None:
            raise BlueHiveError(
                "The api_key client option must be set either by passing api_key to the client or by setting the BLUEHIVE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("BLUE_HIVE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.bluehive.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.health = health.HealthResource(self)
        self.version = version.VersionResource(self)
        self.providers = providers.ProvidersResource(self)
        self.database = database.DatabaseResource(self)
        self.fax = fax.FaxResource(self)
        self.employers = employers.EmployersResource(self)
        self.hl7 = hl7.Hl7Resource(self)
        self.orders = orders.OrdersResource(self)
        self.employees = employees.EmployeesResource(self)
        self.integrations = integrations.IntegrationsResource(self)
        self.with_raw_response = BlueHiveWithRawResponse(self)
        self.with_streaming_response = BlueHiveWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncBlueHive(AsyncAPIClient):
    health: health.AsyncHealthResource
    version: version.AsyncVersionResource
    providers: providers.AsyncProvidersResource
    database: database.AsyncDatabaseResource
    fax: fax.AsyncFaxResource
    employers: employers.AsyncEmployersResource
    hl7: hl7.AsyncHl7Resource
    orders: orders.AsyncOrdersResource
    employees: employees.AsyncEmployeesResource
    integrations: integrations.AsyncIntegrationsResource
    with_raw_response: AsyncBlueHiveWithRawResponse
    with_streaming_response: AsyncBlueHiveWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncBlueHive client instance.

        This automatically infers the `api_key` argument from the `BLUEHIVE_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("BLUEHIVE_API_KEY")
        if api_key is None:
            raise BlueHiveError(
                "The api_key client option must be set either by passing api_key to the client or by setting the BLUEHIVE_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("BLUE_HIVE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.bluehive.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.health = health.AsyncHealthResource(self)
        self.version = version.AsyncVersionResource(self)
        self.providers = providers.AsyncProvidersResource(self)
        self.database = database.AsyncDatabaseResource(self)
        self.fax = fax.AsyncFaxResource(self)
        self.employers = employers.AsyncEmployersResource(self)
        self.hl7 = hl7.AsyncHl7Resource(self)
        self.orders = orders.AsyncOrdersResource(self)
        self.employees = employees.AsyncEmployeesResource(self)
        self.integrations = integrations.AsyncIntegrationsResource(self)
        self.with_raw_response = AsyncBlueHiveWithRawResponse(self)
        self.with_streaming_response = AsyncBlueHiveWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class BlueHiveWithRawResponse:
    def __init__(self, client: BlueHive) -> None:
        self.health = health.HealthResourceWithRawResponse(client.health)
        self.version = version.VersionResourceWithRawResponse(client.version)
        self.providers = providers.ProvidersResourceWithRawResponse(client.providers)
        self.database = database.DatabaseResourceWithRawResponse(client.database)
        self.fax = fax.FaxResourceWithRawResponse(client.fax)
        self.employers = employers.EmployersResourceWithRawResponse(client.employers)
        self.hl7 = hl7.Hl7ResourceWithRawResponse(client.hl7)
        self.orders = orders.OrdersResourceWithRawResponse(client.orders)
        self.employees = employees.EmployeesResourceWithRawResponse(client.employees)
        self.integrations = integrations.IntegrationsResourceWithRawResponse(client.integrations)


class AsyncBlueHiveWithRawResponse:
    def __init__(self, client: AsyncBlueHive) -> None:
        self.health = health.AsyncHealthResourceWithRawResponse(client.health)
        self.version = version.AsyncVersionResourceWithRawResponse(client.version)
        self.providers = providers.AsyncProvidersResourceWithRawResponse(client.providers)
        self.database = database.AsyncDatabaseResourceWithRawResponse(client.database)
        self.fax = fax.AsyncFaxResourceWithRawResponse(client.fax)
        self.employers = employers.AsyncEmployersResourceWithRawResponse(client.employers)
        self.hl7 = hl7.AsyncHl7ResourceWithRawResponse(client.hl7)
        self.orders = orders.AsyncOrdersResourceWithRawResponse(client.orders)
        self.employees = employees.AsyncEmployeesResourceWithRawResponse(client.employees)
        self.integrations = integrations.AsyncIntegrationsResourceWithRawResponse(client.integrations)


class BlueHiveWithStreamedResponse:
    def __init__(self, client: BlueHive) -> None:
        self.health = health.HealthResourceWithStreamingResponse(client.health)
        self.version = version.VersionResourceWithStreamingResponse(client.version)
        self.providers = providers.ProvidersResourceWithStreamingResponse(client.providers)
        self.database = database.DatabaseResourceWithStreamingResponse(client.database)
        self.fax = fax.FaxResourceWithStreamingResponse(client.fax)
        self.employers = employers.EmployersResourceWithStreamingResponse(client.employers)
        self.hl7 = hl7.Hl7ResourceWithStreamingResponse(client.hl7)
        self.orders = orders.OrdersResourceWithStreamingResponse(client.orders)
        self.employees = employees.EmployeesResourceWithStreamingResponse(client.employees)
        self.integrations = integrations.IntegrationsResourceWithStreamingResponse(client.integrations)


class AsyncBlueHiveWithStreamedResponse:
    def __init__(self, client: AsyncBlueHive) -> None:
        self.health = health.AsyncHealthResourceWithStreamingResponse(client.health)
        self.version = version.AsyncVersionResourceWithStreamingResponse(client.version)
        self.providers = providers.AsyncProvidersResourceWithStreamingResponse(client.providers)
        self.database = database.AsyncDatabaseResourceWithStreamingResponse(client.database)
        self.fax = fax.AsyncFaxResourceWithStreamingResponse(client.fax)
        self.employers = employers.AsyncEmployersResourceWithStreamingResponse(client.employers)
        self.hl7 = hl7.AsyncHl7ResourceWithStreamingResponse(client.hl7)
        self.orders = orders.AsyncOrdersResourceWithStreamingResponse(client.orders)
        self.employees = employees.AsyncEmployeesResourceWithStreamingResponse(client.employees)
        self.integrations = integrations.AsyncIntegrationsResourceWithStreamingResponse(client.integrations)


Client = BlueHive

AsyncClient = AsyncBlueHive
