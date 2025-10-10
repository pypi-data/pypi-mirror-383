from __future__ import annotations

import contextlib
import dataclasses
import functools
import logging
import time
import urllib.parse
from typing import TYPE_CHECKING, Any, Self

import aiohttp
import aiohttp_retry

from .base import sanitize_params
from .jsons import TJSONDumpable, TJSONParsed, json_loads

if TYPE_CHECKING:
    from collections.abc import Collection
    from types import TracebackType

LOGGER = logging.getLogger(__name__)


def resp_data_for_debug(resp_data: bytes, max_length: int = 100, cut_suffix: str = "...") -> str:
    # Could avoid decoding resp_data beyond `max_length * 4` or so, but it shouldn't matter much.
    resp_text = resp_data.decode("utf-8", errors="replace")
    if len(resp_text) <= max_length:
        return repr(resp_text)
    return repr(f"{resp_text[:max_length]}{cut_suffix}")


@dataclasses.dataclass()
class HTTPResponse:
    """Simplified wrapper of `aiohttp.ClientResponse` with pre-read body"""

    orig: aiohttp.ClientResponse
    content: bytes
    time_taken_sec: float

    max_resp_log_len: int | None = None

    @property
    def status(self) -> int:
        return self.orig.status

    def json(self) -> TJSONParsed:
        return json_loads(self.content)

    def json_untyped(self) -> Any:
        return json_loads(self.content)

    @functools.cached_property
    def str_for_log(self) -> str:
        result = f"{self.status}, {len(self.content)}b in {self.time_taken_sec:.3f}s"
        if self.max_resp_log_len:
            debug_data = resp_data_for_debug(self.content, self.max_resp_log_len)
            result = f"{result} data={debug_data}"
        return result


@dataclasses.dataclass()
class HTTPClient:
    session: aiohttp.ClientSession | None = None
    _session_managed: bool = False
    logger: logging.Logger = LOGGER

    retry_statuses: Collection[int] = frozenset({429, *range(500, 600)})
    retry_attempts: int = 5
    retry_start_timeout_sec: float = 0.5
    default_timeout_sec: float = 5.0
    max_resp_log_len: int = 300
    max_resp_error_message_len: int = 1000

    @staticmethod
    def make_url_for_log(url: str, params: dict[str, Any]) -> str:
        """
        Join url with the query parameters, sanitizing the parameters as needed.

        Warning: Does not necessarily match the aiohttp's logic;
        should not be considered a securely correct representation.

        >>> make_url_for_log = HTTPClient.make_url_for_log
        >>> make_url_for_log("http://example.com", dict(val="a", apiKey="b" * 20))
        'http://example.com?val=a&apiKey=bb...bb'
        >>> make_url_for_log("http://example.com?val=0a&inparam=123", dict(val="a", apiKey="b" * 20))
        'http://example.com?val=0a&inparam=123&val=a&apiKey=bb...bb'
        """
        params_clean = sanitize_params(params)
        params_s = urllib.parse.urlencode(params_clean)
        return f"{url}&{params_s}" if "?" in url else f"{url}?{params_s}"

    @property
    def _retry_options(self) -> aiohttp_retry.RetryOptionsBase:
        return aiohttp_retry.ExponentialRetry(
            attempts=self.retry_attempts,
            start_timeout=self.retry_start_timeout_sec,
            max_timeout=self.default_timeout_sec,
            statuses=set(self.retry_statuses),
        )

    async def __aenter__(self) -> Self:
        if self.session is None:
            assert not self._session_managed
            self._session_managed = True
            self.session = aiohttp.ClientSession()
            await self.session.__aenter__()

        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self._session_managed:
            assert self.session is not None
            session = self.session
            self.session = None
            self._session_managed = False
            await session.__aexit__(exc_type, exc_value, exc_tb)

    async def close(self) -> None:
        await self.__aexit__(None, None, None)

    async def req(
        self,
        url: str,
        *,
        method: str = "get",
        params: dict[str, Any] | None = None,
        require_ok: bool = True,
        retry_options: aiohttp_retry.RetryOptionsBase | None = None,
        **kwargs: Any,
    ) -> HTTPResponse:
        do_logging = self.logger.isEnabledFor(logging.DEBUG)
        if do_logging:
            url_for_log = self.make_url_for_log(url, params or {})
            req_log_s = f"{method.upper()} {url_for_log}"
            self.logger.debug("HTTP request: %s", req_log_s)

        async with contextlib.AsyncExitStack() as acm:
            sess = self.session
            # Making the `__aenter__` of this client optional
            # (in which case it creates a session-per-request)
            if sess is None:
                sess = await acm.enter_async_context(aiohttp.ClientSession())

            retry_client = aiohttp_retry.RetryClient(sess, retry_options=retry_options or self._retry_options)
            start_time = time.monotonic()
            async with retry_client.request(
                method, url, params=params or {}, timeout=self.default_timeout_sec, **kwargs
            ) as resp:
                resp_content = await resp.read()
                wrapped_resp = HTTPResponse(
                    orig=resp,
                    content=resp_content,
                    time_taken_sec=time.monotonic() - start_time,
                    max_resp_log_len=self.max_resp_log_len,
                )

                try:
                    if require_ok:
                        resp.raise_for_status()
                except aiohttp.ClientResponseError as exc:
                    resp_text_cut = resp_data_for_debug(resp_content, self.max_resp_error_message_len)
                    resp_text_msg = f"resp_text[:{self.max_resp_error_message_len}]={resp_text_cut}"
                    exc.message = f"{exc.message}; {resp_text_msg}"
                    if do_logging:
                        self.logger.debug(
                            "HTTP response exception: %s -> %s, %s", req_log_s, wrapped_resp.str_for_log, exc.message
                        )
                    raise

                if do_logging:
                    LOGGER.debug("HTTP response: %s -> %s", req_log_s, wrapped_resp.str_for_log)

        return wrapped_resp

    async def req_jsonrpc(
        self,
        url: str,
        jsonrpc_method: str,
        params: TJSONDumpable,
        request_id: str | None = None,
        jsonrpc_version: str | None = "2.0",
        **kwargs: Any,
    ) -> Any:
        data = {"method": jsonrpc_method, "params": params}
        if jsonrpc_version is not None:
            data["jsonrpc"] = jsonrpc_version
        if request_id is not None:
            data["id"] = request_id

        resp = await self.req(url, method="post", json=data, **kwargs)
        resp_data = resp.json_untyped()

        if not isinstance(resp_data, dict):
            raise ValueError(f"Unexpected JSONRPC response type: {type(resp_data)}, {repr(resp_data)[:1024]=!r}")
        # Not including any sanity validation ("jsonrpc", "id")
        result = resp_data.get("result")
        error = resp_data.get("error")

        if error is not None:
            if result is not None:
                LOGGER.warning("JSONRPC with both error and result: %r, %s", error, repr(result)[:2048])
                return result

            raise ValueError(f"JSONRPC error: {error!r}")

        return result
