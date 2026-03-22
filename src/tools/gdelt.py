"""GDELT News Intelligence Tools — Globale Nachrichten-Analyse und Trends."""

import httpx
from typing import Any


GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_GEO_API = "https://api.gdeltproject.org/api/v2/geo/geo"


async def _gdelt_suche(params: dict) -> dict[str, Any]:
    """Führt eine GDELT API-Anfrage durch."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(GDELT_DOC_API, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}


def _artikel_formatieren(artikel: dict) -> dict:
    """Formatiert einen GDELT-Artikel."""
    return {
        "titel": artikel.get("title", ""),
        "url": artikel.get("url", ""),
        "quelle": artikel.get("domain", ""),
        "sprache": artikel.get("language", ""),
        "land": artikel.get("sourcecountry", ""),
        "seendate": artikel.get("seendate", ""),
        "socialshares": artikel.get("socialsharecount", 0),
    }


def register_gdelt_tools(mcp) -> None:
    """Registriert alle GDELT News Intelligence Tools."""

    @mcp.tool()
    async def search_global_news(query: str, mode: str = "artlist", max_records: int = 10, language: str = "") -> dict:
        """Durchsucht globale Nachrichten via GDELT — deckt 65+ Sprachen und 100+ Länder ab.

        Args:
            query: Suchanfrage (z.B. "AI regulation", "climate change Germany")
            mode: Suchmodus — artlist (Artikelliste), artgallery (mit Bildern)
            max_records: Maximale Ergebnisse (Standard: 10, max: 250)
            language: Sprachfilter (z.B. "german", "english", leer = alle)
        """
        max_records = min(max_records, 250)

        # Query aufbauen
        suchbegriff = query
        if language:
            suchbegriff = f"{query} sourcelang:{language}"

        params = {
            "query": suchbegriff,
            "mode": mode,
            "maxrecords": max_records,
            "format": "json",
            "sort": "DateDesc",
        }

        daten = await _gdelt_suche(params)

        if "error" in daten:
            return {"fehler": daten["error"], "suchbegriff": query}

        artikel_liste = daten.get("articles", [])
        return {
            "suchbegriff": query,
            "sprache_filter": language or "alle",
            "gefunden": len(artikel_liste),
            "artikel": [_artikel_formatieren(a) for a in artikel_liste],
            "quelle": "GDELT Project (Global News Database)",
        }

    @mcp.tool()
    async def get_news_timeline(query: str, timespan: str = "1d") -> dict:
        """Analysiert News-Volumen über Zeit für ein Thema (Trend-Analyse).

        Args:
            query: Thema oder Suchbegriff
            timespan: Zeitraum — 15min, 1h, 4h, 1d, 3d, 7d, 1m (Standard: 1d)
        """
        gueltige_zeitraeume = ["15min", "1h", "4h", "1d", "3d", "7d", "1m"]
        if timespan not in gueltige_zeitraeume:
            timespan = "1d"

        params = {
            "query": query,
            "mode": "timelinevol",
            "timespan": timespan,
            "format": "json",
        }

        daten = await _gdelt_suche(params)

        if "error" in daten:
            return {"fehler": daten["error"], "suchbegriff": query}

        timeline = daten.get("timeline", [{}])
        zeitreihe = []
        if timeline:
            datenpunkte = timeline[0].get("data", [])
            for punkt in datenpunkte[-20:]:  # Letzte 20 Datenpunkte
                zeitreihe.append({
                    "zeitpunkt": punkt.get("date", ""),
                    "volumen": punkt.get("value", 0),
                })

        # Trend berechnen
        trend = "unbekannt"
        if len(zeitreihe) >= 2:
            erster = zeitreihe[0].get("volumen", 0)
            letzter = zeitreihe[-1].get("volumen", 0)
            if letzter > erster * 1.2:
                trend = "steigend"
            elif letzter < erster * 0.8:
                trend = "sinkend"
            else:
                trend = "stabil"

        return {
            "suchbegriff": query,
            "zeitraum": timespan,
            "trend": trend,
            "datenpunkte": len(zeitreihe),
            "timeline": zeitreihe,
            "quelle": "GDELT News Volume Analysis",
        }

    @mcp.tool()
    async def get_news_by_country(country_code: str, query: str = "", max_records: int = 10) -> dict:
        """Ruft Nachrichten aus einem bestimmten Land ab.

        Args:
            country_code: 2-Buchstaben Ländercode (z.B. DE, US, GB, FR, JP)
            query: Optionaler Zusatz-Suchbegriff
            max_records: Maximale Ergebnisse (Standard: 10)
        """
        country_code = country_code.upper()
        suchbegriff = f"sourcecountry:{country_code}"
        if query:
            suchbegriff = f"{query} {suchbegriff}"

        params = {
            "query": suchbegriff,
            "mode": "artlist",
            "maxrecords": max_records,
            "format": "json",
            "sort": "DateDesc",
        }

        daten = await _gdelt_suche(params)

        if "error" in daten:
            return {"fehler": daten["error"], "land": country_code}

        artikel_liste = daten.get("articles", [])
        return {
            "land": country_code,
            "suchbegriff": query or "(alle Themen)",
            "gefunden": len(artikel_liste),
            "artikel": [_artikel_formatieren(a) for a in artikel_liste],
            "quelle": "GDELT Global News",
        }

    @mcp.tool()
    async def get_trending_topics(timespan: str = "1d", tone_filter: str = "") -> dict:
        """Ermittelt aktuelle Trending-Themen weltweit via GDELT.

        Args:
            timespan: Zeitraum — 1h, 4h, 1d, 3d, 7d (Standard: 1d)
            tone_filter: Stimmungsfilter — positive, negative, neutral (leer = alle)
        """
        # GDELT Tone-Analyse: tonechart Modus
        tone_query = ""
        if tone_filter == "positive":
            tone_query = " tone>5"
        elif tone_filter == "negative":
            tone_query = " tone<-5"

        # Beliebte Trending-Themen durch breite Suche ermitteln
        themen_suchanfragen = [
            "AI artificial intelligence" + tone_query,
            "economy finance market" + tone_query,
            "climate environment" + tone_query,
            "politics government election" + tone_query,
            "technology startup innovation" + tone_query,
        ]

        ergebnisse = []
        async with httpx.AsyncClient(timeout=15.0) as client:
            for thema in themen_suchanfragen:
                try:
                    response = await client.get(
                        GDELT_DOC_API,
                        params={
                            "query": thema,
                            "mode": "artlist",
                            "maxrecords": 3,
                            "timespan": timespan,
                            "format": "json",
                        },
                    )
                    daten = response.json()
                    artikel = daten.get("articles", [])
                    if artikel:
                        ergebnisse.append({
                            "thema": thema.replace(tone_query, "").strip(),
                            "artikel_count": len(artikel),
                            "top_artikel": [_artikel_formatieren(a) for a in artikel[:2]],
                        })
                except Exception:
                    continue

        return {
            "zeitraum": timespan,
            "stimmung_filter": tone_filter or "alle",
            "themen": ergebnisse,
            "quelle": "GDELT Global News Intelligence",
        }
