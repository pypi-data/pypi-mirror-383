# Changelog

All notable changes to Scrava will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-10-12

### Changed
- 🔧 Updated all GitHub URLs to `nextractdevelopers/Scrava` organization
- 📝 Updated package metadata with Nextract Data Solutions branding
- 🔗 Added company website link to version command output
- 🛠️ Fixed build script to use `python3` instead of `python` for macOS compatibility

### Fixed
- Build script compatibility with macOS/Linux systems

## [0.1.0] - 2025-10-12

### Added
- 🎉 Initial release of Scrava framework
- Async-first web scraping architecture using `asyncio`
- Multi-modal fetching with HTTP (httpx) and browser automation (Playwright)
- Pluggable queue system (Memory, Redis with Bloom filters)
- Hook system for request/response interception
- Built-in caching with filesystem and Redis backends
- Pipeline system for data processing (JSON, MongoDB)
- Pydantic-based data models with automatic validation
- `parsel` integration for powerful CSS/XPath selectors
- Type-safe configuration system with YAML support
- Structured logging with `structlog`
- Beautiful CLI with `typer` and `rich`
- Interactive shell mode for REPL-like experience
- Data formatters for cleaning and format conversion
- HTML cleaning and text normalization utilities
- Format converters (JSON ↔ CSV ↔ Excel)
- Cross-platform support (macOS, Windows, Linux, ARM/Intel)
- Comprehensive documentation and examples

### Core Features
- **BaseBot**: User-friendly bot interface with `process()` method
- **Core Orchestrator**: Manages event loop, concurrency, and component coordination
- **Request/Response**: Clean data structures with built-in selector support
- **Pluggable Architecture**: Easy to extend with custom queues, fetchers, hooks, pipelines
- **Developer Experience**: Interactive project creation, hot reload, beautiful UI

### Data Processing
- **DataCleaner**: Remove HTML, URLs, emojis, normalize Unicode
- **CSVFormatter**: Read/write/convert CSV files
- **ExcelFormatter**: Read/write/convert Excel files with styling
- **JSONFormatter**: Handle JSON and JSONL formats

### CLI Tools
- `scrava new` - Interactive project creation
- `scrava run` - Execute bots with configurable options
- `scrava list` - List available bots
- `scrava shell` - Interactive selector testing
- `scrava version` - System information
- `scrava-format` - Standalone data formatting tool

### Documentation
- Complete API documentation
- Step-by-step quickstart guide
- Platform-specific installation guides
- Real-world examples
- Formatter documentation

## [Unreleased]

### Planned
- Distributed crawling support
- Advanced rate limiting
- Proxy rotation
- Session management
- More storage backends (PostgreSQL, Elasticsearch)
- GraphQL support
- API scraping utilities
- Monitoring and metrics
- Web UI for managing crawls

---

## Version History

- **0.1.0** (2025-10-12) - Initial release

---

For detailed changes, see [GitHub Releases](https://github.com/nextractdevelopers/Scrava/releases).

