# Scrava Formatters - Data Cleaning & Conversion Guide

Comprehensive utilities for cleaning scraped data and converting between formats.

---

## 🎯 Quick Start

### Clean HTML from scraped data

```python
from scrava import clean_html, clean_text

# Remove HTML tags
text = clean_html('<p>Hello <b>World</b></p>')  
# Result: "Hello World"

# Comprehensive cleaning
text = clean_text(
    '<p>  Check   http://example.com  </p>',
    remove_html=True,
    remove_urls=True
)
# Result: "Check"
```

### Convert between formats

```python
from scrava import ExcelFormatter, CSVFormatter

# Convert JSONL to Excel with cleaning
formatter = ExcelFormatter()
formatter.convert('scraped_data.jsonl', 'clean_data.xlsx', clean=True)

# Convert CSV to JSONL
csv_fmt = CSVFormatter()
csv_fmt.convert('data.csv', 'data.jsonl')
```

---

## 📦 Data Cleaning

### Using Individual Functions

```python
from scrava.formatters import (
    clean_html,
    clean_whitespace,
    remove_urls,
    normalize_unicode,
    remove_emojis
)

# Remove HTML
text = clean_html('<div><p>Hello</p></div>')  # "Hello"

# Clean whitespace
text = clean_whitespace('  too   much   space  ')  # "too much space"

# Remove URLs
text = remove_urls('Check https://example.com')  # "Check"

# Normalize Unicode
text = normalize_unicode('Café')  # "Cafe"

# Remove emojis
text = remove_emojis('Hello 😊 World 🌍')  # "Hello  World"
```

### Using DataCleaner Class

```python
from scrava import DataCleaner

# Create cleaner with options
cleaner = DataCleaner(
    remove_html=True,
    remove_urls=True,
    remove_emoji=True,
    normalize=True,
    lowercase=False
)

# Clean single text
text = cleaner.clean('<p>Hello <b>World</b> 😊 http://example.com</p>')
# Result: "Hello World"

# Clean dictionary
data = {
    'title': '<h1>Product Name</h1>',
    'description': '  Too much space  ',
    'price': '$99.99'
}
clean_data = cleaner.clean_dict(data)
# Result: {'title': 'Product Name', 'description': 'Too much space', 'price': '$99.99'}

# Clean list of dictionaries
records = [
    {'name': '<b>Item 1</b>', 'price': '  $10  '},
    {'name': '<b>Item 2</b>', 'price': '  $20  '}
]
clean_records = cleaner.clean_list(records)
```

### Clean Specific Fields Only

```python
cleaner = DataCleaner(
    remove_html=True,
    fields_to_clean=['title', 'description']  # Only clean these fields
)

data = {
    'title': '<b>Product</b>',
    'description': '<p>Details</p>',
    'url': 'https://example.com'  # Won't be cleaned
}
cleaned = cleaner.clean_dict(data)
```

---

## 📄 Format Conversion

### CSV Formatter

```python
from scrava import CSVFormatter

formatter = CSVFormatter(
    delimiter=',',
    clean_html=True,
    normalize=False
)

# Convert JSONL to CSV
formatter.convert('data.jsonl', 'data.csv', clean=True)

# Convert data to CSV
data = [
    {'name': '<b>John</b>', 'age': 30},
    {'name': '<b>Jane</b>', 'age': 25}
]
formatter.to_csv(data, 'output.csv', clean=True)

# Read CSV back
records = formatter.from_csv('output.csv', clean=True)
```

### Excel Formatter

```python
from scrava import ExcelFormatter

formatter = ExcelFormatter(
    sheet_name='Data',
    auto_width=True,        # Auto-adjust column widths
    freeze_header=True,     # Freeze first row
    clean_html=True,
    normalize=False
)

# Convert JSONL to Excel
formatter.convert('scraped.jsonl', 'clean.xlsx', clean=True)

# Convert data to Excel
data = [
    {'product': '<h1>Item</h1>', 'price': '$99', 'stock': 10},
    {'product': '<h1>Tool</h1>', 'price': '$49', 'stock': 5}
]
formatter.to_excel(data, 'products.xlsx', clean=True)

# Read Excel back
records = formatter.from_excel('products.xlsx', clean=True)

# Read specific sheet
records = formatter.from_excel('workbook.xlsx', sheet_name='Sheet2')
```

### JSON Formatter

```python
from scrava import JSONFormatter

# JSONL formatter (one record per line)
formatter = JSONFormatter(
    pretty=False,
    clean_html=True
)
formatter.to_jsonl(data, 'output.jsonl', clean=True)

# Pretty JSON formatter
formatter = JSONFormatter(
    pretty=True,
    indent=2
)
formatter.to_json(data, 'output.json', clean=True)

# Read JSONL
records = formatter.from_jsonl('data.jsonl', clean=True)

# Read JSON
records = formatter.from_json('data.json', clean=True)
```

---

## 🔧 Standalone CLI Tool

Use the formatter from command line:

```bash
# Convert formats
scrava-format convert data.jsonl data.csv --clean
scrava-format convert output.jsonl output.xlsx --normalize
scrava-format convert data.csv data.json --pretty

# Clean data in place
scrava-format clean data.jsonl --html --urls --emoji
scrava-format clean data.csv --normalize -o clean_data.csv

# Help
scrava-format --help
```

