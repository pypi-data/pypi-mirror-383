# Scrava Formatters - Quick Start

🎯 **Clean and convert scraped data with ease!**

---

## 🚀 Basic Usage

### Clean HTML and Text

```python
from scrava import clean_html, clean_text, DataCleaner

# Remove HTML tags
clean_html('<p>Hello <b>World</b></p>')  # "Hello World"

# Full cleaning
clean_text('<div>Check http://site.com</div>', 
           remove_html_tags=True, 
           remove_urls_flag=True)  # "Check"

# Reusable cleaner
cleaner = DataCleaner(remove_html=True, normalize=True)
cleaner.clean('<p>Café</p>')  # "Cafe"
```

### Convert File Formats

```python
from scrava import ExcelFormatter, CSVFormatter

# JSONL → Excel (with cleaning)
formatter = ExcelFormatter()
formatter.convert('scraped.jsonl', 'clean.xlsx', clean=True)

# CSV → JSONL
csv_fmt = CSVFormatter()
csv_fmt.convert('data.csv', 'data.jsonl')
```

---

## 💡 Common Tasks

### Task 1: Clean Scraped E-commerce Data

```python
from scrava import DataCleaner, ExcelFormatter

# Your scraped data (messy)
products = [
    {'title': '<h1>Laptop</h1>', 'price': '<span>$999</span>'},
    {'title': '<h1>Mouse</h1>', 'price': '<span>$29</span>'},
]

# Clean it
cleaner = DataCleaner(remove_html=True)
clean_products = cleaner.clean_list(products)

# Export to Excel
formatter = ExcelFormatter(auto_width=True)
formatter.to_excel(clean_products, 'products.xlsx', clean=False)
```

### Task 2: Format Single Output File

```python
from scrava import CSVFormatter

# Convert output.jsonl to clean CSV
formatter = CSVFormatter(clean_html=True, normalize=True)
formatter.convert('output.jsonl', 'data_clean.csv', clean=True)
```

### Task 3: Clean Specific Fields Only

```python
from scrava import DataCleaner

cleaner = DataCleaner(
    remove_html=True,
    fields_to_clean=['title', 'description']  # Only these
)

data = {
    'title': '<b>Product</b>',      # Will be cleaned
    'url': 'https://example.com'    # Won't be touched
}
cleaned = cleaner.clean_dict(data)
```

---

## 🔧 Standalone CLI Tool

```bash
# Convert formats
scrava-format convert data.jsonl data.csv --clean
scrava-format convert data.csv data.xlsx --normalize

# Clean files
scrava-format clean data.jsonl --html --urls --emoji
```

---

## 📦 What You Get

✅ **HTML Cleaning** - Remove tags, keep text  
✅ **Text Normalization** - Fix whitespace, Unicode  
✅ **URL Removal** - Clean URLs from text  
✅ **Format Conversion** - JSON ↔ CSV ↔ Excel  
✅ **Batch Processing** - Clean multiple files  
✅ **Pipeline Integration** - Use in your bots  

---

## 🎓 Full Documentation

See `FORMATTERS.md` for complete guide with all options and examples.

---

**Made with ❤️ by Scrava**

