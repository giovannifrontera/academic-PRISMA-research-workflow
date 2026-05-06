"""
ERIC MCP Server - Education Resources Information Center
Uses the free public ERIC API: https://api.ies.ed.gov/eric/
API uses Apache Solr syntax for field-specific queries.
"""

import json
import urllib.request
import urllib.parse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("eric")

ERIC_API = "https://api.ies.ed.gov/eric/"
DEFAULT_TIMEOUT = 30  # increased from 15s


def _build_solr_query(
    query: str,
    year_from: int = None,
    year_to: int = None,
    education_level: str = None,
    pub_type: str = None,
    language: str = None,
    title_only: bool = False,
) -> str:
    """Build a Solr query string combining free-text and field filters."""
    parts = []

    # Main query — optionally restricted to title field
    if query:
        if title_only:
            parts.append(f'title:({query})')
        else:
            parts.append(f'({query})')

    # Year range filter
    if year_from or year_to:
        y_from = year_from or "*"
        y_to = year_to or "*"
        parts.append(f'publicationdateyear:[{y_from} TO {y_to}]')

    # Education level filter
    # Common ERIC values: "Secondary Education", "Higher Education",
    # "Elementary Education", "Early Childhood Education", "Adult Education"
    if education_level:
        parts.append(f'educationlevel:"{education_level}"')

    # Publication type filter
    # Common values: "Journal Articles", "Reports - Research",
    # "Dissertations/Theses", "Books", "Reports - Descriptive"
    if pub_type:
        parts.append(f'publicationtype:"{pub_type}"')

    # Language filter
    if language:
        parts.append(f'language:"{language}"')

    return " AND ".join(parts) if parts else "*:*"


def _search(solr_query: str, rows: int = 10, start: int = 0) -> dict:
    params = {
        "search": solr_query,
        "format": "json",
        "rows": rows,
        "start": start,
    }
    url = ERIC_API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=DEFAULT_TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def _format_results(data: dict, query_label: str) -> str:
    response = data.get("response", {})
    total = response.get("numFound", 0)
    docs = response.get("docs", [])

    if not docs:
        return f"No results found for: {query_label}"

    results = [f"Found {total} results for '{query_label}' (showing {len(docs)}):\n"]

    for i, doc in enumerate(docs, 1):
        title = doc.get("title", "No title")
        authors = ", ".join(doc.get("author", [])) or "Unknown authors"
        year = doc.get("publicationdateyear", "n.d.")
        source = doc.get("source", "")
        eric_id = doc.get("id", "")
        abstract = doc.get("description", "")
        pub_type = ", ".join(doc.get("publicationtype", []))
        edu_level = ", ".join(doc.get("educationlevel", []))

        result = f"{i}. **{title}**\n"
        result += f"   Authors: {authors} ({year})\n"
        if source:
            result += f"   Source: {source}\n"
        if pub_type:
            result += f"   Type: {pub_type}\n"
        if edu_level:
            result += f"   Education Level: {edu_level}\n"
        if eric_id:
            result += f"   ERIC ID: {eric_id} | URL: https://eric.ed.gov/?id={eric_id}\n"
        if abstract:
            result += f"   Abstract: {abstract[:300]}{'...' if len(abstract) > 300 else ''}\n"

        results.append(result)

    return "\n".join(results)


@mcp.tool()
def eric_search(
    query: str,
    rows: int = 10,
    start: int = 0,
) -> str:
    """
    Search the ERIC database (Education Resources Information Center).
    Covers peer-reviewed journals, reports, curriculum guides, and more
    related to education, pedagogy, and learning.

    Supports Apache Solr field syntax for precise queries:
      - title:"chatbot"                    → search in title only
      - descriptor:"Artificial Intelligence" → controlled vocabulary
      - educationlevel:"Secondary Education" → filter by school level
      - publicationdateyear:[2020 TO 2025]  → year range
      - publicationtype:"Journal Articles"  → filter by type

    For precise multi-field queries, use eric_advanced_search instead.

    Args:
        query: Search query. Supports boolean (AND, OR, NOT) and Solr field syntax.
        rows: Number of results to return (default 10, max 200)
        start: Offset for pagination (default 0)
    """
    data = _search(query, rows=rows, start=start)
    return _format_results(data, query)


