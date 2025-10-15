from __future__ import annotations

import typing

from .client import Client
from .models import Response
from .settings import (DEFAULT_FOLLOW_REDIRECTS, DEFAULT_TIMEOUT,
                       DEFAULT_TLS_HTTP2, DEFAULT_TLS_IDENTIFIER)
from .types import (AuthTypes, CookieTypes, HeaderTypes, MethodTypes,
                    ProtocolTypes, ProxyTypes, RequestData, RequestFiles,
                    TimeoutTypes, TLSIdentifierTypes, URLParamTypes, URLTypes)

__all__ = [
    "delete",
    "get",
    "head",
    "options",
    "patch",
    "post",
    "put",
    "request",
]


def request(
    method: MethodTypes,
    url: URLTypes,
    *,
    params: URLParamTypes = None,
    data: RequestData = None,
    files: RequestFiles = None,
    json: typing.Any = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: AuthTypes = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
        Constructs and sends an HTTP request.

        This method builds a `Request` object based on the given parameters, sends
        it using the configured client, and returns the server's response.

        Parameters:
            - **method** (str): HTTP method to use (e.g., `"GET"`, `"POST"`).
            - **url** (URLTypes): The URL to send the request to.
            - **params** (optional): Query parameters to include in the request URL.
            - **data** (optional): Form data to include in the request body.
            - **json** (optional): A JSON serializable object to include in the request body.
            - **headers** (optional): Custom headers to include in the request.
            - **cookies** (optional): Cookies to include with the request.
            - **files** (optional): Files to upload in a multipart request.
            - **auth** (optional): Authentication credentials or handler.
            - **timeout** (optional): Timeout configuration for the request.
            - **follow_redirects** (optional): Whether to follow HTTP redirects.

        Returns:
            - **Response**: The client's response to the HTTP request.

        Usage:
            ```python

    import tls_requests
                >>> with tls_requests.Client() as sync_client:
                        r = sync_client.request('GET', 'https://httpbin.org/get')
                >>> r
                <Response [200]>
            ```
    """

    with Client(
        cookies=cookies,
        proxy=proxy,
        http2=http2,
        timeout=timeout,
        verify=verify,
        client_identifier=tls_identifier,
        **config,
    ) as client:
        return client.request(
            method=method,
            url=url,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
        )


def get(
    url: URLTypes,
    *,
    params: URLParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: AuthTypes = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
    Sends a `GET` request.

    **Parameters**: See `tls_requests.request`.

    Note that the `data`, `files`, `json` and `content` parameters are not available
    on this function, as `GET` requests should not include a request body.
    """
    return request(
        "GET",
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        proxy=proxy,
        http2=http2,
        follow_redirects=follow_redirects,
        timeout=timeout,
        verify=verify,
        tls_identifier=tls_identifier,
        **config,
    )


def options(
    url: URLTypes,
    *,
    params: URLParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: AuthTypes = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
    Sends an `OPTIONS` request.

    **Parameters**: See `tls_requests.request`.

    Note that the `data`, `files`, `json` and `content` parameters are not available
    on this function, as `OPTIONS` requests should not include a request body.
    """
    return request(
        "OPTIONS",
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        proxy=proxy,
        http2=http2,
        follow_redirects=follow_redirects,
        timeout=timeout,
        verify=verify,
        tls_identifier=tls_identifier,
        **config,
    )


def head(
    url: URLTypes,
    *,
    params: URLParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: AuthTypes = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
    Sends a `HEAD` request.

    **Parameters**: See `tls_requests.request`.

    Note that the `data`, `files`, `json` and `content` parameters are not available
    on this function, as `HEAD` requests should not include a request body.
    """
    return request(
        "HEAD",
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        proxy=proxy,
        http2=http2,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        tls_identifier=tls_identifier,
        **config,
    )


def post(
    url: URLTypes,
    *,
    data: RequestData = None,
    files: RequestFiles = None,
    json: typing.Any = None,
    params: URLParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: AuthTypes = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
    Sends a `POST` request.

    **Parameters**: See `tls_requests.request`.
    """
    return request(
        "POST",
        url,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        proxy=proxy,
        http2=http2,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        tls_identifier=tls_identifier,
        **config,
    )


def put(
    url: URLTypes,
    *,
    data: RequestData = None,
    files: RequestFiles = None,
    json: typing.Any = None,
    params: URLParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: AuthTypes = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
    Sends a `PUT` request.

    **Parameters**: See `tls_requests.request`.
    """
    return request(
        "PUT",
        url,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        proxy=proxy,
        http2=http2,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        tls_identifier=tls_identifier,
        **config,
    )


def patch(
    url: URLTypes,
    *,
    data: RequestData = None,
    files: RequestFiles = None,
    json: typing.Any = None,
    params: URLParamTypes = None,
    headers: HeaderTypes = None,
    cookies: CookieTypes = None,
    auth: AuthTypes = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
    Sends a `PATCH` request.

    **Parameters**: See `tls_requests.request`.
    """
    return request(
        "PATCH",
        url,
        data=data,
        files=files,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        proxy=proxy,
        http2=http2,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        tls_identifier=tls_identifier,
        **config,
    )


def delete(
    url: URLTypes,
    *,
    params: URLParamTypes | None = None,
    headers: HeaderTypes | None = None,
    cookies: CookieTypes | None = None,
    auth: AuthTypes | None = None,
    proxy: ProxyTypes = None,
    http2: ProtocolTypes = DEFAULT_TLS_HTTP2,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT,
    follow_redirects: bool = DEFAULT_FOLLOW_REDIRECTS,
    verify: bool = True,
    tls_identifier: TLSIdentifierTypes = DEFAULT_TLS_IDENTIFIER,
    **config,
) -> Response:
    """
    Sends a `DELETE` request.

    **Parameters**: See `tls_requests.request`.

    Note that the `data`, `files`, `json` and `content` parameters are not available
    on this function, as `DELETE` requests should not include a request body.
    """
    return request(
        "DELETE",
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        proxy=proxy,
        http2=http2,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        tls_identifier=tls_identifier,
        **config,
    )
