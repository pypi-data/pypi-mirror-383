"""
Scraping operations with rich IDE support and smart input coercion.
"""

from __future__ import annotations

from typing import Any

from pydantic import HttpUrl
from .._log import get_logger

from ..backend.caller import EndpointCaller
from ..backend.api_endpoints import SCRAPE_URL, SCRAPE_GET
from ..frontend.client_state import ScrapeResult
from ..models.request import (
    Format,
    Country,
    WaitAction,
    ClickAction,
    FillInputAction,
    ScrollAction,
    Parser,
    LLMExtract,
    LinksOnPage,
    ScreenSize,
    Transformer,
)
from ..models.response import CreateScrapeResponse, GetScrapeResponse
from ..frontend.input_coersion import coerce_to_list, coerce_to_key_in_dict, coerce_to_string

logger = get_logger("frontend.scrape_menu")



class ScrapeMenu:
    """Scraping operations with rich IDE support and smart input coercion.
    
    This class provides methods for scraping individual URLs with various
    configuration options. It supports smart input coercion, validation,
    and provides rich type hints for better IDE support.
    """
    
    def __init__(self, caller: EndpointCaller, validate_request: bool = True) -> None:
        self._caller = caller
        self._validate_request = validate_request

    async def create(
        self,
        url: HttpUrl | str,
        *,
        formats: list[Format] | list[str] | Format | str | None = None,
        country: Country | str | None = None,
        wait_before_scraping: int | None = None,
        remove_css_selectors: list[str] | str | None = None,
        actions: list[WaitAction | ClickAction | FillInputAction | ScrollAction] | list[dict[str, Any]] | dict[str, Any] | None = None,
        transformer: Transformer | str | None = None,
        remove_images: bool | None = None,
        remove_class_names: list[str] | None = None,
        parser: Parser | str | None = None,
        llm_extract: LLMExtract | dict[str, Any] | None = None,
        links_on_page: LinksOnPage | dict[str, Any] | None = None,
        screen_size: ScreenSize | dict[str, int] | str | None = None,
        metadata: dict[str, Any] | None = None,
        validate_request: bool | None = None,
    ) -> ScrapeResult:
        """Scrape a URL with rich type hints and smart input coercion.
        
        Creates a new scraping job for the specified URL with various configuration
        options. Supports smart input coercion and provides rich type hints for
        better IDE support.
        
        Args:
            url: URL to scrape (supports bare domains like "example.com").
            formats: Output formats - single format or list of formats.
                Can be Format enum values, strings, or mixed lists.
            country: Country for geolocation when scraping.
                Can be a Country enum or string representation.
            wait_before_scraping: Wait time in milliseconds before scraping starts.
                Useful for pages that need time to load dynamic content.
            remove_css_selectors: CSS selectors to remove from the page.
                Can be a string, list of strings, or configuration object.
            actions: List of browser actions to perform before scraping.
                Can be action objects, dictionaries, or mixed lists.
            transformer: Custom transformer to apply to the scraped content.
                Can be a Transformer object or string identifier.
            remove_images: Whether to remove images from the scraped content.
            remove_class_names: List of CSS class names to remove from the page.
            parser: Parser configuration for content extraction.
                Can be a Parser object, dictionary, or parser ID string.
            llm_extract: LLM extraction configuration for structured data extraction.
                Can be an LLMExtract object or dictionary with extraction settings.
            links_on_page: Configuration for extracting links from the page.
                Can be a LinksOnPage object or dictionary with link extraction settings.
            screen_size: Browser viewport configuration for rendering.
                Can be a ScreenSize object, dictionary, or string identifier.
            metadata: Custom metadata to associate with the scrape (not yet supported by API).
            validate_request: Override the global validation setting for this request.
                If None, uses the instance's default validation setting.
                
        Returns:
            ScrapeResult: The scraped content in the requested formats.
            
        Raises:
            Exception: If the API request fails.
            
        Examples:
            # Basic scraping
            result = await client.scrape("example.com")
            
            # With formats
            result = await client.scrape("example.com", formats=Format.HTML)
            result = await client.scrape("example.com", formats=[Format.HTML, Format.MARKDOWN])
            
            # With country
            result = await client.scrape("example.com", country=Country.US)
            
            # With parser
            result = await client.scrape("example.com", parser="@olostep/google-news")
        """

        body_params = {
            "url_to_scrape": url,
            "formats": coerce_to_list(formats),
            "country": country,
            "wait_before_scraping": wait_before_scraping,
            "remove_css_selectors": coerce_to_string(remove_css_selectors),
            "actions": coerce_to_list(actions),
            "transformer": transformer,
            "remove_images": remove_images,
            "remove_class_names": remove_class_names,
            "parser": coerce_to_key_in_dict(parser, "id"),
            "llm_extract": llm_extract,
            "links_on_page": links_on_page,
            "screen_size": coerce_to_key_in_dict(screen_size, "screen_type"),
            "metadata": metadata,
        }


        # local validation setting overrides global validation setting
        validate_request = self._validate_request if validate_request is None else validate_request
        
        res: CreateScrapeResponse = await self._caller.invoke(
            SCRAPE_URL, 
            body_params=body_params,
            validate_request=validate_request
        )
        
        return ScrapeResult(res)
    
    __call__ = create # shorthand for create

    async def get(self, scrape_id: str) -> ScrapeResult:
        """Get an existing scrape result by ID.
        
        Retrieves a previously created scrape result using its unique identifier.
        Useful for accessing scrape results that were created earlier or
        by other processes.
        
        Args:
            scrape_id: The unique identifier of the scrape to retrieve.
                This is returned when creating a scrape with the create() method.
                
        Returns:
            ScrapeResult: The scraped content and metadata.
            
        Raises:
            Exception: If the API request fails.
            
        Examples:
            # Get existing scrape result
            result = await client.scrape.get("scrape_123")
            print(f"URL: {result.url_to_scrape}")
            print(f"HTML length: {len(result.html_content)}")
        """
        path_params = {"scrape_id": scrape_id}
        res: GetScrapeResponse = await self._caller.invoke(
            SCRAPE_GET, 
            path_params=path_params,
            validate_request=self._validate_request
        )
        return ScrapeResult(res)

