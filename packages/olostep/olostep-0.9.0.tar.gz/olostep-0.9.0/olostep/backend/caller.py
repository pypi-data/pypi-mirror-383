from __future__ import annotations

import asyncio
import json
from typing import Any
from pydantic import ValidationError
import pprint
from olostep.models.response import Country

from .api_endpoints import EndpointContract
from .transport_protocol import Transport, RawAPIResponse, RawAPIRequest
from ..errors import (
    OlostepServerError_CreditsExhausted,
    OlostepServerError_NetworkBusy,
    OlostepServerError_ResourceNotFound,
    OlostepServerError_InternalNetworkIssue,
    OlostepServerError_OutOfResources,
    OlostepServerError_UnknownIssue,
    OlostepServerError_AuthFailed,
    OlostepServerError_InvalidEndpointCalled,
    OlostepServerError_BlacklistedDomain,
    OlostepServerError_FeatureApprovalRequired,
    # OlostepRateLimitError,
    OlostepServerError_RequestUnprocessable,
    OlostepServerError_NoResultInResponse,
    OlostepServerError_TemporaryIssue,
    OlostepClientError_RequestValidationFailed,
    OlostepClientError_ResponseValidationFailed,
    OlostepServerError_ResourceNotFound,
    OlostepServerError_ParserNotFound
)
from .._log import get_logger

logger = get_logger("backend.caller")
# T = TypeVar('T')

