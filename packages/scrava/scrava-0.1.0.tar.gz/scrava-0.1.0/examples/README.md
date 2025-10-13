# Scrava Examples

This directory contains comprehensive examples demonstrating various features of the Scrava framework.

## Examples Overview

### 1. `basic_bot.py` - Getting Started

The simplest example showing:
- Basic bot structure
- Pydantic models for data validation
- CSS selectors
- Pagination handling
- JSON output

**Run it:**
```bash
python examples/basic_bot.py
```

### 2. `advanced_bot.py` - Multiple Callbacks & Hierarchy

Advanced scraping patterns:
- Multiple callback methods
- Request priorities
- Category hierarchy navigation
- Metadata passing between requests
- Browser rendering (JavaScript support)
- Caching

**Run it:**
```bash
python examples/advanced_bot.py
```

### 3. `custom_hooks.py` - Extending with Hooks

Demonstrates the hook system:
- **Request Hooks:**
  - RetryHook - automatic retries
  - UserAgentRotationHook - rotate user agents
  - RequestLoggingHook - log all requests
  - StatusCodeFilterHook - filter by status code

- **Bot Hooks:**
  - DataValidationHook - validate scraped data
  - DeduplicationHook - remove duplicates
  - DataEnrichmentHook - add metadata

**Run it:**
```bash
python examples/custom_hooks.py
```

### 4. `custom_pipelines.py` - Data Processing

Custom pipeline implementations:
- **CsvPipeline** - Export to CSV
- **SqlitePipeline** - Store in SQLite database
- **TransformPipeline** - Data transformation
- **FilterPipeline** - Conditional filtering
- **StatsPipeline** - Collect statistics
- **DuplicateFilterPipeline** - Remove duplicates

Shows how to:
- Create custom pipelines
- Chain multiple pipelines
- Transform and filter data
- Export to various formats

**Run it:**
```bash
python examples/custom_pipelines.py
```

## Common Patterns

### Pattern 1: Simple Scraping

```python
from scrava import BaseBot, Response
from scrava.core.crawler import Crawler
from scrava.pipelines.json import JsonPipeline

class MyBot(BaseBot):
    start_urls = ['https://example.com']
    
    async def process(self, response: Response):
        # Extract data
        for item in response.selector.css('.item'):
            yield MyRecord(...)

crawler = Crawler(pipelines=[JsonPipeline()])
crawler.run(MyBot)
```

### Pattern 2: Multi-Level Navigation

```python
class MyBot(BaseBot):
    async def process(self, response: Response):
        # Extract category links
        for category in response.selector.css('.category'):
            yield Request(url, callback=self.parse_category)
    
    async def parse_category(self, response: Response):
        # Extract item links
        for item in response.selector.css('.item'):
            yield Request(url, callback=self.parse_item)
    
    async def parse_item(self, response: Response):
        yield Item(...)
```

### Pattern 3: Browser Automation

```python
async def process(self, response: Response):
    # Use browser for JavaScript-heavy pages
    yield Request(
        url='https://spa-site.com',
        meta={'browser': True}
    )
```

### Pattern 4: Custom Hooks

```python
from scrava.hooks.request import RequestHook

class MyHook(RequestHook):
    async def process_req(self, request, bot):
        # Modify request before fetching
        request.headers['Custom'] = 'Value'
        return None

crawler = Crawler(request_hooks=[MyHook()])
```

### Pattern 5: Custom Pipelines

```python
from scrava.pipelines.base import BasePipeline

class MyPipeline(BasePipeline):
    async def process_rec(self, record, bot):
        # Process record
        await self.save(record)
        return record

crawler = Crawler(pipelines=[MyPipeline()])
```

## Tips & Best Practices

1. **Use Pydantic Models**: Define clear schemas with validation
2. **Enable Caching**: Speed up development with CacheHook
3. **Add Delays**: Be respectful with `download_delay`
4. **Handle Errors**: Use RetryHook for robustness
5. **Log Everything**: Use structured logging for debugging
6. **Test Selectors**: Use `scrava shell <url>` before running
7. **Chain Pipelines**: Combine multiple pipelines for data flow
8. **Use Priorities**: Control request order with priority
9. **Pass Metadata**: Use `request.meta` to pass context
10. **Monitor Stats**: Check logs for performance metrics

## Output Files

After running examples, you'll see:
- `books.jsonl` - JSON Lines output
- `products.jsonl` - Product data
- `books_with_hooks.jsonl` - Data with hooks applied
- `books.csv` - CSV export
- `books.db` - SQLite database
- `.scrava_cache/` - Cached responses (if enabled)

## Need Help?

- Check the main [README.md](../README.md)
- Read the [API documentation](../docs/API.md)
- Review the source code in `scrava/`
- Open an issue on GitHub

Happy scraping! 🕷️



