"""
CORE MCP Server
Searches CORE (core.ac.uk) — the world's largest aggregator of open access
research. Provides direct access to full-text papers from Italian and
international institutional repositories.
API docs: https://api.core.ac.uk/docs/v3
Requires a free API key: https://core.ac.uk/services/api
"""

import json
import urllib.request
import urllib.parse
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("core")

BASE_URL = "https://api.core.ac.uk/v3"
DEFAULT_TIMEOUT = 30
API_KEY = os.environ.get("CORE_API_KEY", "")


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


def _post(endpoint: str, payload: dict) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(), method="POST")
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def _format_results(results: list, label: str, total: int) -> str:
    if not results:
        return f"CORE — nessun risultato per: {label}"
    lines = [f"CORE — {total} risultati per '{label}' (mostro {len(results)}):\n"]
    for i, r in enumerate(results, 1):
        authors = r.get("authors", [])
        if isinstance(authors, list):
            auth_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in authors[:3]]
            auth_str = ", ".join(filter(None, auth_names))
            if len(authors) > 3:
                auth_str += " et al."
        else:
            auth_str = ""

        year = r.get("yearPublished", "") or ""
        title = r.get("title", "(senza titolo)") or "(senza titolo)"
        abstract = r.get("abstract", "") or ""
        doi = r.get("doi", "") or ""
        url_link = r.get("sourceFulltextUrls", [None])[0] if r.get("sourceFulltextUrls") else ""
        journal = r.get("journals", [{}])[0].get("title", "") if r.get("journals") else ""
        core_id = r.get("id", "")

        line = f"{i}. **{title}**\n"
        line += f"   {auth_str or 'N/D'} ({year or 'n.d.'})\n"
        if journal:
            line += f"   Rivista: {journal}\n"
        if doi:
            line += f"   DOI: {doi}\n"
        if core_id:
            line += f"   CORE: https://core.ac.uk/works/{core_id}\n"
        if url_link:
            line += f"   Fulltext: {url_link}\n"
        if abstract:
            line += f"   Abstract: {abstract[:300]}{'...' if len(abstract) > 300 else ''}\n"
        lines.append(line)
    return "\n".join(lines)


@mcp.tool()
def core_search(
    query: str,
    year_from: int = None,
    year_to: int = None,
    language: str = None,
    rows: int = 10,
    offset: int = 0,
) -> str:
    """
    Search CORE for open access full-text papers.
    CORE aggregates Italian institutional repositories (IRIS network) and
    thousands of global repositories. Ideal for finding full-text OA papers.
    Requires CORE_API_KEY environment variable (free at core.ac.uk/services/api).

    Args:
        query: Search terms (e.g. "artificial intelligence secondary school")
        year_from: Start year (e.g. 2015)
        year_to: End year (e.g. 2025)
        language: Language code (e.g. "it" for Italian, "en" for English)
        rows: Number of results (default 10, max 100)
        offset: Pagination offset (default 0)
    """
    filters = []
    if year_from:
        filters.append({"field": "yearPublished", "value": year_from, "operation": "GREATER_OR_EQUAL"})
    if year_to:
        filters.append({"field": "yearPublished", "value": year_to, "operation": "LESS_OR_EQUAL"})
    if language:
        filters.append({"field": "language.code", "value": language, "operation": "EQUALS"})

    payload = {
        "q": query,
        "limit": rows,
        "offset": offset,
        "filters": filters,
    }
    data = _post("search/works", payload)
    results = data.get("results", [])
    total = data.get("totalHits", 0)
    return _format_results(results, query, total)


@mcp.tool()
def core_count(
    query: str,
    year_from: int = None,
    year_to: int = None,
) -> str:
    """
    Return total result count from CORE without downloading records.
    Use at PRISMA Phase 1 to estimate volume.

    Args:
        query: Search terms
        year_from: Start year
        year_to: End year
    """
    filters = []
    if year_from:
        filters.append({"field": "yearPublished", "value": year_from, "operation": "GREATER_OR_EQUAL"})
    if year_to:
        filters.append({"field": "yearPublished", "value": year_to, "operation": "LESS_OR_EQUAL"})
    payload = {"q": query, "limit": 1, "offset": 0, "filters": filters}
    data = _post("search/works", payload)
    total = data.get("totalHits", 0)
    parts = [f"CORE — risultati per '{query}'"]
    if year_from or year_to:
        parts.append(f"[{year_from or ''}-{year_to or ''}]")
    return " ".join(parts) + f": **{total}**"


@mcp.tool()
def core_get(work_id: str) -> str:
    """
    Retrieve full metadata for a specific CORE work by its ID.
    Use to get complete details (fulltext URL, affiliations) for a paper
    identified during screening.

    Args:
        work_id: CORE work ID (numeric, from core_search results)
    """
    url = f"{BASE_URL}/works/{work_id}"
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        r = json.loads(resp.read().decode())

    authors = r.get("authors", [])
    auth_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in authors]
    abstract = r.get("abstract", "") or ""
    fulltext_urls = r.get("sourceFulltextUrls", []) or []
    affiliations = []
    for a in authors:
        if isinstance(a, dict):
            for aff in a.get("affiliations", []):
                if isinstance(aff, dict) and aff.get("name"):
                    affiliations.append(aff["name"])

    lines = [
        f"**{r.get('title', 'N/D')}**",
        f"Autori: {', '.join(auth_names) or 'N/D'}",
        f"Anno: {r.get('yearPublished', 'n.d.')}",
        f"DOI: {r.get('doi', 'N/D')}",
        f"CORE ID: {r.get('id', 'N/D')}",
        f"Lingua: {r.get('language', {}).get('name', 'N/D') if isinstance(r.get('language'), dict) else 'N/D'}",
    ]
    if affiliations:
        lines.append(f"Affiliazioni: {'; '.join(set(affiliations))}")
    if fulltext_urls:
        lines.append(f"Fulltext: {fulltext_urls[0]}")
    if abstract:
        lines.append(f"\nAbstract:\n{abstract}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