class EndpointCaller:
    def __init__(self, transport: Transport, base_url: str, api_key: str, max_retries: int = 3) -> None:
        self._transport = transport
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._max_retries = max_retries



    def _handle_errors(self, request: RawAPIRequest, response: RawAPIResponse) -> None:
        body = response.body

        parsed_body: dict[str, Any] | None = None
        if isinstance(body, dict):
            parsed_body = body
        else:
            try:
                parsed_body = json.loads(body)
            except Exception:
                parsed_body = None


        
        # The API has weak input validation, so we need to handle two bad requests cases as the same error.
        if response.status_code in [400, 500]:
            body = response.body

            # Special case: parser not found error
            if parsed_body:
                error = parsed_body.get("error") or parsed_body
                message = error.get("message") if isinstance(error, dict) else None
                if message and "no parser with this name and/or version found" in message.lower():
                    raise OlostepServerError_ParserNotFound(request=request, response=response)

            raise OlostepServerError_RequestUnprocessable(request=request, response=response)

        if response.status_code == 401:
            raise OlostepServerError_BlacklistedDomain()

        if response.status_code == 402:
            body = response.body

            # Special case: credit exhausted error
            if parsed_body:
                usage_limit_reached = parsed_body.get("usage_limit_reached", False)
                if usage_limit_reached:
                    message = parsed_body.get("message")
                    raise OlostepServerError_CreditsExhausted(message=message)
            # fallback to authentication error
            raise OlostepServerError_AuthFailed(api_key=self._api_key)

        if response.status_code == 403:
            # Check for invalid API endpoint error first
            if (response.headers.get("x-amzn-ErrorType", response.headers.get("x-amzn-errortype")) == "IncompleteSignatureException" \
                and "Invalid key=value pair" in response.body):
                raise OlostepServerError_InvalidEndpointCalled(
                    request.url,
                    request.method,
                    {"body": response.body, "headers": response.headers}
                )
            else:
                # Fallback to feature approval required error
                raise OlostepServerError_FeatureApprovalRequired()
        
        if response.status_code == 404:
            if parsed_body:
                # special case: not enough scraping resources available for a given (usually specific) request.
                if (parsed_body.get("malformed_request") is False and parsed_body.get("message", "").lower() == "not enough resources available for the batch execution."):
                    raise OlostepServerError_OutOfResources(request=request, response=response)
            # if "not_found" in response.body:
            raise OlostepServerError_ResourceNotFound(server_response=response.body)
            
        # if response.status_code == 429:
        #     raise OlostepRateLimitError(status_code=response.status_code, message="Rate limit exceeded")

        if response.status_code == 501:
            body = response.body
            # We do not assume we get valid JSON for errors so we to work with strings
            if (
                (isinstance(body, dict) and body.get("max_capacity_reached") is True)
                or (
                    isinstance(body, str)
                    and '"max_capacity_reached":true' in body.replace("'", '"').lower().replace(" ", "")
                )
            ):
                raise OlostepServerError_NetworkBusy()
        
        # only obsever with crawl endpoint
        if response.status_code == 502:
            raise OlostepServerError_RequestUnprocessable(request=request, response=response)
        
        if response.status_code == 503:
            # only obseved on batch start with parser and invalid country. 
            # need investigation.

            if (
                parsed_body is not None
                and parsed_body.get("malformed_request") is False
                and parsed_body.get("message", "").lower() == "not enough resources available for the batch execution."
                and (request.json.get("country") not in [c.value for c in Country])
            ):
                # "body": {
                #   "malformed_request": false,
                #   "message": "Not enough resources available for the batch execution."
                # }
                raise OlostepServerError_RequestUnprocessable(request=request, response=response)


        if response.status_code == 504:
            # Differentiate between timeout and network error based on response content
            if isinstance(response.body, str) and "Network error communicating with endpoint" in response.body:
                # JSON response with network error message - transient issue that can be retried
                raise OlostepServerError_InternalNetworkIssue()
            else:
                # HTML response or other content - true timeout that should not be retried
                raise OlostepServerError_NoResultInResponse()

        # fallback to unknown server issued error
        raise OlostepServerError_UnknownIssue(status_code=response.status_code, server_response={"body": response.body, "headers": response.headers})



    def _prepare_request(
        self,
        contract: EndpointContract,
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: dict[str, Any] | None = None,
    ) -> RawAPIRequest:
        """
        Prepare the request.
        """
        return RawAPIRequest(
            method=contract.method,
            url=f"{self._base_url}/{contract.formatted_path(path_params=path_params)}",
            query=query_params,
            json=body_params,
            headers=None
        )


    def _handle_response(
        self,
        request: RawAPIRequest,
        response: RawAPIResponse,
        contract: EndpointContract,
    ) -> Any:
        """
        Process the response, handle errors, and return parsed data.
        """
        request = request
        # We handle non-transport errors here and translate
        # them to their actual semantic meaning (not the standard HTTP status codes)
        logger.debug(f"Response from '{contract.name}' with status code [{response.status_code}]")
        if response.status_code >= 400:
            logger.debug(f"Handling error code {response.status_code}")
            self._handle_errors(request, response)

        # Parse JSON manually - transport returns raw text
        try:
            data = json.loads(response.body or "{}")
        except json.JSONDecodeError as e:
            err = OlostepServerError_UnknownIssue(
                status_code=response.status_code, 
                server_response={"body": response.body, "headers": response.headers}
            ) 
            logger.error(f"Response from '{contract.name}' contains invalid JSON",exc_info=err)
            raise err
        
        logger.debug(f"Response from '{contract.name}' contains valid JSON. Evaluating against [{contract.response_model.__name__}] model.")
        try:
            return contract.response_model(**data) if contract.response_model else data
        except ValidationError as e:
            raise OlostepClientError_ResponseValidationFailed(request=request, response=response, errors=e.errors()) from e



    def validate_request(
        self,
        contract: EndpointContract,
        *,
        path_params: dict[str, Any] | None = {},
        query_params: dict[str, Any] | None = {},
        body_params: dict[str, Any] | None = {},
    ) -> Any:


        unvalidated_data = {
            "path_params": path_params,
            "query_params": query_params,
            "body_params": body_params,
        }
        
        request_model = contract.request_model
        if request_model:
            logger.debug(f"Validating request for '{contract.name}' against model [{request_model.__name__}]. Data:\n{pprint.pformat(unvalidated_data)}")
            try:
                request_data = request_model(path_params=path_params, query_params=query_params, body_params=body_params)
            except ValidationError as e:
                raise OlostepClientError_RequestValidationFailed(e.errors()) from e

            validated: dict[str, Any] = dict(request_data.model_dump(mode="json"))
            # Defensive extraction of the three top-level fields as dicts
            path: dict[str, Any] = dict(validated.get("path_params") or {})
            query: dict[str, Any] = dict(validated.get("query_params") or {})
            body: dict[str, Any] = dict(validated.get("body_params") or {})
            logger.debug(f"Request validation for '{contract.name}' completed. Validated data:\n{pprint.pformat(validated)}")
            return {
                "path_params": path,
                "query_params": query,
                "body_params": body,
            }
        else:
            logger.debug(f"No request model found for contract '{contract.name}'. Skipping validation.")
            return {
                "path_params": path_params or {},
                "query_params": query_params or {},
                "body_params": body_params or {},
            }

    def _compress_request(        
        self,
        contract: EndpointContract,  # noqa: F841, type: ignore  # intentionally unused, required for signature
        *,
        path_params: dict[str, Any] | None = {},
        query_params: dict[str, Any] | None = {},
        body_params: dict[str, Any] | None = {},
    ) -> Any:
        """
        Recursively compress request data by removing empty values.
        
        Removes:
        - None values
        - Empty strings
        - Empty lists
        - Empty dicts
        - Lists containing only None, empty strings, empty lists, or empty dicts
        - Dicts containing only empty values
        """
        def is_empty_value(value: Any) -> bool:
            """Check if a value is considered empty."""
            if value is None:
                return True
            if isinstance(value, str) and value == "":
                return True
            if isinstance(value, list):
                return len(value) == 0 or all(is_empty_value(item) for item in value)
            if isinstance(value, dict):
                return len(value) == 0 or all(is_empty_value(v) for v in value.values())
            return False
        
        def compress_dict(data: dict[str, Any]) -> dict[str, Any]:
            """Recursively compress a dictionary."""
            if not isinstance(data, dict):
                return data
            
            compressed = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    compressed_value = compress_dict(value)
                    if not is_empty_value(compressed_value):
                        compressed[key] = compressed_value
                elif isinstance(value, list):
                    compressed_list = []
                    for item in value:
                        if isinstance(item, dict):
                            compressed_item = compress_dict(item)
                            if not is_empty_value(compressed_item):
                                compressed_list.append(compressed_item)
                        elif not is_empty_value(item):
                            compressed_list.append(item)
                    if compressed_list:  # Only add non-empty lists
                        compressed[key] = compressed_list
                elif not is_empty_value(value):
                    compressed[key] = value
            
            return compressed
        
        return {
            "path_params": compress_dict(path_params or {}),
            "query_params": compress_dict(query_params or {}),
            "body_params": compress_dict(body_params or {}),
        }
    async def _invoke(
        self,
        contract: EndpointContract,
        *,
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute endpoint and return the parsed Pydantic response model instance.
        
        The return type is dynamically determined by the contract's response_model.
        If response_model is None, returns raw dict data.
        If response_model is set, returns an instance of that model.
        """

        request = self._prepare_request(contract, path_params, query_params, body_params)
        response = await self._transport.request(
            request
        )

        model = self._handle_response(request, response, contract)
        return model

    async def invoke(
        self,
        contract: EndpointContract,
        *,
        path_params: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: dict[str, Any] | None = None,
        max_retries: int | None = None,
        validate_request: bool = True
    ) -> Any:
        """
        Main method to execute endpoint with automatic retry for transient backend errors.
        If validate_request is True, validates the request parameters and compresses the request parameters.
        If validation is on (default), the caller is handeling more errors from the API.

        """

        # both paths remove empty values recursively
        if validate_request:
            request_pre_processor = self.validate_request
        else:
            request_pre_processor = self._compress_request  


        processed_params = request_pre_processor(
            contract,
            path_params=path_params,
            query_params=query_params,
            body_params=body_params,
        )
        max_retries = self._max_retries if max_retries is None else max_retries
        for attempt in range(max_retries):
            logger.info(f"Calling '{contract.name}' (attempt {attempt+1}/{max_retries}).")

            try:
                return await self._invoke(
                    contract,
                    path_params=processed_params["path_params"],
                    query_params=processed_params["query_params"],
                    body_params=processed_params["body_params"],
                )
            except OlostepServerError_TemporaryIssue:
                if attempt < self._max_retries:
                    await asyncio.sleep(5 ** attempt)
                    continue
                raise
            except OlostepServerError_NoResultInResponse:
                if validate_request and attempt < self._max_retries:
                    await asyncio.sleep(5 ** attempt)
                    continue
                raise
