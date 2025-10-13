"""
Custom hooks example

This example demonstrates:
- Creating custom request hooks
- Creating custom bot hooks
- Retry logic
- Request/response logging
- Data filtering and transformation
"""

from scrava import BaseBot, Request, Response
from scrava.hooks.request import RequestHook
from scrava.hooks.bot import BotHook
from scrava.core.crawler import Crawler
from scrava.pipelines.json import JsonPipeline
from scrava.logging import get_logger
from pydantic import BaseModel
import random

logger = get_logger(__name__)


# Custom Request Hooks

class RetryHook(RequestHook):
    """Automatically retry failed requests."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    async def process_exc(self, request, exception, bot):
        """Retry on exceptions."""
        retry_count = request.meta.get('retry_count', 0)
        
        if retry_count < self.max_retries:
            request.meta['retry_count'] = retry_count + 1
            logger.warning(
                "Retrying request",
                url=request.url,
                retry_count=retry_count + 1,
                max_retries=self.max_retries,
                error=str(exception)
            )
            # Push back to queue for retry
            await bot.core.queue.push(request)
            return None  # Don't re-raise
        
        logger.error(
            "Max retries exceeded",
            url=request.url,
            retries=retry_count,
            error=str(exception)
        )
        return None


class UserAgentRotationHook(RequestHook):
    """Rotate user agents for each request."""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
    
    async def process_req(self, request, bot):
        """Set random user agent."""
        request.headers['User-Agent'] = random.choice(self.user_agents)
        logger.debug("User agent set", url=request.url, ua=request.headers['User-Agent'])
        return None


class RequestLoggingHook(RequestHook):
    """Log all requests and responses."""
    
    async def process_req(self, request, bot):
        """Log outgoing request."""
        logger.info(
            "Outgoing request",
            method=request.method,
            url=request.url,
            priority=request.priority
        )
        return None
    
    async def process_res(self, request, response, bot):
        """Log incoming response."""
        logger.info(
            "Incoming response",
            url=response.url,
            status=response.status,
            size=len(response.body)
        )
        return None


class StatusCodeFilterHook(RequestHook):
    """Filter responses by status code."""
    
    def __init__(self, allowed_codes: list = None):
        self.allowed_codes = allowed_codes or [200]
    
    async def process_res(self, request, response, bot):
        """Filter non-200 responses."""
        if response.status not in self.allowed_codes:
            logger.warning(
                "Response filtered by status code",
                url=response.url,
                status=response.status,
                allowed=self.allowed_codes
            )
            # Return a dummy response to short-circuit processing
            # Or raise an exception to trigger retry
            raise Exception(f"Status code {response.status} not allowed")
        
        return None


# Custom Bot Hooks

class DataValidationHook(BotHook):
    """Validate scraped data before pipeline."""
    
    async def process_output(self, response, result, bot):
        """Validate output data."""
        # Only validate records (not requests)
        if isinstance(result, Request):
            return result
        
        # Check if it's a Pydantic model
        if hasattr(result, 'model_dump'):
            # Pydantic already validated, but we can add custom checks
            data = result.model_dump()
            
            # Example: Filter out items with price 0
            if data.get('price', 0) <= 0:
                logger.warning(
                    "Invalid record filtered",
                    reason="price <= 0",
                    record=data
                )
                return None  # Filter out
        
        return result


class DeduplicationHook(BotHook):
    """Deduplicate scraped records."""
    
    def __init__(self):
        self.seen_ids = set()
    
    async def process_output(self, response, result, bot):
        """Deduplicate based on URL or ID."""
        if isinstance(result, Request):
            return result
        
        # Generate ID from record
        if hasattr(result, 'url'):
            record_id = str(result.url)
        elif hasattr(result, 'id'):
            record_id = str(result.id)
        else:
            return result  # Can't deduplicate
        
        if record_id in self.seen_ids:
            logger.debug("Duplicate record filtered", record_id=record_id)
            return None  # Filter duplicate
        
        self.seen_ids.add(record_id)
        return result


class DataEnrichmentHook(BotHook):
    """Enrich scraped data with additional fields."""
    
    async def process_output(self, response, result, bot):
        """Add metadata to records."""
        if isinstance(result, Request):
            return result
        
        # Add scrape metadata if it's a dict or has attributes
        if hasattr(result, '__dict__'):
            result.scraped_from = str(response.url)
            result.scraped_at = __import__('datetime').datetime.now().isoformat()
            result.bot_name = bot.name
        
        return result


# Example Bot using custom hooks

class Book(BaseModel):
    """Book model."""
    title: str
    price: float
    url: str


class BookBot(BaseBot):
    """Simple bot for testing hooks."""
    
    start_urls = ['https://books.toscrape.com/']
    
    async def process(self, response: Response):
        """Extract books."""
        for book in response.selector.css('article.product_pod')[:5]:  # Limit for demo
            title = book.css('h3 a::attr(title)').get()
            price_text = book.css('.price_color::text').get()
            price = float(price_text.replace('£', '')) if price_text else 0.0
            url = response.urljoin(book.css('h3 a::attr(href)').get())
            
            yield Book(title=title, price=price, url=url)


if __name__ == '__main__':
    # Create crawler with all custom hooks
    crawler = Crawler(
        request_hooks=[
            UserAgentRotationHook(),
            RetryHook(max_retries=3),
            RequestLoggingHook(),
            StatusCodeFilterHook(allowed_codes=[200, 201]),
        ],
        bot_hooks=[
            DataValidationHook(),
            DeduplicationHook(),
            DataEnrichmentHook(),
        ],
        pipelines=[JsonPipeline(output_file='books_with_hooks.jsonl')],
        concurrent_reqs=5,
        download_delay=0.5
    )
    
    # Run the bot
    crawler.run(BookBot)



