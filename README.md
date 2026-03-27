# news-aggregator-mcp-server

**Multi-source news aggregation for AI agents** — RSS/Atom feeds, HackerNews, and GDELT global news intelligence.

[![PyPI version](https://badge.fury.io/py/news-aggregator-mcp-server.svg)](https://pypi.org/project/news-aggregator-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **No API key required.** 16 built-in news sources, HackerNews API, and GDELT covering 65+ languages and 100+ countries.

## Quick Start

```bash
pip install news-aggregator-mcp-server
```

Add to your MCP client config:

```json
{
  "mcpServers": {
    "news-aggregator": {
      "command": "uvx",
      "args": ["news-aggregator-mcp-server"]
    }
  }
}
```

**That's it.** Ask your AI: *"What are the top tech news today?"*

## What Can You Do?

**Ask your AI agent things like:**
- *"Show me the top HackerNews stories about AI"*
- *"What's trending in global news about climate change?"*
- *"Get me the latest crypto news from CoinDesk and CryptoSlate"*
- *"How much media coverage is Bitcoin getting this week?"*
- *"What are the top news stories from Germany today?"*

## 11 Tools

### RSS/Atom Feeds (16 built-in sources)
| Tool | What it does |
|------|-------------|
| `fetch_feed` | Fetch any RSS/Atom feed by URL |
| `get_news_by_category` | News by category: tech, ai, general, business, crypto, science |
| `search_rss_feeds` | Search feeds by keyword |
| `list_feed_catalog` | Show all built-in sources |

### HackerNews
| Tool | What it does |
|------|-------------|
| `get_hackernews_top` | Top/New/Best/Ask/Show/Jobs stories |
| `get_hackernews_story` | Story details with top comments |
| `get_hackernews_trending` | Filter stories by keywords |

### GDELT Global News Intelligence
| Tool | What it does |
|------|-------------|
| `search_global_news` | Search worldwide news (65+ languages) |
| `get_news_timeline` | News volume trends over time |
| `get_news_by_country` | News filtered by country code (DE, US, GB...) |
| `get_trending_topics` | Currently trending topics worldwide |

## Built-in News Sources

| Category | Sources |
|----------|---------|
| Tech | TechCrunch, Wired, Ars Technica, The Verge |
| AI | MIT Technology Review, VentureBeat AI, IEEE Spectrum AI |
| General | Reuters, BBC News, AP News |
| Business | Bloomberg Technology, Financial Times, CNBC |
| Crypto | CoinDesk, CryptoSlate, Decrypt |
| Science | Nature News, Science Daily, NASA News |

## Related Servers

- [social-trends-mcp-server](https://pypi.org/project/social-trends-mcp-server/) — Reddit & HackerNews trending analysis
- [cybersecurity-mcp-server](https://pypi.org/project/cybersecurity-mcp-server/) — CVE database & vulnerability intelligence

## License

MIT
