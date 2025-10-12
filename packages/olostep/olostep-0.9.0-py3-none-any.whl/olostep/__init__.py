# Core clients
from .clients.async_client import OlostepClient
from .clients.sync_client import SyncOlostepClient

# Stateful result objects
from .frontend.client_state import ScrapeResult, BatchItem, CrawlPage, Crawl, CrawlInfo, Sitemap

# Type system
from .models.request import (
    Format,
    Country,
    RetrieveFormat,
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

# Error hierarchy
from . import errors

__version__ = "0.9.0"

# Get all error classes dynamically
_error_classes = [name for name in dir(errors) if not name.startswith('_') and name.endswith('Error')]

__all__ = [
    # Clients
    "OlostepClient",
    "SyncOlostepClient",
    # Result objects
    "ScrapeResult", 
    "BatchItem", 
    "CrawlPage", 
    "Crawl", 
    "CrawlInfo", 
    "Sitemap",
    # Types
    "Format",
    "Country", 
    "RetrieveFormat",
    "WaitAction",
    "ClickAction", 
    "FillInputAction",
    "ScrollAction",
    "Parser",
    "LLMExtract",
    "LinksOnPage", 
    "ScreenSize",
    "Transformer",
    # Error classes
    *_error_classes,
    # Version
    "__version__",
]