@mcp.tool()
def eric_advanced_search(
    query: str,
    year_from: int = None,
    year_to: int = None,
    education_level: str = None,
    pub_type: str = None,
    language: str = None,
    title_only: bool = False,
    rows: int = 10,
    start: int = 0,
) -> str:
    """
    Advanced search on ERIC with structured filters. Builds a precise
    Solr query combining free-text search with field-level filters.

    Education level values (use exact strings):
      "Secondary Education"     → high school / secondary school
      "Higher Education"        → university / college
      "Elementary Education"    → primary school
      "Early Childhood Education"
      "Adult Education"
      "Postsecondary Education"

    Publication type values:
      "Journal Articles"
      "Reports - Research"
      "Reports - Descriptive"
      "Dissertations/Theses"
      "Books"
      "Conference Papers"

    Language values: "English", "Italian", "Chinese", "Spanish", etc.

    Args:
        query: Main search terms (supports AND, OR, NOT)
        year_from: Start year (e.g. 2020)
        year_to: End year (e.g. 2025)
        education_level: Filter by education level (see above)
        pub_type: Filter by publication type (see above)
        language: Filter by language (e.g. "English")
        title_only: If True, restrict query to title field only
        rows: Number of results (default 10, max 200)
        start: Pagination offset (default 0)
    """
    solr_query = _build_solr_query(
        query=query,
        year_from=year_from,
        year_to=year_to,
        education_level=education_level,
        pub_type=pub_type,
        language=language,
        title_only=title_only,
    )
    data = _search(solr_query, rows=rows, start=start)
    label = f"{query} [filters: level={education_level}, years={year_from}-{year_to}, type={pub_type}, lang={language}]"
    return _format_results(data, label)


@mcp.tool()
def eric_get_record(eric_id: str) -> str:
    """
    Retrieve full details for a specific ERIC record by its ID.

    Args:
        eric_id: The ERIC document ID (e.g., EJ1234567 or ED123456)
    """
    solr_query = f"id:{eric_id}"
    data = _search(solr_query, rows=1)
    docs = data.get("response", {}).get("docs", [])

    if not docs:
        return f"Record not found: {eric_id}"

    doc = docs[0]
    lines = []
    lines.append(f"# {doc.get('title', 'No title')}")
    lines.append(f"**ERIC ID:** {doc.get('id', '')}")
    lines.append(f"**Authors:** {', '.join(doc.get('author', [])) or 'Unknown'}")
    lines.append(f"**Year:** {doc.get('publicationdateyear', 'n.d.')}")
    lines.append(f"**Source:** {doc.get('source', '')}")
    lines.append(f"**Type:** {', '.join(doc.get('publicationtype', []))}")
    lines.append(f"**Education Level:** {', '.join(doc.get('educationlevel', []))}")
    lines.append(f"**Subject:** {', '.join(doc.get('subject', []))}")
    lines.append(f"**Descriptor:** {', '.join(doc.get('descriptor', []))}")
    lines.append(f"**Language:** {', '.join(doc.get('language', []))}")
    lines.append(f"\n**Abstract:**\n{doc.get('description', 'No abstract available')}")
    lines.append(f"\n**URL:** https://eric.ed.gov/?id={doc.get('id', '')}")

    return "\n".join(lines)


@mcp.tool()
def eric_search_by_descriptor(
    descriptor: str,
    year_from: int = None,
    year_to: int = None,
    education_level: str = None,
    rows: int = 10,
) -> str:
    """
    Search ERIC using controlled vocabulary descriptors (ERIC Thesaurus terms).
    More precise than free-text search. Optionally combine with year and
    education level filters.

    Common descriptors: "Artificial Intelligence", "Educational Technology",
    "Computer Assisted Instruction", "Academic Achievement", "Self Efficacy",
    "Technology Integration", "Blended Learning", "Distance Education"

    Args:
        descriptor: ERIC thesaurus descriptor term
        year_from: Start year filter (optional)
        year_to: End year filter (optional)
        education_level: Education level filter (optional, e.g. "Secondary Education")
        rows: Number of results (default 10)
    """
    solr_query = _build_solr_query(
        query=f'descriptor:"{descriptor}"',
        year_from=year_from,
        year_to=year_to,
        education_level=education_level,
    )
    data = _search(solr_query, rows=rows)
    label = f'descriptor:"{descriptor}" [level={education_level}, years={year_from}-{year_to}]'
    return _format_results(data, label)


if __name__ == "__main__":
    mcp.run(transport="stdio")
