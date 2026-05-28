---
name: pipeline-ricerca
description: Use when starting a new academic research project, switching between skills mid-workflow, or needing to know which files connect prisma-review, hybrid-rag, edtech-pilot-design and pandoc-export. Reference for the complete PRISMA → RAG → Pilot → Preprint pipeline.
---

# Pipeline di Ricerca Accademica

## Flusso completo

```
[prisma-review]          → eligibility_prisma.json + prisma_synthesis.md
       ↓
[hybrid-rag]             → rag_db/
       ↓
[edtech-pilot-design]    → protocollo_ricerca.md + preprint_bozza.md
       ↓
[pandoc-export]          → preprint_bozza.docx
```

Ogni skill è invocata tramite il tool **`Skill`** di Claude Code (es. `Skill("prisma-review")`).

---

## Stage 1 — `prisma-review`

**Quando:** all'inizio di un progetto, per costruire la base bibliografica.

**Input richiesti:** domanda di ricerca (PICO), parametri di configurazione (anni, database, lingua).

**File prodotti:**

| File | Contenuto | Consumato da |
|---|---|---|
| `prisma_state.json` | Stato operativo + lista paper inclusi (dati minimi) | Ripresa di sessione |
| `prisma_log.md` | Log metodologico ufficiale per il paper | — |
| `screening_prisma.json` | Paper dopo deduplicazione (con abstract) | `hybrid-rag` (fallback) |
| `eligibility_prisma.json` / `extraction_table.json` | Paper inclusi con dati estratti completi | `hybrid-rag` (primario) |
| `prisma_synthesis.md` | Sintesi tematica + **sezione OUTPUT PER PILOT STUDY** | `edtech-pilot-design` |
| `prisma_bibliography.md` | Schede bibliografiche annotate | Report finale |

**File critico per il passaggio al Pilot:** `prisma_synthesis.md` — sezione **OUTPUT PER PILOT STUDY** (effect size aggregati, framework dominante, strumenti, RQ aperte, gap di popolazione, durata tipica interventi). Deve essere compilata durante la Fase 4, non solo alla fine.

---

## Stage 2 — `hybrid-rag`

**Quando:** dopo la Fase 4 di `prisma-review`, per costruire il database RAG per la generazione del report e per il pilot.

**Input richiesti:** `eligibility_prisma.json` (o `extraction_table.json`). Opzionale: cartella PDF manuali.

**Comandi minimi:**
```bash
py hybrid_rag.py choose-backend --backend lancedb  # raccomandato; ometti per usare chromadb
py hybrid_rag.py init
py hybrid_rag.py index-prisma eligibility_prisma.json
py hybrid_rag.py status
```

> `choose-model` è opzionale: il default `minilm` va bene per < 30 paper. Per 30-150 paper usa `--model e5-large` prima di `init`.

**File prodotti:**

| File/Cartella | Contenuto | Consumato da |
|---|---|---|
| `rag_db/` | Database vettoriale locale (LanceDB, ChromaDB o Qdrant) | `prisma-review` Fase 6, `edtech-pilot-design` |
| `rag_db/config.json` | Modello attivo, backend, indicizzazione | Ripresa di sessione |

**Dipendenza:** `hybrid_rag.py` deve esistere nella cartella di lavoro. Se non esiste: leggi `~/.claude/skills/hybrid-rag/hybrid_rag_template.py` e scrivilo con Write tool.

---

## Stage 3 — `edtech-pilot-design`

**Quando:** dopo `prisma-review` (e opzionalmente `hybrid-rag`), per progettare lo studio pilota.

**Input richiesti:**
- `prisma_synthesis.md` (sezione OUTPUT PER PILOT STUDY) — pre-compila automaticamente framework, effect size, strumenti, RQ
- `rag_db/` (opzionale) — abilita query RAG durante la progettazione

**File prodotti:**

| File | Contenuto | Consumato da |
|---|---|---|
| `protocollo_ricerca.md` | Protocollo completo (Blocco STATO + 10 sezioni) | `pandoc-export` (opzionale) |
| `strumenti_valutazione.md` | Questionari, tracce intervista, LA | — |
| `timeline_pilota.md` | Cronoprogramma settimanale | — |
| `preprint_bozza.md` | Paper IMRAD (Protocol o Results) | `pandoc-export` |

---

## Stage 4 — `pandoc-export`

**Quando:** al termine di `prisma-review` (report finale) o `edtech-pilot-design` (preprint).

**Input richiesti:** qualsiasi file `.md` da convertire.

**Output:** file `.docx` nella stessa cartella del sorgente.

---

## Entry point alternativi

| Situazione | Da dove partire |
|---|---|
| Primo progetto, nessun file | `prisma-review` Fase 0 |
| `prisma_state.json` esiste e valido | `prisma-review` — legge fase_corrente e riprende |
| `prisma_state.json` corrotto (JSON invalido) | Rinominalo in `prisma_state.json.bak`, avvisa l'utente, riparte da Fase 0 con i dati recuperabili da `prisma_log.md` |
| `eligibility_prisma.json` pronto, RAG non ancora costruito | `hybrid-rag` direttamente |
| `rag_db/` esiste, pilot non ancora avviato | `edtech-pilot-design` — rileva automaticamente `rag_db/` |
| `protocollo_ricerca.md` esiste | `edtech-pilot-design` — legge Blocco STATO e riprende |
| Dati già raccolti | `edtech-pilot-design` Fase 5 (Results Paper) |
| Solo export Word | `pandoc-export` direttamente |

---

## Handoff critico: prisma-review → edtech-pilot-design

La sezione **OUTPUT PER PILOT STUDY** di `prisma_synthesis.md` è l'unico meccanismo di trasferimento dati strutturato tra le due skill. Se questa sezione è vuota, `edtech-pilot-design` dovrà raccogliere manualmente tutte le informazioni bibliografiche.

Campi da compilare in `prisma_synthesis.md` prima di avviare `edtech-pilot-design`:

```markdown
### Effect size aggregati
| Outcome | N studi | Effect size medio | Range | Qualità evidenza |

### Framework teorici dominanti
[lista con frequenza]

### Strumenti di misura più usati
| Strumento | N studi | Outcome | Versione italiana |

### RQ non ancora investigate
[lista domande aperte]

### Gap di popolazione
[es. "Nessuno studio su secondaria italiana"]

### Durata tipica degli interventi
[Range min–max settimane; mediana]
```