---

## 💡 Real-World Examples

### Example 1: Clean E-commerce Data

```python
from scrava import DataCleaner, ExcelFormatter

# Scraped messy e-commerce data
products = [
    {
        'title': '<h1>   Laptop Pro   </h1>',
        'price': '<span>$999.99</span>',
        'description': '<p>Best laptop<br>with features</p>',
        'url': 'https://shop.com/product/123'
    },
    # ... more products
]

# Clean the data
cleaner = DataCleaner(
    remove_html=True,
    remove_extra_whitespace=True,
    fields_to_clean=['title', 'price', 'description']  # Keep URL as-is
)
clean_products = cleaner.clean_list(products)

# Export to Excel
formatter = ExcelFormatter(auto_width=True, freeze_header=True)
formatter.to_excel(clean_products, 'products_clean.xlsx', clean=False)

print(f"✓ Cleaned and exported {len(clean_products)} products")
```

### Example 2: Process Scraping Results

```python
from pathlib import Path
from scrava import JSONFormatter, CSVFormatter, DataCleaner

# Read scraped JSONL file
json_fmt = JSONFormatter()
data = json_fmt.from_jsonl('output.jsonl')

print(f"Loaded {len(data)} records")

# Clean the data
cleaner = DataCleaner(
    remove_html=True,
    remove_urls=False,  # Keep URLs
    normalize=True,
    remove_emoji=True
)
clean_data = cleaner.clean_list(data)

# Export to multiple formats
csv_fmt = CSVFormatter()
csv_fmt.to_csv(clean_data, 'data_clean.csv', clean=False)

excel_fmt = ExcelFormatter(auto_width=True)
excel_fmt.to_excel(clean_data, 'data_clean.xlsx', clean=False)

print("✓ Exported to CSV and Excel")
```

### Example 3: Batch Convert and Clean Files

```python
from pathlib import Path
from scrava import CSVFormatter

formatter = CSVFormatter(clean_html=True, normalize=True)

# Process all JSONL files in directory
jsonl_files = Path('scraped_data').glob('*.jsonl')

for jsonl_file in jsonl_files:
    csv_file = jsonl_file.with_suffix('.csv')
    count = formatter.convert(jsonl_file, csv_file, clean=True)
    print(f"✓ {jsonl_file.name} → {csv_file.name} ({count} records)")
```

### Example 4: Use in Scrava Pipeline

```python
from pydantic import BaseModel
from scrava import BaseBot, Response, DataCleaner

class Product(BaseModel):
    name: str
    price: str
    description: str

class MyBot(BaseBot):
    start_urls = ['https://shop.com/products']
    
    def __init__(self):
        super().__init__()
        # Initialize cleaner
        self.cleaner = DataCleaner(
            remove_html=True,
            remove_extra_whitespace=True
        )
    
    async def process(self, response: Response):
        for item in response.selector.css('.product'):
            # Extract data (might contain HTML)
            data = {
                'name': item.css('.name::text').get(),
                'price': item.css('.price::text').get(),
                'description': item.css('.description').get()
            }
            
            # Clean before yielding
            clean_data = self.cleaner.clean_dict(data)
            
            yield Product(**clean_data)
```

---

## 🎨 Advanced Options

### Custom Delimiter for CSV

```python
formatter = CSVFormatter(delimiter=';')  # Use semicolon
formatter.to_csv(data, 'data.csv')
```

### Pretty Print JSON

```python
formatter = JSONFormatter(pretty=True, indent=4)
formatter.to_json(data, 'pretty.json')
```

### Excel with Custom Sheet Name

```python
formatter = ExcelFormatter(
    sheet_name='Products',
    auto_width=True,
    freeze_header=True
)
formatter.to_excel(data, 'report.xlsx')
```

### Clean Specific Fields

```python
cleaner = DataCleaner(
    remove_html=True,
    fields_to_clean=['title', 'content']  # Only these fields
)
```

---

## 📊 Supported Formats

| Format | Read | Write | Clean | Extension |
|--------|------|-------|-------|-----------|
| JSON | ✅ | ✅ | ✅ | `.json` |
| JSONL | ✅ | ✅ | ✅ | `.jsonl` |
| CSV | ✅ | ✅ | ✅ | `.csv` |
| Excel | ✅ | ✅ | ✅ | `.xlsx` |

---

## 🔧 Installation

Formatters are included with Scrava. For Excel support:

```bash
pip install openpyxl
```

---

## 💡 Tips

1. **Clean early**: Clean data as you scrape (in the bot) rather than after
2. **Be selective**: Use `fields_to_clean` to avoid cleaning URLs or codes
3. **Test first**: Try cleaning on a small sample before processing everything
4. **Chain operations**: Clean → Convert → Export
5. **Keep originals**: Always save cleaned data to a new file

---

## 🐛 Troubleshooting

**Excel not working?**
```bash
pip install openpyxl
```

**Unicode errors?**
```python
cleaner = DataCleaner(normalize=True)
```

**Too much cleaned?**
```python
# Be more selective
cleaner = DataCleaner(
    remove_html=True,
    remove_urls=False,  # Keep URLs
    fields_to_clean=['title', 'description']  # Only these
)
```

---

**Happy Formatting! 🎨**

