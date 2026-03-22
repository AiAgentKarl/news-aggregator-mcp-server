"""HackerNews Tools — Tech-News und Community-Trends von Hacker News."""

import asyncio
import httpx
from typing import Any


HN_API = "https://hacker-news.firebaseio.com/v0"


async def _item_abrufen(client: httpx.AsyncClient, item_id: int) -> dict[str, Any] | None:
    """Ruft ein einzelnes HN-Item (Story/Comment) ab."""
    try:
        response = await client.get(f"{HN_API}/item/{item_id}.json")
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


async def _top_stories_laden(story_typ: str, max_stories: int = 10) -> list[dict]:
    """Lädt Top-Stories eines bestimmten Typs von HackerNews."""
    endpunkte = {
        "top": "topstories",
        "new": "newstories",
        "best": "beststories",
        "ask": "askstories",
        "show": "showstories",
        "jobs": "jobstories",
    }
    endpunkt = endpunkte.get(story_typ, "topstories")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Story-IDs abrufen
        response = await client.get(f"{HN_API}/{endpunkt}.json")
        response.raise_for_status()
        story_ids = response.json()[:max_stories]

        # Alle Stories parallel abrufen
        tasks = [_item_abrufen(client, sid) for sid in story_ids]
        items = await asyncio.gather(*tasks)

    # Gültige Stories formatieren
    stories = []
    for item in items:
        if not item or item.get("type") not in ("story", "job"):
            continue
        stories.append({
            "id": item.get("id"),
            "titel": item.get("title", ""),
            "url": item.get("url", f"https://news.ycombinator.com/item?id={item.get('id')}"),
            "punkte": item.get("score", 0),
            "kommentare": item.get("descendants", 0),
            "autor": item.get("by", ""),
            "veroeffentlicht_unix": item.get("time", 0),
            "hn_link": f"https://news.ycombinator.com/item?id={item.get('id')}",
            "typ": item.get("type", "story"),
        })

    return stories


def register_hackernews_tools(mcp) -> None:
    """Registriert alle HackerNews Tools."""

    @mcp.tool()
    async def get_hackernews_top(story_type: str = "top", limit: int = 10) -> dict:
        """Ruft Top-Stories von Hacker News ab.

        Args:
            story_type: Art der Stories — top, new, best, ask, show, jobs (Standard: top)
            limit: Anzahl Stories (Standard: 10, max: 30)
        """
        limit = min(limit, 30)
        stories = await _top_stories_laden(story_type, limit)
        return {
            "typ": story_type,
            "stories_count": len(stories),
            "stories": stories,
            "quelle": "Hacker News",
        }

    @mcp.tool()
    async def get_hackernews_story(story_id: int) -> dict:
        """Ruft Details zu einer spezifischen HackerNews-Story ab.

        Args:
            story_id: Numerische ID der HN-Story (z.B. 39876543)
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            item = await _item_abrufen(client, story_id)

        if not item:
            return {"fehler": f"Story {story_id} nicht gefunden"}

        # Top-Kommentare laden wenn vorhanden
        kommentare = []
        kommentar_ids = item.get("kids", [])[:5]
        if kommentar_ids:
            async with httpx.AsyncClient(timeout=10.0) as client:
                tasks = [_item_abrufen(client, kid) for kid in kommentar_ids]
                kommentar_items = await asyncio.gather(*tasks)
            for k in kommentar_items:
                if k and k.get("text"):
                    import re
                    text = re.sub(r"<[^>]+>", "", k.get("text", ""))[:300]
                    kommentare.append({
                        "autor": k.get("by", ""),
                        "text": text,
                        "punkte": k.get("score", 0),
                    })

        return {
            "id": item.get("id"),
            "titel": item.get("title", ""),
            "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            "punkte": item.get("score", 0),
            "kommentare_anzahl": item.get("descendants", 0),
            "autor": item.get("by", ""),
            "typ": item.get("type", ""),
            "hn_link": f"https://news.ycombinator.com/item?id={story_id}",
            "top_kommentare": kommentare,
        }

    @mcp.tool()
    async def get_hackernews_trending(keywords: str, limit: int = 5) -> dict:
        """Sucht HackerNews Top-Stories nach Keywords.

        Args:
            keywords: Suchbegriffe kommagetrennt (z.B. "AI, Claude, MCP")
            limit: Maximale Treffer (Standard: 5)
        """
        search_terms = [k.strip().lower() for k in keywords.split(",")]

        # Top 50 Stories laden und filtern
        stories = await _top_stories_laden("top", 50)

        treffer = []
        for story in stories:
            titel_lower = story["titel"].lower()
            url_lower = story.get("url", "").lower()
            for term in search_terms:
                if term in titel_lower or term in url_lower:
                    story["matched_keyword"] = term
                    treffer.append(story)
                    break

        return {
            "keywords": search_terms,
            "treffer": treffer[:limit],
            "treffer_count": len(treffer),
            "basis": "HackerNews Top 50 Stories",
        }
