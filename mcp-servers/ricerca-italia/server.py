"""
Italian/European Academic Databases MCP Server
Uses OpenAIRE API (openaire.eu) to search publications from:
- Italian institutional repositories (IRIS network)
- Italian open journals (OJS, riviste OA)
- European open access research outputs
API docs: https://graph.openaire.eu/develop/api.html
"""

import json
import urllib.request
import urllib.parse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ricerca-italia")

OPENAIRE_SEARCH_API = "https://api.openaire.eu/search/publications"
OPENAIRE_GRAPH_API = "https://api.openaire.eu/graph/v1/researchProducts"
DEFAULT_TIMEOUT = 30


def _search_publications(
    keywords: str,
    country: str = None,
    year_from: int = None,
    year_to: int = None,
    page: int = 1,
    size: int = 10,
    open_access: bool = None,
) -> dict:
    params = {
        "keywords": keywords,
        "format": "json",
        "page": page,
        "size": size,
    }
    if country:
        params["country"] = country
    if year_from:
        params["fromDateAccepted"] = f"{year_from}-01-01"
    if year_to:
        params["toDateAccepted"] = f"{year_to}-12-31"
    if open_access is True:
        params["OA"] = "true"
    elif open_access is False:
        params["OA"] = "false"

    url = OPENAIRE_SEARCH_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def _extract_field(obj, *keys):
    """Navigate nested dict safely, return None if any key is missing."""
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _parse_result(result: dict) -> dict:
    """Extract relevant fields from an OpenAIRE publication record."""
    metadata = _extract_field(result, "metadata", "oaf:entity", "oaf:result") or {}

    # Title
    title_obj = metadata.get("title", {})
    if isinstance(title_obj, list):
        title = title_obj[0].get("$", "") if title_obj else ""
    elif isinstance(title_obj, dict):
        title = title_obj.get("$", "")
    else:
        title = str(title_obj) if title_obj else ""

    # Authors
    creators = metadata.get("creator", [])
    if isinstance(creators, dict):
        creators = [creators]
    authors = [c.get("$", "") for c in creators if isinstance(c, dict)]

    # Date
    date = metadata.get("dateofacceptance", {})
    year = date.get("$", "")[:4] if isinstance(date, dict) else ""

    # Abstract
    desc = metadata.get("description", {})
    if isinstance(desc, list):
        abstract = desc[0].get("$", "") if desc else ""
    elif isinstance(desc, dict):
        abstract = desc.get("$", "")
    else:
        abstract = ""

    # DOI / identifiers
    pid = metadata.get("pid", [])
    if isinstance(pid, dict):
        pid = [pid]
    doi = ""
    for p in (pid or []):
        if isinstance(p, dict) and p.get("@classid") == "doi":
            doi = p.get("$", "")
            break

    # Source / journal
    source = metadata.get("source", {})
    if isinstance(source, list):
        journal = source[0].get("$", "") if source else ""
    elif isinstance(source, dict):
        journal = source.get("$", "")
    else:
        journal = ""

    # Best available URL
    best_access = metadata.get("bestaccessright", {})
    oa = best_access.get("@classid", "") == "OPEN" if isinstance(best_access, dict) else False

    # OpenAIRE ID
    header = result.get("header", {})
    oa_id = header.get("dri:objIdentifier", {}).get("$", "") if isinstance(header, dict) else ""

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "abstract": abstract,
        "doi": doi,
        "journal": journal,
        "open_access": oa,
        "openaire_id": oa_id,
    }


