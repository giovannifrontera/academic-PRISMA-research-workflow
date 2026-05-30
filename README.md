<div align="center">

# Academic PRISMA Research Workflow

### Rigorous Research Orchestration via Claude Code

**Academic PRISMA Workflow** is an advanced toolkit that transforms Claude Code into a specialized research assistant for systematic reviews, pilot study design, and evidence synthesis.

[Pipeline](#the-research-pipeline) · [Capabilities](#core-skills) · [MCP Servers](#academic-connectivity) · [Quick Start](#quick-start)

</div>

---

## The Research Pipeline

This workflow automates the most labor-intensive stages of academic research while maintaining full methodological rigor:

```mermaid
graph LR;
    A[PRISMA Review] -->|evidence| B[Hybrid RAG];
    B -->|synthesis| C[Pilot Design];
    C -->|preprint| D[Academic Export];
```

By using a **State-Handoff Pattern**, each stage generates structured JSON/Markdown files, allowing researchers to audit, verify, and resume work across multiple sessions.

---

## Core Skills

| Skill | Description |
|---|---|
| **PRISMA Review** | A 6-phase automation of the systematic review process, from database identification to quality assessment. |
| **Hybrid RAG** | A local evidence-retrieval engine combining dense vector search and sparse BM25 retrieval for high-recall synthesis. |
| **Pilot Design** | Generates quasi-experimental study protocols with theoretical grounding and ethical compliance (GDPR/MIUR). |
| **Academic Export** | Orchestrates Pandoc to convert research outputs into publication-ready documents. |

---

## Academic Connectivity (MCP)

The system connects Claude directly to the global academic record via a suite of custom **Model Context Protocol (MCP)** servers:

*   **ERIC & OpenAIRE:** Education and European open-access research.
*   **CORE & DOAJ:** Full-text aggregators and open journals.
*   **Zenodo:** Preprints and Horizon Europe datasets.
*   **Semantic Scholar:** Citation-graph-based discovery.

---

## Quick Start

### 1. Install Skills
```powershell
Copy-Item -Recurse skills\* $env:USERPROFILE\.claude\skills\
```

### 2. Configure MCP
```bash
claude mcp add eric python server.py
# (see README-mcp.md for full configuration)
```

---

*Part of the **[AI-Wiki Ecosystem](https://github.com/giovannifrontera/giovannifrontera)** · Developed by Giovanni Frontera, Ph.D.*
