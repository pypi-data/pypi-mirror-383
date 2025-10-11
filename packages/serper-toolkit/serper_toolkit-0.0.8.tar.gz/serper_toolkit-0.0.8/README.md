# Serper MCP Toolkit

A high-performance, asynchronous MCP server that provides comprehensive Google search and web content scraping capabilities through the Serper API (excluding some rarely used interfaces).

This project is built on `httpx`, utilizing asynchronous clients and connection pool management to offer LLMs a stable and efficient external information retrieval tool.

## Key Features

- **Asynchronous Architecture**: Fully based on `asyncio` and `httpx`, ensuring high throughput and non-blocking I/O operations.
- **HTTP Connection Pool**: Manages and reuses TCP connections through a global `httpx.AsyncClient` instance, significantly improving performance under high concurrency.
- **Concurrency Control**: Built-in global and per-API endpoint concurrency semaphores effectively manage API request rates to prevent exceeding rate limits.
- **Automatic Retry Mechanism**: Integrated request retry functionality with exponential backoff strategy automatically handles temporary network fluctuations or server errors, enhancing service stability.
- **Intelligent Country Code Parsing**: Includes a comprehensive country name dictionary supporting inputs in Chinese, English, ISO Alpha-2/3, and other formats, with automatic normalization.
- **Flexible Environment Variable Configuration**: Supports fine-tuned service configuration via environment variables.

## Available Tools

This service provides the following tools:

| Tool Name                | Description                                  |
| ------------------------ | -------------------------------------------- |
| `serper-general-search`  | Performs general Google web searches.        |
| `serper-image-search`    | Performs Google image searches.               |
| `serper-video-search`    | Performs Google video searches.               |
| `serper-place-search`    | Performs Google place searches.               |
| `serper-maps_search`     | Performs Google Maps searches.                |
| `serper-news-search`     | Performs Google news searches.                |
| `serper-lens-search`     | Performs Google Lens reverse image searches via image URL. |
| `serper-scholar-search`  | Performs Google Scholar searches.             |
| `serper-shopping-search` | Performs Google Shopping searches.            |
| `serper-patents-search`  | Performs Google Patents searches.             |
| `serper-scrape`          | Scrapes and returns the content of a specified URL. |

## Installation Guide

It is recommended to install using `pip` or `uv`.

```bash
# Using pip
pip install serper-toolkit

# Or using uv
uv pip install serper-toolkit
```

## Quick Start

### Set Environment Variables

Create a `.env` file in the project root directory and enter your Serper API key:

```bash
SERPER_API_KEY="your-serper-api-key-here"
```

### Configure MCP Client

Add the following server configuration in the MCP client configuration file:

```json
{
  "mcpServers": {
    "serper": {
      "command": "python3",
      "args": ["-m", "serper-toolkit"],
      "env": {
        "SERPER_API_KEY": "<Your Serper API key>"
      }
    }
  }
}
```

```json
{
  "mcpServers": {
    "serper-toolkit": {
      "command": "uvx",
      "args": ["serper-toolkit"],
      "env": {
        "SERPER_API_KEY": "<Your Serper API key>"
      }
    }
  }
}
```

### Environment Variables

- `SERPER_MAX_CONNECTIONS`: Maximum number of HTTP client connections (default: 200).
- `SERPER_KEEPALIVE`: Maximum number of keep-alive HTTP client connections (default: 20).
- `SERPER_HTTP2`: Enable HTTP/2 (default: "0", set to "1" to enable).
- `SERPER_MAX_CONCURRENT_REQUESTS`: Global maximum concurrent requests (default: 200).
- `SERPER_RETRY_COUNT`: Maximum retry attempts for failed requests (default: 3).
- `SERPER_RETRY_BASE_DELAY`: Base delay time for retries in seconds (default: 0.5).
- `SERPER_ENDPOINT_CONCURRENCY`: Set concurrency per endpoint (JSON format), e.g., {"search":10,"scrape":2}.
- `SERPER_ENDPOINT_RETRYABLE`: Set retry allowance per endpoint (JSON format), e.g., {"scrape": false}.

## Tool Parameters and Usage Examples

### serper-general-search: Perform general web search

Parameters:

- `search_key_words` (str, required): Keywords to search.
- `search_country` (str, optional): Specify the country/region for search results. Supports Chinese names (e.g., "China"), English names (e.g., "United States"), or ISO codes (e.g., "US"). Default is "US".
- `search_num` (int, optional): Number of results to return, range 1-100. Default is 10.
- `search_time` (str, optional): Filter results by time range. Available values: "hour", "day", "week", "month", "year".

Example:

```Python
result_json = serper_general_search(
    search_key_words="AI advancements 2024",
    search_country="United States",
    search_num=5,
    search_time="month"
)
```

### serper-lens-search: Perform reverse image search via image URL

Parameters:

- `image_url` (str, required): Public URL of the image to search.
- `search_country` (str, optional): Specify the country/region for search results. Default is "US".

Example:

```Python
result_json = serper_lens_search(
    image_url="https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png",
    search_country="JP"
)
```

### serper-scrape: Scrape webpage content

Parameters:

- `url` (str, required): URL of the target webpage.
- `include_markdown` (bool, optional): Whether to include Markdown-formatted content in the returned results. Default is False.

Example:

```Python
result_json = serper_scrape(
    url="https://www.example.com",
    include_markdown=True
)
```

## License Agreement

This project is licensed under the MIT License.