def _format_results(data: dict, query_label: str) -> str:
    response = data.get("response", {})
    header = response.get("header", {})
    total = _extract_field(header, "total", "$") or "0"

    results_obj = response.get("results", {})
    if not results_obj:
        return f"Nessun risultato per: {query_label}"

    raw_results = results_obj.get("result", [])
    if isinstance(raw_results, dict):
        raw_results = [raw_results]

    if not raw_results:
        return f"Nessun risultato per: {query_label}"

    lines = [f"Trovati {total} risultati per '{query_label}' (mostro {len(raw_results)}):\n"]

    for i, result in enumerate(raw_results, 1):
        rec = _parse_result(result)
        authors_str = ", ".join(rec["authors"][:3])
        if len(rec["authors"]) > 3:
            authors_str += " et al."

        line = f"{i}. **{rec['title'] or '(senza titolo)'}**\n"
        line += f"   Autori: {authors_str or 'N/D'} ({rec['year'] or 'n.d.'})\n"
        if rec["journal"]:
            line += f"   Rivista: {rec['journal']}\n"
        if rec["doi"]:
            line += f"   DOI: {rec['doi']}\n"
        if rec["openaire_id"]:
            line += f"   OpenAIRE: https://explore.openaire.eu/search/publication?articleId={rec['openaire_id']}\n"
        oa_label = "Open Access" if rec["open_access"] else "Accesso limitato"
        line += f"   Accesso: {oa_label}\n"
        if rec["abstract"]:
            abstract_short = rec["abstract"][:300]
            if len(rec["abstract"]) > 300:
                abstract_short += "..."
            line += f"   Abstract: {abstract_short}\n"
        lines.append(line)

    return "\n".join(lines)


@mcp.tool()
def openaire_search(
    query: str,
    year_from: int = None,
    year_to: int = None,
    country: str = None,
    open_access: bool = None,
    rows: int = 10,
    page: int = 1,
) -> str:
    """
    Cerca pubblicazioni accademiche su OpenAIRE (openaire.eu).
    Copre repository istituzionali italiani (rete IRIS), riviste open access
    italiane (OJS) e output di ricerca europei.

    Args:
        query: Termini di ricerca (es. "chatbot education metacognition")
        year_from: Anno iniziale (es. 2015)
        year_to: Anno finale (es. 2025)
        country: Codice paese ISO per filtrare (es. "IT" per Italia, "FR" per Francia)
        open_access: True = solo OA, False = solo non-OA, None = tutti
        rows: Numero di risultati (default 10, max 100)
        page: Pagina dei risultati (default 1)
    """
    data = _search_publications(
        keywords=query,
        country=country,
        year_from=year_from,
        year_to=year_to,
        page=page,
        size=rows,
        open_access=open_access,
    )
    return _format_results(data, query)


@mcp.tool()
def openaire_search_italy(
    query: str,
    year_from: int = None,
    year_to: int = None,
    open_access: bool = True,
    rows: int = 10,
    page: int = 1,
) -> str:
    """
    Cerca pubblicazioni accademiche italiane su OpenAIRE.
    Filtra automaticamente per paese Italia (IT).
    Utile per includere fonti italiane nelle review PRISMA.

    Args:
        query: Termini di ricerca
        year_from: Anno iniziale
        year_to: Anno finale
        open_access: True = solo OA (default), None = tutti
        rows: Numero di risultati (default 10)
        page: Pagina (default 1)
    """
    data = _search_publications(
        keywords=query,
        country="IT",
        year_from=year_from,
        year_to=year_to,
        page=page,
        size=rows,
        open_access=open_access,
    )
    label = f"{query} [Italia]"
    return _format_results(data, label)


@mcp.tool()
def openaire_count(
    query: str,
    year_from: int = None,
    year_to: int = None,
    country: str = None,
) -> str:
    """
    Restituisce solo il conteggio totale dei risultati senza scaricare i record.
    Utile per stimare il volume prima della Fase 1 di una review PRISMA.

    Args:
        query: Termini di ricerca
        year_from: Anno iniziale
        year_to: Anno finale
        country: Codice paese ISO (es. "IT")
    """
    data = _search_publications(
        keywords=query,
        country=country,
        year_from=year_from,
        year_to=year_to,
        size=1,
    )
    response = data.get("response", {})
    header = response.get("header", {})
    total = _extract_field(header, "total", "$") or "0"
    country_label = f" [{country}]" if country else ""
    years_label = ""
    if year_from or year_to:
        years_label = f" [{year_from or ''}–{year_to or ''}]"
    return f"Totale risultati per '{query}'{country_label}{years_label}: **{total}**"


if __name__ == "__main__":
    mcp.run(transport="stdio")
