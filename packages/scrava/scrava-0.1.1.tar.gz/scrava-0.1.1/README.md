# Scrava

**Scrava** is a powerful, composable web scraping framework for Python that provides a unified API for building scalable web scrapers by orchestrating the best tools in the Python ecosystem.

> 🏢 **Built by [Nextract Data Solutions](https://nextract.dev)** - Your partner for enterprise web scraping and data extraction.

[![PyPI version](https://badge.fury.io/py/scrava.svg)](https://pypi.org/project/scrava/)
[![Python versions](https://img.shields.io/pypi/pyversions/scrava.svg)](https://pypi.org/project/scrava/)
[![License](https://img.shields.io/pypi/l/scrava.svg)](https://github.com/nextractdevelopers/Scrava/blob/main/LICENSE)

## 🎯 Philosophy

Scrava doesn't reinvent the wheel. Instead, it provides a **composition-over-invention** approach:

- **Unifying Force**: Eliminates boilerplate and integration complexity
- **Battle-Tested Libraries**: Built on httpx, Playwright, parsel, and more
- **Developer Experience**: Designed to be intuitive and "piece of cake" for newcomers
- **Production-Ready**: Structured logging, statistics, error handling, and more

## ✨ Features

- 🚀 **Async-First**: Built on asyncio for maximum performance
- 🔄 **Dual-Mode Fetching**: HTTP (httpx) and Browser (Playwright) support
- 📦 **Flexible Queuing**: In-memory or Redis-backed with duplicate filtering
- 🪝 **Powerful Hooks**: Intercept and modify requests, responses, and data flow
- 💾 **Pipeline System**: MongoDB, JSON, or custom data storage
- 🎯 **Pydantic Integration**: Type-safe data models with validation
- 📊 **Structured Logging**: Production-grade logging with structlog
- ⚙️ **Config Management**: YAML + Pydantic for type-safe configuration
- 🛠️ **CLI Tools**: Project scaffolding, bot runner, and interactive shell

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (latest version recommended)

### Platform-Specific Notes

**macOS (Apple Silicon - M1/M2/M3/M4):**
```bash
# Use native ARM64 Python for best performance
arch -arm64 pip install scrava
```

**macOS (Intel):**
```bash
pip install scrava
```

**Windows:**
```bash
pip install scrava
```

**Linux:**
```bash
pip install scrava
```

### Installation Options

```bash
# Basic installation (works on all platforms)
pip install scrava

# With browser support (Playwright)
pip install scrava[browser]

# With Redis queue support
pip install scrava[redis]

# With MongoDB pipeline support
pip install scrava[mongodb]

# Install everything
pip install scrava[all]
```

### Development Installation

```bash
# Clone and install in editable mode
git clone https://github.com/nextractdevelopers/Scrava.git
cd Scrava
pip install -e .

# With all optional dependencies
pip install -e ".[all]"
```

### Quick Installation Scripts

For easier installation, use our platform-specific scripts:

**macOS/Linux:**
```bash
# Auto-detects architecture and installs correctly
curl -sSL https://raw.githubusercontent.com/nextractdevelopers/Scrava/main/install.sh | bash

# Or download and run manually
chmod +x install.sh
./install.sh
```

**Windows (PowerShell):**
```powershell
# Download and run the installation script
iwr -useb https://raw.githubusercontent.com/nextractdevelopers/Scrava/main/install.ps1 | iex

# Or download and run manually
.\install.ps1
```

### Verify Installation

```bash
# Check if Scrava is properly installed
scrava version

# Run the welcome screen
scrava
```

### Troubleshooting

If you encounter installation issues, see [PLATFORM.md](PLATFORM.md) for detailed platform-specific instructions.

## 🚀 Quick Start

### 1. Create a New Project

```bash
scrava new my_project
cd my_project
```

### 2. Define Your Bot

```python
# bots/book_bot.py
from pydantic import BaseModel, HttpUrl
from scrava import BaseBot, Request, Response


class Book(BaseModel):
    """A scraped book record."""
    title: str
    price: float
    url: HttpUrl
    in_stock: bool = True


class BookBot(BaseBot):
    """Bot for scraping books.toscrape.com"""
    
    start_urls = ['https://books.toscrape.com']
    
    async def process(self, response: Response):
        """Extract book data from the page."""
        # Extract books using parsel selectors
        for book in response.selector.css('article.product_pod'):
            title = book.css('h3 a::attr(title)').get()
            price_text = book.css('.price_color::text').get()
            price = float(price_text.replace('£', ''))
            url = response.urljoin(book.css('h3 a::attr(href)').get())
            
            yield Book(
                title=title,
                price=price,
                url=url
            )
        
        # Follow pagination
        next_page = response.selector.css('.next a::attr(href)').get()
        if next_page:
            yield Request(response.urljoin(next_page))
```

### 3. Run Your Bot

```bash
scrava run book_bot
```

## 🏗️ Core Components

### Request & Response

```python
from scrava import Request, Response

# Create a request
request = Request(
    url='https://example.com',
    method='GET',
    headers={'User-Agent': 'MyBot/1.0'},
    priority=10,  # Higher priority = processed first
    meta={'browser': True}  # Use browser rendering
)

# Response provides powerful selectors
async def process(self, response: Response):
    # CSS selectors
    title = response.selector.css('h1::text').get()
    
    # XPath selectors
    links = response.selector.xpath('//a/@href').getall()
    
    # Join relative URLs
    absolute_url = response.urljoin('/path')
```

### Bot Lifecycle

```python
from scrava import BaseBot, Response

class MyBot(BaseBot):
    start_urls = ['https://example.com']
    
    async def setup(self):
        """Called before crawling starts."""
        self.session_data = {}
    
    async def process(self, response: Response):
        """Main processing method."""
        yield Record(...)
        yield Request(...)
    
    async def teardown(self):
        """Called after crawling completes."""
        pass
```

### Queue System

```python
from scrava import Crawler
from scrava.queue import MemoryQueue, RedisQueue

# In-memory queue (default)
crawler = Crawler(queue=MemoryQueue())

# Redis-backed queue for distributed crawls
crawler = Crawler(queue=RedisQueue(redis_url="redis://localhost:6379/0"))
```

### Fetchers

```python
# HTTP fetcher (default)
from scrava.fetchers import HttpxFetcher

crawler = Crawler(
    fetcher=HttpxFetcher(
        timeout=30.0,
        follow_redirects=True,
        verify_ssl=True
    )
)

# Browser fetcher for JavaScript-heavy sites
from scrava.fetchers import PlaywrightFetcher

crawler = Crawler(
    browser_fetcher=PlaywrightFetcher(
        headless=True,
        browser_type='chromium',
        context_pool_size=5
    ),
    enable_browser=True
)

# Use browser for specific requests
yield Request(url, meta={'browser': True})
```

### Hooks

#### Request Hooks

```python
from scrava.hooks import RequestHook

class UserAgentHook(RequestHook):
    async def process_req(self, request, bot):
        # Modify request before fetching
        request.headers['User-Agent'] = 'MyBot/1.0'
        return None
    
    async def process_res(self, request, response, bot):
        # Process response after fetching
        print(f"Got {response.status} from {response.url}")
        return None

crawler = Crawler(request_hooks=[UserAgentHook()])
```

#### Built-in Cache Hook

```python
from scrava.hooks import CacheHook

# Enable caching
crawler = Crawler(
    request_hooks=[
        CacheHook(expiration=86400)  # Cache for 1 day
    ]
)

# Disable caching for specific requests
yield Request(url, meta={'cache': False})
```

### Pipelines

```python
from scrava.pipelines import JsonPipeline, MongoPipeline

# JSON output
crawler = Crawler(
    pipelines=[JsonPipeline(output_file='output.jsonl')]
)

# MongoDB with batching
crawler = Crawler(
    pipelines=[
        MongoPipeline(
            uri='mongodb://localhost:27017',
            database='scrava',
            batch_size=100,
            batch_timeout=5.0
        )
    ]
)

# Custom pipeline
from scrava.pipelines import BasePipeline

class CustomPipeline(BasePipeline):
    async def process_rec(self, record, bot):
        # Process and store record
        await self.save_to_db(record)
        return record
```

### Configuration

```yaml
# config/settings.yaml
project_name: "my_project"

scrava:
  concurrent_reqs: 16
  download_delay: 0.0
  enable_browser: false

cache:
  enabled: true
  path: ".scrava_cache"
  expiration_secs: 86400

queue:
  backend: "scrava.queue.memory.MemoryQueue"
  redis_url: "redis://localhost:6379/0"

pipeline:
  enabled:
    - scrava.pipelines.json.JsonPipeline
  mongodb_uri: "mongodb://localhost:27017"
  mongodb_database: "scrava"

logging:
  level: "INFO"
  format: "console"  # or "json" for production
  use_colors: true
```

```python
from scrava.config import load_settings

settings = load_settings('config/settings.yaml')
```

### Logging

```python
from scrava.logging import setup_logging, get_logger

# Setup logging
setup_logging(
    level="INFO",
    format="console",  # "json" for production
    use_colors=True
)

# Get logger
logger = get_logger(__name__)

logger.info("Bot started", bot_name="my_bot", url="https://example.com")
# Output: 2024-10-27 10:30:05 [info] Bot started bot_name=my_bot url=https://example.com
```

## 🔧 CLI Commands

```bash
# Create a new project
scrava new <project_name>

# Run a bot
scrava run <bot_name>

# List all bots
scrava list

# Interactive selector shell
scrava shell <url>
scrava shell <url> --browser  # Use browser rendering

# Show version
scrava version
```

## 📚 Advanced Examples

### Custom Callback Methods

```python
class ProductBot(BaseBot):
    start_urls = ['https://shop.example.com']
    
    async def process(self, response: Response):
        # Extract category links
        for category in response.selector.css('.category'):
            url = response.urljoin(category.css('a::attr(href)').get())
            yield Request(url, callback=self.parse_category)
    
    async def parse_category(self, response: Response):
        # Extract products
        for product in response.selector.css('.product'):
            yield Request(
                response.urljoin(product.css('a::attr(href)').get()),
                callback=self.parse_product
            )
    
    async def parse_product(self, response: Response):
        yield Product(
            name=response.selector.css('h1::text').get(),
            price=float(response.selector.css('.price::text').get())
        )
```

### Browser Automation

```python
async def process(self, response: Response):
    # Scroll page, click buttons, etc. with JavaScript
    yield Request(
        url='https://spa-site.com',
        meta={
            'browser': True,
            'wait_for': '.dynamic-content',
            'scroll': True
        }
    )
```

### Error Handling Hook

```python
class RetryHook(RequestHook):
    async def process_exc(self, request, exception, bot):
        if request.meta.get('retry_count', 0) < 3:
            # Retry with incremented counter
            request.meta['retry_count'] = request.meta.get('retry_count', 0) + 1
            await bot.queue.push(request)
        return None
```

### Data Validation Pipeline

```python
class ValidationPipeline(BasePipeline):
    async def process_rec(self, record, bot):
        # Pydantic automatically validates
        if record.price < 0:
            logger.warning("Invalid price", record=record)
            return None  # Filter out
        return record
```

## 🎯 Best Practices

1. **Use Pydantic Models**: Define clear schemas for your scraped data
2. **Leverage Hooks**: Keep bot logic clean by using hooks for cross-cutting concerns
3. **Configure Delays**: Be respectful with `download_delay` to avoid overwhelming servers
4. **Enable Caching**: Speed up development with the built-in CacheHook
5. **Structure Logs**: Use structured logging for easy debugging and monitoring
6. **Handle Errors**: Implement retry logic and error hooks for robust crawls
7. **Test Selectors**: Use `scrava shell <url>` to test CSS/XPath selectors interactively

## 🔗 Architecture

```
┌─────────────┐
│    Bot      │  ← Your scraping logic
└──────┬──────┘
       │
       ↓
┌─────────────┐
│    Core     │  ← Orchestrator (asyncio event loop)
└──────┬──────┘
       │
       ├→ Queue      (MemoryQueue / RedisQueue)
       ├→ Fetcher    (HttpxFetcher / PlaywrightFetcher)
       ├→ Hooks      (RequestHook / BotHook)
       └→ Pipelines  (MongoPipeline / JsonPipeline)
```

## 📖 Documentation

For full documentation, visit: [https://scrava.readthedocs.io](https://scrava.readthedocs.io)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Scrava is built on the shoulders of giants:
- [httpx](https://www.python-httpx.org/) - HTTP client
- [Playwright](https://playwright.dev/python/) - Browser automation
- [parsel](https://parsel.readthedocs.io/) - Data extraction
- [Pydantic](https://pydantic.dev/) - Data validation
- [structlog](https://www.structlog.org/) - Structured logging
- [Typer](https://typer.tiangolo.com/) - CLI framework

---

## 🏢 About Nextract Data Solutions

Scrava is developed and maintained by [**Nextract Data Solutions**](https://nextract.dev), a leading provider of enterprise web scraping and data extraction services.

**Need enterprise-grade data extraction?**

While Scrava is perfect for developers building their own scrapers, Nextract Data Solutions offers done-for-you web scraping and data pipelines for businesses that need:

- ✅ Custom enterprise scraping solutions
- ✅ Data-as-a-Service (DaaS) subscriptions
- ✅ Data enrichment and validation
- ✅ 99.9% accuracy and reliability
- ✅ Dedicated support and SLA guarantees

### 📞 Contact Nextract

- **Website**: [https://nextract.dev](https://nextract.dev)
- **Email**: [hello@nextract.dev](mailto:hello@nextract.dev)
- **Phone**: +91 85110-98799
- **GitHub**: [@nextractdevelopers](https://github.com/nextractdevelopers)

[**Schedule a Free Strategy Call**](https://nextract.dev) | [**Download Capabilities Deck**](https://nextract.dev)

---

**Happy Scraping! 🕷️**


