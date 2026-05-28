<div align="center">

# Academic PRISMA Research Workflow

**A Claude Code toolkit for rigorous, reproducible academic research**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Claude Code](https://img.shields.io/badge/Powered_by-Claude_Code-purple.svg)](https://claude.ai/code)

</div>

This workflow turns Claude Code into a structured academic research assistant. It covers the full pipeline — from PRISMA systematic literature reviews to pilot study design and preprint export — using a set of interconnected skills and custom MCP servers that connect Claude directly to academic databases.

---

## Pipeline

```mermaid
graph LR;
    A[prisma-review] -->|eligibility_prisma.json| B[hybrid-rag];
    B -->|rag_db/| C[edtech-pilot-design];
    C -->|preprint_bozza.md| D[pandoc-export];
```

Each stage hands off structured files to the next, so you can resume mid-workflow across sessions without losing context.

---

## Skills

| Skill | What it does |
|---|---|
| `prisma-review` | Runs a 6-phase PRISMA systematic review: database search across 8 sources, deduplication, screening, eligibility, data extraction with quality scoring, and RAG-powered report generation. |
| `hybrid-rag` | Builds a local hybrid retrieval database from your PRISMA metadata or PDFs. Combines dense vector search (sentence-transformers) with BM25 sparse retrieval and Reciprocal Rank Fusion for high-recall evidence retrieval. |
| `edtech-pilot-design` | Designs a mixed-methods quasi-experimental pilot study. Covers theoretical framework, instruments, power analysis, ethics (GDPR/MIUR), OSF pre-registration, and IMRAD preprint drafting. Tailored for Italian Ed-Tech research contexts. |
| `pipeline-ricerca` | Reference map of the full pipeline: file dependencies, handoff points between skills, and entry-point scenarios for resuming at any stage. |
| `pandoc-export` | Converts any Markdown output (review report, pilot protocol, preprint) to Word (.docx) via pandoc. |

---

## MCP Servers

Eight academic database servers give Claude direct search access during the PRISMA identification phase. Each is a separate server so result counts can be tracked per source, as required by PRISMA reporting.

### Custom servers (included in this repo)

| Server | Source | Coverage | API key |
|---|---|---|---|
| `eric` | [ERIC API](https://api.ies.ed.gov/eric/) | Education research, peer-reviewed | No |
| `openaire` | [OpenAIRE Graph API](https://graph.openaire.eu/develop/api.html) | European open access + Italian institutional repositories (IRIS) | No |
| `core` | [CORE API v3](https://api.core.ac.uk/docs/v3) | Full-text OA aggregator, strong Italian repository coverage | Free |
| `doaj` | [DOAJ API](https://doaj.org/api/docs) | Open access journals, filterable by publisher country | No |
| `zenodo` | [Zenodo REST API](https://developers.zenodo.org/) | Preprints, datasets, Horizon Europe outputs | No |

### External servers (pip-installable)

| Server | Install | API key |
|---|---|---|
| `semantic-scholar` | `pip install semantic-scholar-fastmcp` | Free — [get one here](https://www.semanticscholar.org/product/api) |
| `pubmed` | `pip install mcp-simple-pubmed` | No |
| `arxiv` | `pip install arxiv-mcp-server` | No |

---

## Installation

### Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.10+
- [Pandoc](https://pandoc.org/installing.html) (for Word export only)

> **RAG dependencies** (`sentence-transformers`, `rank-bm25`, `pymupdf`, `chromadb`) are installed automatically the first time you run `hybrid-rag`. You do not need to install them manually.

### 1. Install the skills

**Linux / macOS**
```bash
cp -r skills/* ~/.claude/skills/
```

**Windows (PowerShell)**
```powershell
Copy-Item -Recurse skills\* $env:USERPROFILE\.claude\skills\
```

### 2. Install the custom MCP servers

**Linux / macOS**
```bash
cp -r mcp-servers/eric mcp-servers/openaire mcp-servers/core mcp-servers/doaj mcp-servers/zenodo ~/.claude/mcp-servers/

claude mcp add eric     python ~/.claude/mcp-servers/eric/server.py
claude mcp add openaire python ~/.claude/mcp-servers/openaire/server.py
claude mcp add doaj     python ~/.claude/mcp-servers/doaj/server.py
claude mcp add zenodo   python ~/.claude/mcp-servers/zenodo/server.py

# CORE requires a free API key — get one at https://core.ac.uk/services/api
claude mcp add core python ~/.claude/mcp-servers/core/server.py \
  -e CORE_API_KEY=your_key_here
```

**Windows (PowerShell)**
```powershell
$mcp = "$env:USERPROFILE\.claude\mcp-servers"
Copy-Item -Recurse mcp-servers\eric, mcp-servers\openaire, mcp-servers\core, mcp-servers\doaj, mcp-servers\zenodo $mcp\

$py = (Get-Command python).Source
claude mcp add eric     $py "$mcp\eric\server.py"
claude mcp add openaire $py "$mcp\openaire\server.py"
claude mcp add doaj     $py "$mcp\doaj\server.py"
claude mcp add zenodo   $py "$mcp\zenodo\server.py"

# CORE requires a free API key — get one at https://core.ac.uk/services/api
claude mcp add core $py "$mcp\core\server.py" -e CORE_API_KEY=your_key_here
```

### 3. Install the external MCP servers

```bash
pip install semantic-scholar-fastmcp mcp-simple-pubmed arxiv-mcp-server

# semantic-scholar requires a free API key
claude mcp add semantic-scholar semantic-scholar-fastmcp \
  -e SEMANTIC_SCHOLAR_API_KEY=your_key_here \
  -e SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE=0

claude mcp add pubmed mcp-simple-pubmed
claude mcp add arxiv  arxiv-mcp-server
```

### 4. Verify

```bash
claude mcp list
# All servers should show ✓ Connected
```

---

## How the RAG system works

The `hybrid-rag` skill uses a **generated script** pattern rather than a pre-installed package:

1. The first time you invoke `hybrid-rag`, Claude writes `hybrid_rag.py` into your project folder by copying it from the installed skill template.
2. You then run `py hybrid_rag.py init`, which installs the required Python packages and creates a `rag_db/` directory in your project folder.
3. Subsequent commands (`index-prisma`, `query`, etc.) operate on that local database.

The `rag_db/` directory is **local to each project** — it is never committed to version control and does not exist until you run `init`. Each research project gets its own database built from its own PRISMA results.

---

## Usage

Start any skill by describing your task in Claude Code:

```
Start a PRISMA systematic review on chatbot use in secondary education
```

```
Build a RAG database from my eligibility_prisma.json
```

```
Design a pilot study based on my PRISMA synthesis
```

```
Export report_finale.md to Word
```

The `pipeline-ricerca` skill acts as a map if you need to resume mid-workflow or understand which files connect which stages.

---

## Notes

- Skill instructions are written in **Italian**, as the workflow targets Italian academic researchers (Ed-Tech, Scienze della Formazione). The MCP tools and RAG system handle both Italian and English documents.
- The `edtech-pilot-design` skill includes Italian-specific content: MIUR/INVALSI compliance, Italian validated instruments, and OSF pre-registration guidance.

---

## License

[AGPL-3.0](LICENSE) — anyone who distributes or runs this software as a service must publish the source code.
