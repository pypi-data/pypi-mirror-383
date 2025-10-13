"""scrava/bot.py"""
from typing import List, AsyncIterator, Union
from abc import ABC

from scrava.http.request import Request
from scrava.http.response import Response


class BaseBot(ABC):
    """
    Base class for all Scrava bots.
    
    A bot contains the scraping logic and defines how to extract data
    from web pages.
    
    Attributes:
        start_urls (List[str]): A list of URLs to begin crawling from.
        name (str): The name of this bot (auto-generated from class name).
    """
    
    start_urls: List[str] = []
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    async def start_requests(self) -> AsyncIterator[Request]:
        """
        Generate the initial requests for the crawl.
        
        By default, this creates GET requests for all URLs in start_urls.
        Override this method for custom initial request generation.
        
        Yields:
            Request objects
        """
        for url in self.start_urls:
            yield Request(url)
    
    async def process(self, response: Response) -> AsyncIterator[Union[Request, 'BaseModel']]:
        """
        The main data extraction method.
        
        This method is called with each Response and should yield:
        - Record objects (Pydantic models) containing scraped data
        - Request objects for following links/pagination
        
        Args:
            response: The Response object to process
            
        Yields:
            Request or Record objects
        """
        raise NotImplementedError("Bots must implement the process() method")
    
    async def setup(self):
        """
        Called before the bot starts processing.
        
        Override this for bot-specific initialization.
        """
        pass
    
    async def teardown(self):
        """
        Called after the bot finishes processing.
        
        Override this for bot-specific cleanup.
        """
        pass


