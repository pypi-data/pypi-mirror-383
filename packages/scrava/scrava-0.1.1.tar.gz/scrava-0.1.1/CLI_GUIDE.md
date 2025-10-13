# Scrava CLI Guide

Complete reference for all Scrava CLI commands and options.

---

## 🚀 Interactive Shell Mode

**Just type `scrava` to enter interactive mode:**

```bash
scrava
```

This enters a MongoDB/Redis-style interactive shell where you can run commands without the `scrava` prefix:

```
scrava:myproject> help
scrava:myproject> run my_bot
scrava:myproject> list
scrava:myproject> version
scrava:myproject> exit
```

---

## 📋 Command Reference

### `scrava new` - Create New Project

Create a new Scrava project with skeleton bot template.

**Usage:**
```bash
scrava new [PROJECT_NAME]
```

**Interactive:**
- Prompts for project name if not provided
- Asks for bot name (creates custom bot file)
- Creates skeleton template for you to implement

**What it creates:**
- `bots/your_bot.py` - Skeleton bot with TODOs
- `config/settings.yaml` - Configuration
- `data/` - Output directory
- `README.md` - Project guide

**Example:**
```bash
scrava new my_scraper
# Then asks: Bot name? [my_bot]
# Creates: bots/my_bot.py with skeleton
```

---

### `scrava run` - Run a Bot

Run a bot with full control over execution parameters.

**Usage:**
```bash
scrava run BOT_NAME [OPTIONS]
```

**Options:**

| Option | Short | Type | Description | Example |
|--------|-------|------|-------------|---------|
| `--config` | `-c` | PATH | Custom config file | `-c prod.yaml` |
| `--output` | `-o` | TEXT | Output file path | `-o data/books.jsonl` |
| `--concurrency` | `-n` | INT | Concurrent requests | `-n 32` |
| `--delay` | `-d` | FLOAT | Download delay (seconds) | `-d 0.5` |
| `--browser` | `-b` | FLAG | Enable browser mode | `--browser` |
| `--no-cache` | | FLAG | Disable caching | `--no-cache` |
| `--debug` | | FLAG | Debug logging (verbose) | `--debug` |
| `--verbose` | `-v` | FLAG | INFO level logging | `-v` |
| `--quiet` | `-q` | FLAG | WARNING level only | `-q` |

**Logging Levels:**

| Flag | Level | What You See |
|------|-------|--------------|
| (default) | WARNING | **Silent** - No logs, only start/complete messages |
| `--verbose` / `-v` | INFO | Key events (requests, responses, records) |
| `--debug` | DEBUG | Everything (TCP connections, headers, cache hits, etc.) |
| `--quiet` / `-q` | WARNING | Only warnings and errors (same as default) |

**Examples:**

```bash
# Basic run
scrava run my_bot

# Debug mode - see all internal operations
scrava run my_bot --debug

# High performance - 50 concurrent requests, no delay
scrava run my_bot -n 50 -d 0

# Custom output location
scrava run my_bot -o data/output_$(date +%Y%m%d).jsonl

# Browser mode for JavaScript sites
scrava run my_bot --browser

# Disable cache for fresh data
scrava run my_bot --no-cache

# Production mode - quiet logs, custom config
scrava run my_bot -q -c config/production.yaml

# Full control
scrava run my_bot -n 32 -d 0.5 -o results.jsonl --debug
```

**What the output shows:**

```
Starting bot: my_bot
✓ Ready (concurrency=16, delay=0.0s, cache=ON, log=DEBUG)
2025-10-12 22:19:16 [info] Starting crawl ...
2025-10-12 22:19:16 [debug] Fetching request url=...
2025-10-12 22:19:18 [debug] Record scraped record_type=Book
...
✓ Complete (23.45s) - Output: output.jsonl
```

---

### `scrava list` - List Bots

List all bots in the current project.

**Usage:**
```bash
scrava list
```

**Output:**
```
🤖 Available Bots (3 found)
┌───┬───────────┬──────────────────────┬─────────────────────────┐
│ # │ Bot Name  │ File                 │ Command                 │
├───┼───────────┼──────────────────────┼─────────────────────────┤
│ 1 │ amazon    │ bots/amazon.py       │ scrava run amazon       │
│ 2 │ ebay      │ bots/ebay.py         │ scrava run ebay         │
│ 3 │ book_bot  │ bots/book_bot.py     │ scrava run book_bot     │
└───┴───────────┴──────────────────────┴─────────────────────────┘
```

---

### `scrava shell` - Interactive Selector Testing

Test CSS/XPath selectors against a live URL.

**Usage:**
```bash
scrava shell URL [--browser]
```

**Options:**
- `--browser` / `-b` - Use browser rendering

**Example:**
```bash
scrava shell https://books.toscrape.com

# In the shell:
>>> response.selector.css('h1::text').get()
'All products'

>>> response.selector.css('.product_pod').getall()
[... list of products ...]

>>> exit
```

