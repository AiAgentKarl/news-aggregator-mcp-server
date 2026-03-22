# news-aggregator-mcp-server

MCP-Server für Nachrichten-Aggregation — RSS/Atom-Feeds, HackerNews und GDELT Global News Intelligence für AI-Agents.

## Features

- **11 Tools** für umfassende Nachrichten-Abdeckung
- **RSS/Atom**: 16 vordefinierte Quellen in 6 Kategorien + beliebige Feeds
- **HackerNews**: Top/New/Best Stories, Story-Details, Keyword-Suche
- **GDELT**: Globale Nachrichten in 65+ Sprachen, 100+ Länder, Trend-Analyse
- **Kostenlos**: Kein API-Key erforderlich

## Installation

```bash
pip install news-aggregator-mcp-server
```

Oder via `uvx`:
```bash
uvx news-aggregator-mcp-server
```

## Claude Desktop Konfiguration

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

## Tools

### RSS/Atom Feeds
| Tool | Beschreibung |
|------|-------------|
| `fetch_feed` | Beliebigen RSS/Atom-Feed abrufen |
| `get_news_by_category` | News aus Kategorie (tech/ai/general/business/crypto/science) |
| `search_rss_feeds` | Feeds nach Keyword durchsuchen |
| `list_feed_catalog` | Alle vordefinierten Quellen anzeigen |

### HackerNews
| Tool | Beschreibung |
|------|-------------|
| `get_hackernews_top` | Top/New/Best/Ask/Show/Jobs Stories |
| `get_hackernews_story` | Story-Details mit Top-Kommentaren |
| `get_hackernews_trending` | Stories nach Keywords filtern |

### GDELT Global News
| Tool | Beschreibung |
|------|-------------|
| `search_global_news` | Weltweite Nachrichtensuche (65+ Sprachen) |
| `get_news_timeline` | News-Volumen-Trend über Zeit |
| `get_news_by_country` | Nachrichten nach Ländercode (DE, US, GB...) |
| `get_trending_topics` | Aktuelle Trending-Themen weltweit |

## Beispiel-Nutzung

```python
# Alle Tech-News der letzten Stunden
news = await get_news_by_category("ai", max_per_feed=5)

# HackerNews Top Stories
hn = await get_hackernews_top("top", limit=10)

# Weltweite Nachrichten über KI-Regulierung
global_news = await search_global_news("AI regulation", language="english")

# Trend-Analyse: Wie viel wird über Thema berichtet?
trend = await get_news_timeline("Bitcoin", timespan="7d")

# News aus Deutschland
de_news = await get_news_by_country("DE", query="Technologie")
```

## Kategorien (RSS-Feeds)

| Kategorie | Quellen |
|-----------|---------|
| `tech` | TechCrunch, Wired, Ars Technica, The Verge |
| `ai` | MIT Technology Review, VentureBeat AI, IEEE Spectrum AI |
| `general` | Reuters, BBC News, AP News |
| `business` | Bloomberg Technology, Financial Times, CNBC |
| `crypto` | CoinDesk, CryptoSlate, Decrypt |
| `science` | Nature News, Science Daily, NASA News |

## Lizenz

MIT
