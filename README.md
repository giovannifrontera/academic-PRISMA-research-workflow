# Academic PRISMA Research Workflow

A complete toolkit for AI-assisted academic research using [Claude Code](https://claude.ai/code). Covers the full pipeline from systematic literature review to pilot study design and preprint writing.

## What this does

**Five interconnected skills** guide you through the entire research workflow:

```
[prisma-review]       Systematic literature review (PRISMA methodology)
       ↓
[hybrid-rag]          Local vector database for evidence retrieval (Dense + BM25 + RRF)
       ↓
[edtech-pilot-design] Mixed-methods pilot study design (Ed-Tech / Italian school context)
       ↓
[pandoc-export]       Export any Markdown output to Word (.docx)
```

A fifth skill, **[pipeline-ricerca]**, serves as a cross-skill reference map with file dependencies and entry points for any stage of the workflow.

---

## Skills

| Skill | What it does |
|---|---|
| `prisma-review` | 6-phase PRISMA systematic review with MCP database search (Semantic Scholar, PubMed, ERIC, OpenAIRE), screening, eligibility, data extraction, quality assessment, and RAG-powered report generation |
| `hybrid-rag` | Builds and queries a local Hybrid RAG database from PRISMA JSON metadata or PDF documents. Combines dense vector search (ChromaDB or Qdrant + sentence-transformers) with BM25 sparse retrieval and Reciprocal Rank Fusion |
| `edtech-pilot-design` | Designs quasi-experimental mixed-methods pilot studies for Ed-Tech research. Covers framework, design, instruments (with Italian validation), power analysis, ethics (GDPR/MIUR), OSF pre-registration, and IMRAD preprint writing |
| `pipeline-ricerca` | Reference map of the full pipeline: file dependencies, handoff points, and 8 entry-point scenarios for resuming mid-workflow |
| `pandoc-export` | Converts Markdown outputs (PRISMA report, pilot protocol, preprint) to Word (.docx) using pandoc |

---

## MCP Servers

Two custom MCP servers extend Claude Code's search capabilities:

| Server | API | What it searches |
|---|---|---|
| `eric` | [ERIC API](https://api.ies.ed.gov/eric/) (free, no key) | Education Resources Information Center — peer-reviewed ed research |
| `ricerca-italia` | [OpenAIRE API](https://graph.openaire.eu/develop/api.html) (free, no key) | Italian institutional repositories, European open access |

Additionally, the workflow uses these installable MCP servers:

| Server | Install | Notes |
|---|---|---|
| `semantic-scholar` | `pip install semantic-scholar-fastmcp` | Requires free API key from [semanticscholar.org](https://www.semanticscholar.org/product/api) |
| `pubmed` | `pip install mcp-simple-pubmed` | Free, no key required |
| `arxiv` | `pip install arxiv-mcp-server` | Free, no key required |

---

## Installation

### 1. Install Claude Code

Follow the [official instructions](https://docs.anthropic.com/en/docs/claude-code).

### 2. Copy skills

```bash
# Linux / macOS
cp -r skills/* ~/.claude/skills/

# Windows (PowerShell)
Copy-Item -Recurse skills\* $env:USERPROFILE\.claude\skills\
```

### 3. Install MCP servers

```bash
# Local servers (ERIC + OpenAIRE) — copy to your Claude config folder
cp -r mcp-servers/eric ~/.claude/mcp-servers/
cp -r mcp-servers/ricerca-italia ~/.claude/mcp-servers/

# Register them with Claude Code
claude mcp add eric python ~/.claude/mcp-servers/eric/server.py
claude mcp add ricerca-italia python ~/.claude/mcp-servers/ricerca-italia/server.py

# Install via pip
pip install semantic-scholar-fastmcp mcp-simple-pubmed arxiv-mcp-server

# Register semantic-scholar with your API key
claude mcp add semantic-scholar semantic-scholar-fastmcp \
  -e SEMANTIC_SCHOLAR_API_KEY=your_key_here \
  -e SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE=0

# Register pubmed and arxiv
claude mcp add pubmed mcp-simple-pubmed
claude mcp add arxiv arxiv-mcp-server
```

### 4. Install hybrid-rag dependencies (on first use)

The `hybrid-rag` skill will copy `hybrid_rag_template.py` to your project folder and run:
```bash
py hybrid_rag.py init      # Windows
python3 hybrid_rag.py init # Linux / macOS
```
This automatically installs: `sentence-transformers`, `rank-bm25`, `pymupdf`, `chromadb`.

### 5. Verify

```bash
claude mcp list
```
All servers should show ✓ Connected.

---

## Usage

Start any skill via the `Skill` tool in Claude Code:

```
Skill("prisma-review")        # Start a new systematic review
Skill("hybrid-rag")           # Build or query the RAG database
Skill("edtech-pilot-design")  # Design a pilot study
Skill("pipeline-ricerca")     # Check workflow status and file map
Skill("pandoc-export")        # Export to Word
```

Or just describe your task — Claude Code will select the relevant skill automatically.

---

## Requirements

- Claude Code (any plan)
- Python 3.10+
- pandoc (for Word export) — `winget install JohnMacFarlane.Pandoc` on Windows

---

## Language

The skill instructions are written in **Italian**, targeting Italian academic researchers. The RAG system and MCP tools support both Italian and English queries.

---

## License

MIT
