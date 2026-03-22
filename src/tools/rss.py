"""RSS/Atom Feed Tools — Nachrichten aus beliebigen Feeds abrufen."""

import asyncio
from typing import Any
import feedparser
import httpx


# Vordefinierte Nachrichten-Quellen nach Kategorie
FEED_KATALOG = {
    "tech": [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    ],
    "ai": [
        {"name": "MIT Technology Review AI", "url": "https://www.technologyreview.com/feed/"},
        {"name": "VentureBeat AI", "url": "https://venturebeat.com/ai/feed/"},
        {"name": "IEEE Spectrum AI", "url": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss"},
    ],
    "general": [
        {"name": "Reuters", "url": "https://feeds.reuters.com/reuters/topNews"},
        {"name": "BBC News", "url": "https://feeds.bbci.co.uk/news/rss.xml"},
        {"name": "AP News", "url": "https://rsshub.app/apnews/topics/apf-topnews"},
    ],
    "business": [
        {"name": "Bloomberg Technology", "url": "https://feeds.bloomberg.com/technology/news.rss"},
        {"name": "Financial Times", "url": "https://www.ft.com/rss/home"},
        {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    ],
    "crypto": [
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
        {"name": "CryptoSlate", "url": "https://cryptoslate.com/feed/"},
        {"name": "Decrypt", "url": "https://decrypt.co/feed"},
    ],
    "science": [
        {"name": "Nature News", "url": "https://www.nature.com/nature.rss"},
        {"name": "Science Daily", "url": "https://www.sciencedaily.com/rss/all.xml"},
        {"name": "NASA News", "url": "https://www.nasa.gov/news-release/feed/"},
    ],
}


def _artikel_extrahieren(feed_daten: feedparser.FeedParserDict, max_artikel: int = 5) -> list[dict]:
    """Extrahiert strukturierte Artikel-Daten aus einem geparsten Feed."""
    artikel = []
    for entry in feed_daten.entries[:max_artikel]:
        # Zusammenfassung bereinigen
        summary = ""
        if hasattr(entry, "summary"):
            summary = entry.summary
            # HTML-Tags entfernen (einfach)
            import re
            summary = re.sub(r"<[^>]+>", "", summary)[:500]

        artikel.append({
            "titel": getattr(entry, "title", "Kein Titel"),
            "url": getattr(entry, "link", ""),
            "zusammenfassung": summary,
            "veroeffentlicht": getattr(entry, "published", ""),
            "autor": getattr(entry, "author", ""),
            "tags": [t.get("term", "") for t in getattr(entry, "tags", [])],
        })
    return artikel


async def _feed_abrufen(feed_url: str, max_artikel: int = 5) -> dict[str, Any]:
    """Ruft einen einzelnen RSS/Atom-Feed ab und parst ihn."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                feed_url,
                headers={"User-Agent": "NewsAggregatorMCP/1.0 (AI Agent Feed Reader)"},
            )
            response.raise_for_status()
            feed_inhalt = response.text

        # Feedparser ist synchron — in Thread ausführen
        loop = asyncio.get_event_loop()
        feed_daten = await loop.run_in_executor(None, feedparser.parse, feed_inhalt)

        return {
            "feed_titel": feed_daten.feed.get("title", "Unbekannter Feed"),
            "feed_url": feed_url,
            "beschreibung": feed_daten.feed.get("subtitle", feed_daten.feed.get("description", "")),
            "letztes_update": feed_daten.feed.get("updated", ""),
            "artikel_anzahl": len(feed_daten.entries),
            "artikel": _artikel_extrahieren(feed_daten, max_artikel),
            "status": "ok",
        }
    except Exception as e:
        return {
            "feed_url": feed_url,
            "status": "fehler",
            "fehler": str(e),
        }


def register_rss_tools(mcp) -> None:
    """Registriert alle RSS/Atom Feed Tools."""

    @mcp.tool()
    async def fetch_feed(feed_url: str, max_articles: int = 10) -> dict:
        """Ruft einen beliebigen RSS/Atom-Feed ab und gibt strukturierte Artikel zurück.

        Args:
            feed_url: URL des RSS/Atom Feeds (z.B. https://techcrunch.com/feed/)
            max_articles: Maximale Anzahl Artikel (Standard: 10, max: 50)
        """
        max_articles = min(max_articles, 50)
        return await _feed_abrufen(feed_url, max_articles)

    @mcp.tool()
    async def get_news_by_category(category: str, max_per_feed: int = 3) -> dict:
        """Aggregiert Nachrichten aus vordefinierten Quellen einer Kategorie.

        Args:
            category: Kategorie — tech, ai, general, business, crypto, science
            max_per_feed: Artikel pro Feed (Standard: 3)
        """
        category = category.lower().strip()
        if category not in FEED_KATALOG:
            return {
                "fehler": f"Unbekannte Kategorie '{category}'",
                "verfuegbare_kategorien": list(FEED_KATALOG.keys()),
            }

        feeds = FEED_KATALOG[category]
        # Alle Feeds parallel abrufen
        tasks = [_feed_abrufen(f["url"], max_per_feed) for f in feeds]
        ergebnisse = await asyncio.gather(*tasks)

        alle_artikel = []
        quellen = []
        for i, ergebnis in enumerate(ergebnisse):
            if ergebnis.get("status") == "ok":
                quellen.append({
                    "name": feeds[i]["name"],
                    "url": feeds[i]["url"],
                    "artikel_count": len(ergebnis.get("artikel", [])),
                })
                for artikel in ergebnis.get("artikel", []):
                    artikel["quelle"] = feeds[i]["name"]
                    alle_artikel.append(artikel)

        return {
            "kategorie": category,
            "quellen": quellen,
            "gesamt_artikel": len(alle_artikel),
            "artikel": alle_artikel,
        }

    @mcp.tool()
    async def search_rss_feeds(query: str, categories: str = "all", max_results: int = 10) -> dict:
        """Durchsucht Nachrichten in allen Kategorien nach einem Suchbegriff.

        Args:
            query: Suchbegriff (z.B. "AI regulation", "Bitcoin", "climate")
            categories: Kommagetrennte Kategorien oder "all" für alle
            max_results: Maximale Gesamtergebnisse (Standard: 10)
        """
        query_lower = query.lower()

        # Kategorien bestimmen
        if categories.lower() == "all":
            aktive_kategorien = list(FEED_KATALOG.keys())
        else:
            aktive_kategorien = [c.strip().lower() for c in categories.split(",")]
            aktive_kategorien = [c for c in aktive_kategorien if c in FEED_KATALOG]

        if not aktive_kategorien:
            return {"fehler": "Keine gültigen Kategorien angegeben", "verfuegbare": list(FEED_KATALOG.keys())}

        # Alle Feeds der gewählten Kategorien sammeln
        alle_feeds = []
        feed_zu_kategorie = {}
        for kat in aktive_kategorien:
            for feed_info in FEED_KATALOG[kat]:
                alle_feeds.append(feed_info)
                feed_zu_kategorie[feed_info["url"]] = kat

        # Parallel abrufen
        tasks = [_feed_abrufen(f["url"], 10) for f in alle_feeds]
        ergebnisse = await asyncio.gather(*tasks)

        # Nach Suchbegriff filtern
        treffer = []
        for i, ergebnis in enumerate(ergebnisse):
            if ergebnis.get("status") != "ok":
                continue
            quelle = alle_feeds[i]["name"]
            kategorie = feed_zu_kategorie[alle_feeds[i]["url"]]
            for artikel in ergebnis.get("artikel", []):
                titel = artikel.get("titel", "").lower()
                zusammenfassung = artikel.get("zusammenfassung", "").lower()
                tags = " ".join(artikel.get("tags", [])).lower()
                if query_lower in titel or query_lower in zusammenfassung or query_lower in tags:
                    treffer.append({
                        **artikel,
                        "quelle": quelle,
                        "kategorie": kategorie,
                    })

        # Relevanz sortieren (Treffer im Titel höher gewichten)
        treffer.sort(key=lambda a: 2 if query_lower in a.get("titel", "").lower() else 1, reverse=True)

        return {
            "suchbegriff": query,
            "kategorien_durchsucht": aktive_kategorien,
            "treffer_gesamt": len(treffer),
            "treffer": treffer[:max_results],
        }

    @mcp.tool()
    async def list_feed_catalog() -> dict:
        """Gibt den vollständigen Katalog vordefinierter Nachrichten-Feeds zurück."""
        katalog_info = {}
        for kategorie, feeds in FEED_KATALOG.items():
            katalog_info[kategorie] = [
                {"name": f["name"], "url": f["url"]} for f in feeds
            ]
        return {
            "kategorien": list(FEED_KATALOG.keys()),
            "gesamt_feeds": sum(len(f) for f in FEED_KATALOG.values()),
            "katalog": katalog_info,
        }
