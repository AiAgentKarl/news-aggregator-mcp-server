"""News Aggregator MCP Server — Nachrichten-Aggregation für AI-Agents.

Bietet:
- RSS/Atom Feed Aggregation (beliebige Feeds + 16 vordefinierte Quellen in 6 Kategorien)
- HackerNews Top/New/Best Stories + Story-Details + Keyword-Suche
- GDELT News Intelligence (globale Nachrichten, 65+ Sprachen, Trend-Analyse, Länder-Filter)
- Vollständig kostenlos, kein API-Key erforderlich
"""

from mcp.server.fastmcp import FastMCP

from src.tools.rss import register_rss_tools
from src.tools.hackernews import register_hackernews_tools
from src.tools.gdelt import register_gdelt_tools

# FastMCP Server erstellen
mcp = FastMCP(
    "News Aggregator MCP Server",
    instructions=(
        "Gibt AI-Agents Zugriff auf aktuelle Nachrichten weltweit: "
        "RSS/Atom-Feeds aus 6 Kategorien (Tech, AI, Business, Crypto, Science, General), "
        "HackerNews Top/New/Best Stories, und GDELT Global News Intelligence "
        "mit Abdeckung in 65+ Sprachen und 100+ Ländern. "
        "Alle Daten kostenlos ohne API-Key. "
        "Ideal für Research-Agents, Market Intelligence und Content-Aggregation."
    ),
)

# Tool-Gruppen registrieren
register_rss_tools(mcp)
register_hackernews_tools(mcp)
register_gdelt_tools(mcp)


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
