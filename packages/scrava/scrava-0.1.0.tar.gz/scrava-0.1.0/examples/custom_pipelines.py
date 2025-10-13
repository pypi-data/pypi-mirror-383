"""
Custom pipelines example

This example demonstrates:
- Creating custom pipelines
- CSV export pipeline
- SQLite database pipeline
- Data transformation pipeline
- Multi-pipeline setup
"""

import csv
import sqlite3
from pathlib import Path
from typing import Any
from pydantic import BaseModel

from scrava import BaseBot, Response
from scrava.pipelines.base import BasePipeline
from scrava.core.crawler import Crawler
from scrava.logging import get_logger

logger = get_logger(__name__)


# Custom Pipelines

class CsvPipeline(BasePipeline):
    """Export records to CSV file."""
    
    def __init__(self, output_file: str = "output.csv"):
        self.output_file = Path(output_file)
        self.file = None
        self.writer = None
        self.headers_written = False
    
    async def setup(self, bot):
        """Open CSV file for writing."""
        self.file = open(self.output_file, 'w', newline='', encoding='utf-8')
        logger.info("CSV pipeline ready", file=str(self.output_file))
    
    async def teardown(self, bot):
        """Close CSV file."""
        if self.file:
            self.file.close()
            logger.info("CSV file closed", file=str(self.output_file))
    
    async def process_rec(self, record: Any, bot):
        """Write record to CSV."""
        # Convert to dict
        if hasattr(record, 'model_dump'):
            data = record.model_dump()
        elif hasattr(record, 'dict'):
            data = record.dict()
        else:
            data = record
        
        # Write headers on first record
        if not self.headers_written:
            self.writer = csv.DictWriter(self.file, fieldnames=data.keys())
            self.writer.writeheader()
            self.headers_written = True
        
        # Write row
        self.writer.writerow(data)
        self.file.flush()
        
        return record


class SqlitePipeline(BasePipeline):
    """Store records in SQLite database."""
    
    def __init__(self, database: str = "scrava.db", table: str = None):
        self.database = database
        self.table = table
        self.conn = None
        self.cursor = None
    
    async def setup(self, bot):
        """Create database connection and table."""
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        
        # Use bot name as table if not specified
        if not self.table:
            self.table = bot.name.lower()
        
        logger.info(
            "SQLite pipeline ready",
            database=self.database,
            table=self.table
        )
    
    async def teardown(self, bot):
        """Close database connection."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            logger.info("SQLite connection closed")
    
    async def process_rec(self, record: Any, bot):
        """Insert record into database."""
        # Convert to dict
        if hasattr(record, 'model_dump'):
            data = record.model_dump()
        elif hasattr(record, 'dict'):
            data = record.dict()
        else:
            data = record
        
        # Create table if not exists (first record)
        columns = ', '.join([f"{k} TEXT" for k in data.keys()])
        create_sql = f"CREATE TABLE IF NOT EXISTS {self.table} ({columns})"
        self.cursor.execute(create_sql)
        
        # Insert record
        placeholders = ', '.join(['?' for _ in data])
        insert_sql = f"INSERT INTO {self.table} VALUES ({placeholders})"
        
        try:
            self.cursor.execute(insert_sql, list(data.values()))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error("SQLite insert failed", error=str(e), record=data)
        
        return record


class TransformPipeline(BasePipeline):
    """Transform records before storage."""
    
    async def process_rec(self, record: Any, bot):
        """Apply transformations to record."""
        if hasattr(record, 'price'):
            # Convert price to USD (example: multiply by 1.2)
            record.price = round(record.price * 1.2, 2)
        
        if hasattr(record, 'title'):
            # Uppercase title
            record.title = record.title.upper()
        
        logger.debug("Record transformed", record=record)
        return record


class FilterPipeline(BasePipeline):
    """Filter records based on conditions."""
    
    def __init__(self, min_price: float = 0, max_price: float = 1000):
        self.min_price = min_price
        self.max_price = max_price
    
    async def process_rec(self, record: Any, bot):
        """Filter records by price range."""
        if hasattr(record, 'price'):
            if record.price < self.min_price or record.price > self.max_price:
                logger.debug(
                    "Record filtered by price",
                    price=record.price,
                    min=self.min_price,
                    max=self.max_price
                )
                return None  # Filter out
        
        return record


class StatsPipeline(BasePipeline):
    """Collect statistics about scraped data."""
    
    def __init__(self):
        self.stats = {
            'total_records': 0,
            'total_price': 0,
            'min_price': float('inf'),
            'max_price': 0,
        }
    
    async def process_rec(self, record: Any, bot):
        """Update statistics."""
        self.stats['total_records'] += 1
        
        if hasattr(record, 'price'):
            price = record.price
            self.stats['total_price'] += price
            self.stats['min_price'] = min(self.stats['min_price'], price)
            self.stats['max_price'] = max(self.stats['max_price'], price)
        
        return record
    
    async def teardown(self, bot):
        """Log final statistics."""
        avg_price = (
            self.stats['total_price'] / self.stats['total_records']
            if self.stats['total_records'] > 0 else 0
        )
        
        logger.info(
            "Pipeline statistics",
            total_records=self.stats['total_records'],
            avg_price=round(avg_price, 2),
            min_price=self.stats['min_price'] if self.stats['min_price'] != float('inf') else 0,
            max_price=self.stats['max_price']
        )


class DuplicateFilterPipeline(BasePipeline):
    """Filter duplicate records based on a key."""
    
    def __init__(self, key: str = 'url'):
        self.key = key
        self.seen = set()
    
    async def process_rec(self, record: Any, bot):
        """Filter duplicates."""
        # Get the key value
        if hasattr(record, self.key):
            key_value = getattr(record, self.key)
        elif isinstance(record, dict) and self.key in record:
            key_value = record[self.key]
        else:
            return record  # Can't check, pass through
        
        if key_value in self.seen:
            logger.debug(f"Duplicate filtered", key=self.key, value=key_value)
            return None
        
        self.seen.add(key_value)
        return record


# Example Bot

class Book(BaseModel):
    """Book model."""
    title: str
    price: float
    url: str


class BookBot(BaseBot):
    """Simple bot for testing pipelines."""
    
    start_urls = ['https://books.toscrape.com/']
    
    async def process(self, response: Response):
        """Extract books."""
        for book in response.selector.css('article.product_pod')[:10]:  # Limit for demo
            title = book.css('h3 a::attr(title)').get()
            price_text = book.css('.price_color::text').get()
            price = float(price_text.replace('£', '')) if price_text else 0.0
            url = response.urljoin(book.css('h3 a::attr(href)').get())
            
            yield Book(title=title, price=price, url=url)


if __name__ == '__main__':
    # Create pipeline for statistics
    stats_pipeline = StatsPipeline()
    
    # Create crawler with multiple pipelines
    # Pipelines are executed in order
    crawler = Crawler(
        pipelines=[
            DuplicateFilterPipeline(key='url'),  # Remove duplicates first
            FilterPipeline(min_price=10, max_price=100),  # Filter by price
            TransformPipeline(),  # Transform data
            stats_pipeline,  # Collect stats
            CsvPipeline(output_file='books.csv'),  # Export to CSV
            SqlitePipeline(database='books.db'),  # Store in SQLite
        ],
        concurrent_reqs=5,
        download_delay=0.5
    )
    
    # Run the bot
    crawler.run(BookBot)