**Useful for:**
- Testing selectors before implementing bot
- Debugging extraction issues
- Learning parsel selector syntax

---

### `scrava version` - System Information

Show version and platform info.

**Usage:**
```bash
scrava version
```

**Output:**
- Scrava version
- Python version
- Platform & architecture
- Installed dependencies
- Platform-specific advice

---

## 🎯 Common Workflows

### Development Workflow

```bash
# 1. Create project
scrava new my_project
cd my_project

# 2. Test selectors
scrava shell https://target-site.com

# 3. Edit bot (implement scraping logic)
# Edit bots/my_bot.py

# 4. Test run with debug
scrava run my_bot --debug -n 4

# 5. Production run
scrava run my_bot -n 32 -o data/prod_output.jsonl
```

### Quick Testing

```bash
# Fast iteration - single request, debug mode
scrava run my_bot --debug -n 1 --no-cache

# Check what gets scraped
head output.jsonl
```

### Production Deployment

```bash
# Quiet, high concurrency, custom output
scrava run my_bot -q -n 100 -d 0.1 -o /var/data/scrape_$(date +%Y%m%d_%H%M%S).jsonl
```

### Browser-Based Scraping

```bash
# For JavaScript-heavy sites
scrava run spa_bot --browser -n 3 -d 1.0

# Browser with debug (see browser operations)
scrava run spa_bot --browser --debug
```

---

## 🔧 Configuration Priority

Settings are applied in this order (later overrides earlier):

1. **Default settings** (in code)
2. **config/settings.yaml** (project config)
3. **Custom config file** (`--config`)
4. **Command-line flags** (highest priority)

**Example:**
```yaml
# config/settings.yaml
scrava:
  concurrent_reqs: 16
  download_delay: 0.5
```

```bash
# This overrides to 32 requests, 0 delay
scrava run my_bot -n 32 -d 0
```

---

## 📊 Understanding Log Levels

### DEBUG (`--debug`)
**Use when:** Developing, debugging issues
**Shows:**
- Every HTTP request/response
- TCP connections
- TLS handshakes
- Cache hits/misses
- Selector results
- Pipeline operations

```
[debug] Fetching request method=GET url=...
[debug] Request fetched size=51294 status=200
[debug] Record scraped record_type=Book
```

### INFO (default)
**Use when:** Normal operation
**Shows:**
- Crawl start/end
- Requests completed
- Records scraped
- Statistics

```
[info] Starting crawl bot=MyBot
[info] Response processed items_yielded=20
[info] Crawl statistics duration=23.5s records=1000
```

### WARNING (`--quiet`)
**Use when:** Production, logging to file
**Shows:**
- Only warnings and errors
- Request failures
- Data validation issues

```
[warning] Request failed url=... error=...
[error] Crawl failed error=...
```

---

## 💡 Pro Tips

### 1. Use Aliases for Common Commands

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# macOS Apple Silicon
alias scrava='arch -arm64 scrava'

# Quick debug run
alias scd='scrava run --debug -n 4'

# Production run with timestamp
alias scp='scrava run -q -o data/$(date +%Y%m%d_%H%M%S).jsonl'
```

### 2. Combine with Other Tools

```bash
# Watch output in real-time
scrava run my_bot & tail -f output.jsonl | jq .

# Count records as they're scraped
watch -n 1 'wc -l output.jsonl'

# Pretty print results
jq . output.jsonl | less
```

### 3. Progressive Testing

```bash
# Step 1: Test selectors
scrava shell https://site.com

# Step 2: Debug single page
scrava run my_bot --debug -n 1

# Step 3: Small batch
scrava run my_bot -n 4

# Step 4: Full run
scrava run my_bot -n 32
```

### 4. Performance Tuning

```bash
# Fast sites - high concurrency
scrava run my_bot -n 100 -d 0

# Slow/rate-limited sites - be gentle
scrava run my_bot -n 4 -d 2.0

# Browser mode - low concurrency (resource intensive)
scrava run my_bot --browser -n 3 -d 1.0
```

---

## 🆘 Troubleshooting

### Bot not found?
```bash
# Check you're in project directory
ls bots/

# List all bots
scrava list
```

### Too many logs?
```bash
# Use quiet mode
scrava run my_bot -q

# Or redirect to file
scrava run my_bot 2>scrape.log
```

### Want to see everything?
```bash
# Debug mode shows all internal operations
scrava run my_bot --debug
```

### Need different output location?
```bash
# Custom path
scrava run my_bot -o ~/Desktop/results.jsonl

# With timestamp
scrava run my_bot -o "data/scrape_$(date +%Y%m%d_%H%M%S).jsonl"
```

---

## 📚 Next Steps

- **API Reference:** See `docs/API.md` for programmatic usage
- **Examples:** Check `examples/` directory
- **Configuration:** Edit `config/settings.yaml` for project defaults

---

**Happy Scraping! 🕷️**

