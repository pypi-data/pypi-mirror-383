from __future__ import annotations

import asyncio
import httpx
import time
import uuid


from ..config import USER_AGENT, API_TIMEOUT
from .._log import io_logger, get_logger
from ..errors import Olostep_APIConnectionError
from .transport_protocol import Transport, RawAPIResponse, RawAPIRequest

logger = get_logger("backend.transport")

try:
    import h2
    USE_HTTP2 = True
except ImportError:
    USE_HTTP2 = False

class HttpxTransport(Transport):
    """
    HTTP Transport Layer for Olostep SDK.

    This class provides the a specialized HTTP transport that is tuned for particularities of the Olostep API.
    Namely, it is tuned for high latency operations and massive concurrency requirements.

    This class can be used directly, but is typically used via the Transport protocol (see: Testing).


    Responsibilities:
    - Low-level HTTP request/response handling using httpx
        - Connection pooling and HTTP/2 support for performance
        - Timeout and connection limit configuration
    - Optional request/response logging for debugging (when enabled)
    - Network-level error handling and transformation


    Seperation of concerns (Non-responsibility):
    The Transport layer is responsible for low-level HTTP communication and only that.
    It does not modify or interpret Input/Output data in any way.

    This means this layer is unaware if a request was successful in the semantic sense.
    So getting a HTTP 504 is success in this layer, getting no response or connection is a failure.

    Error Handling:
    This transport layer purposefully only catches and transforms network-level errors.
    The following errors are transformed into OlostepAPIConnectionError:
        - httpx.ConnectError: Connection failures (DNS, network unreachable, etc.)
        - httpx.TimeoutException: Request timeouts (connect or read timeouts)
        - httpx.RemoteProtocolError: HTTP protocol violations
    HTTP status errors (4xx, 5xx) not considered network-level errors! 
    They are expected to be handled by the caller because they have non-transport semantical meaning and require business logic interpretation. 
    All other errors (JSON parsing, validation) are also left for the caller layer to handle, maintaining clear separation of concerns.


    Testing:
    A faked/stubbed version of this transport is available for testing purposes that can simulate
    API responses without needing to contact the actual Olostep API.
    """
    def __init__(self, api_key: str, *, enable_io_logging: bool = False, max_connection_retries: int = 3) -> None:
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=httpx.Timeout(API_TIMEOUT, connect=30.0),
            limits=httpx.Limits(
                max_keepalive_connections=100,  # More keepalive connections
                max_connections=200,            # Match concurrent request count
            ),
            # Enable HTTP/2 for better multiplexing
            http2=USE_HTTP2,
            # retries=3,
        )
        # self._enable_io_logging = enable_io_logging
        self._max_connection_retries = max_connection_retries

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        request: RawAPIRequest,
    ) -> RawAPIResponse:
        """
        Make an HTTP request with retry logic, exponential backoff, and increasing timeouts.
        
        Retries up to max_connection_retries times if network-level errors occur.
        Uses exponential backoff: 1s, 2s, 4s, ... delays between retries.
        Increases timeout by 15 seconds per retry attempt.
        """
        max_retries = self._max_connection_retries
        base_delay = 1.0
        timeout_bump_per_attempt = 15.0

        # Prepare full request data for logging
        full_headers = dict(self._client.headers)
        if request.headers:
            full_headers.update(request.headers)
        
        for attempt in range(max_retries + 1):
            start_time = time.time()

            # if self._enable_io_logging:
            request_id = f"req_{uuid.uuid4().hex[:12]}"
            io_logger.debug(
                    f"API REQUEST [ref: {request_id}]",
                    extra={
                        "skip_file_logging": True,
                        "request_id": request_id,
                        "I": {
                            "method": request.method,
                            "url": request.url,
                            "query": request.query,
                            "url_formatted": str(httpx.URL(str(request.url)).copy_merge_params(request.query)) if request.query else str(request.url),
                            "headers": full_headers,
                            "json": request.json,
                        }
                    }
                )
            # else:
            #     request_id = None
            
            attempt_timeout=httpx.Timeout(API_TIMEOUT + (attempt * timeout_bump_per_attempt), connect=30.0)

            try:
                response = await self._client.request(
                    request.method, 
                    request.url, 
                    params=request.query, 
                    json=request.json, 
                    headers=full_headers, 
                    timeout=attempt_timeout
                )

                # Get raw response text - no JSON parsing because we get back html if the API is unable to 
                # process the request
                response_text = response.text
                response_time_ms = (time.time() - start_time) * 1000
                
                # Log the response
                # if self._enable_io_logging:
                io_logger.debug(
                    f"API RESPONSE [ref: {request_id}]",
                    extra={
                        "request_id": request_id,
                        "response_time_ms": response_time_ms,
                        "I": {
                            "method": request.method,
                            "url": request.url,
                            "query": request.query,
                            "url_formatted": str(httpx.URL(str(request.url)).copy_merge_params(request.query)) if request.query else str(request.url),
                            "headers": full_headers,
                            "json": request.json,
                        },
                        "O": {
                            "status_code": response.status_code,
                            "headers": dict(response.headers),
                            "body": response_text,
                        }
                    }
                )
                
                return RawAPIResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers), #also lowercase the header keys
                    body=response_text
                )
                
            except (
                httpx.RequestError,
                httpx.InvalidURL,
                httpx.CookieConflict,
                httpx.StreamError
            ) as e:
                # Only handle communication/timeout errors - let caller handle everything else
                response_time_ms = (time.time() - start_time) * 1000

                
                # if self._enable_io_logging:
                io_logger.debug(
                    f"API ERROR '{type(e).__name__}' [ref: {request_id}]",
                    extra={
                        "request_id": request_id,
                        "response_time_ms": response_time_ms,
                        "I": {
                            "method": request.method,
                            "url": request.url,
                            "query": request.query,
                            "url_formatted": str(httpx.URL(str(request.url)).copy_merge_params(request.query)) if request.query else str(request.url),
                            "headers": full_headers,
                            "json": request.json,
                        },
                        "O": {
                            "error": type(e).__name__,
                        }
                    }
                )
                
                if attempt == max_retries:
                    # Last attempt failed, re-raise the error
                    logger.error(f"Connection to API failed terminally after {max_retries + 1} attempts: {e}")
                    raise Olostep_APIConnectionError() from e
                
                # Calculate exponential backoff delay
                delay = base_delay * (2 ** attempt)
                logger.debug(f"API connection attempt {attempt + 1} failed with connection error, retrying in {delay}s (timeout: {attempt_timeout}s): {e}")
                await asyncio.sleep(delay)