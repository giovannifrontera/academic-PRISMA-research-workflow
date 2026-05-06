#!/usr/bin/env python3
"""
hybrid_rag.py — Hybrid RAG per ricerche accademiche
Operazioni: init | choose-model | choose-backend | index-prisma | index-pdf | query | status

Generato dalla skill ~/.claude/skills/hybrid-rag
Backend supportati: chromadb (default) | qdrant
"""

import argparse
import itertools
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Optional

# ── Catalogo modelli ──────────────────────────────────────────────────────────
MODEL_CATALOG = {
    "minilm": {
        "name": "paraphrase-multilingual-MiniLM-L12-v2",
        "label": "MiniLM-L12-v2 (default)",
        "dim": 384,
        "disk_mb": 400,
        "ram_mb": 500,
        "doc_prefix": "",
        "query_prefix": "",
        "notes": "Veloce su CPU. Buona qualità multilingue (italiano + inglese).",
        "index_s_per_paper": 0.08,
        "query_s": 0.2,
    },
    "e5-large": {
        "name": "intfloat/multilingual-e5-large",
        "label": "multilingual-e5-large (Microsoft)",
        "dim": 1024,
        "disk_mb": 1200,
        "ram_mb": 1500,
        "doc_prefix": "passage: ",
        "query_prefix": "query: ",
        "notes": "Ottima qualità. Prefissi query/passage gestiti automaticamente.",
        "index_s_per_paper": 0.45,
        "query_s": 0.8,
    },
    "bge-m3": {
        "name": "BAAI/bge-m3",
        "label": "BGE-M3 (BAAI)",
        "dim": 1024,
        "disk_mb": 2300,
        "ram_mb": 3000,
        "doc_prefix": "",
        "query_prefix": "",
        "notes": "Eccellente qualità multilingue. Pesante su CPU (~1s/paper).",
        "index_s_per_paper": 1.1,
        "query_s": 1.5,
    },
}
DEFAULT_MODEL_KEY = "minilm"

# ── Costanti ──────────────────────────────────────────────────────────────────
RAG_DIR = "rag_db"
CONFIG_FILE = Path(RAG_DIR) / "config.json"
COLLECTION_PRISMA = "prisma_papers"
COLLECTION_PDF = "pdf_manual"
SOURCE_PRISMA = "prisma_json"
SOURCE_PDF = "pdf_manual"
BACKEND_CHROMA = "chromadb"
BACKEND_QDRANT = "qdrant"
RRF_K = 60
CHUNK_SIZE = 800
DENSE_FETCH_MULTIPLIER = 3


# ── Config ────────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"model_key": DEFAULT_MODEL_KEY, "backend": BACKEND_CHROMA}

def _save_config(cfg: dict):
    Path(RAG_DIR).mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def _active_model_cfg(cfg: Optional[dict] = None) -> dict:
    if cfg is None:
        cfg = _load_config()
    key = cfg.get("model_key", DEFAULT_MODEL_KEY)
    return MODEL_CATALOG.get(key, MODEL_CATALOG[DEFAULT_MODEL_KEY])


# ── Encoder (cached) ──────────────────────────────────────────────────────────

_encoder_cache: dict = {}

def _get_encoder(model_name: str):
    if model_name not in _encoder_cache:
        from sentence_transformers import SentenceTransformer
        print(f"Caricamento modello: {model_name} …")
        _encoder_cache[model_name] = SentenceTransformer(model_name)
    return _encoder_cache[model_name]

def _embed_docs(texts: list, model_cfg: dict) -> list:
    enc = _get_encoder(model_cfg["name"])
    prefix = model_cfg.get("doc_prefix", "")
    prefixed = [prefix + t for t in texts] if prefix else texts
    return enc.encode(prefixed, show_progress_bar=False).tolist()

def _embed_query(text: str, model_cfg: dict) -> list:
    enc = _get_encoder(model_cfg["name"])
    prefix = model_cfg.get("query_prefix", "")
    return enc.encode(prefix + text, show_progress_bar=False).tolist()


# ── Backend astratto ──────────────────────────────────────────────────────────
#
# Interfaccia comune a ChromaDB e Qdrant. Ogni metodo restituisce strutture
# dati uniformi: search/get_all → list[{id, text, meta, score, collection}]

class _ChromaBackend:
    def __init__(self):
        import chromadb
        self._client = chromadb.PersistentClient(path=RAG_DIR)

    def name(self) -> str:
        return BACKEND_CHROMA

    def init_collections(self, vector_size: int):
        self._client.get_or_create_collection(COLLECTION_PRISMA)
        self._client.get_or_create_collection(COLLECTION_PDF)

    def upsert(self, coll: str, docs: list, embeddings: list, ids: list, metas: list):
        collection = self._client.get_or_create_collection(coll)
        collection.upsert(documents=docs, embeddings=embeddings, ids=ids, metadatas=metas)

    def search(self, coll: str, query_emb: list, n: int, filter_obj=None) -> list:
        try:
            collection = self._client.get_collection(coll)
            total = collection.count()
            if total == 0:
                return []
            r = collection.query(
                query_embeddings=[query_emb],
                n_results=min(n, total),
                include=["documents", "metadatas", "distances", "ids"]
            )
            return [
                {
                    "id": doc_id, "text": doc, "meta": meta,
                    "score": round(max(0, 1 - dist), 4),
                    "collection": coll,
                }
                for doc, meta, dist, doc_id in zip(
                    r["documents"][0], r["metadatas"][0],
                    r["distances"][0], r["ids"][0]
                )
            ]
        except Exception as e:
            print(f"  Errore dense search su {coll}: {e}")
            return []

    def get_all(self, coll: str) -> list:
        try:
            collection = self._client.get_collection(coll)
            result = collection.get(include=["documents", "metadatas"])
            return [
                {"id": doc_id, "text": doc, "meta": meta, "collection": coll}
                for doc, meta, doc_id in zip(
                    result["documents"], result["metadatas"], result["ids"]
                )
            ]
        except Exception:
            return []

    def count(self, coll: str) -> int:
        try:
            return self._client.get_collection(coll).count()
        except Exception:
            return 0

    def list_collections(self) -> list:
        return [c.name for c in self._client.list_collections()]


class _QdrantBackend:
    def __init__(self):
        from qdrant_client import QdrantClient
        self._client = QdrantClient(path=f"{RAG_DIR}/qdrant")

    def name(self) -> str:
        return BACKEND_QDRANT

    def init_collections(self, vector_size: int):
        from qdrant_client.models import Distance, VectorParams
        for coll in [COLLECTION_PRISMA, COLLECTION_PDF]:
            if not self._client.collection_exists(coll):
                self._client.create_collection(
                    collection_name=coll,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )

    def _to_uuid(self, s: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, s))

    def upsert(self, coll: str, docs: list, embeddings: list, ids: list, metas: list):
        from qdrant_client.models import PointStruct
        points = [
            PointStruct(
                id=self._to_uuid(str_id),
                vector=emb,
                payload={"_doc_id": str_id, "_text": doc, **meta},
            )
            for str_id, doc, emb, meta in zip(ids, docs, embeddings, metas)
        ]
        self._client.upsert(collection_name=coll, points=points)

    def _point_to_doc(self, point, coll: str) -> dict:
        payload = point.payload or {}
        meta = {k: v for k, v in payload.items() if not k.startswith("_")}
        return {
            "id":         payload.get("_doc_id", str(point.id)),
            "text":       payload.get("_text", ""),
            "meta":       meta,
            "score":      getattr(point, "score", 0.0),
            "collection": coll,
        }

    def search(self, coll: str, query_emb: list, n: int, filter_obj=None) -> list:
        try:
            results = self._client.search(
                collection_name=coll,
                query_vector=query_emb,
                limit=n,
                with_payload=True,
                query_filter=filter_obj,
            )
            return [self._point_to_doc(r, coll) for r in results]
        except Exception as e:
            print(f"  Errore dense search su {coll}: {e}")
            return []

    def get_all(self, coll: str) -> list:
        try:
            records, _ = self._client.scroll(
                collection_name=coll,
                limit=10_000,
                with_payload=True,
                with_vectors=False,
            )
            return [self._point_to_doc(r, coll) for r in records]
        except Exception:
            return []

    def count(self, coll: str) -> int:
        try:
            return self._client.count(collection_name=coll).count
        except Exception:
            return 0

    def list_collections(self) -> list:
        return [c.name for c in self._client.get_collections().collections]


_backend_instance: Optional[object] = None

def _get_backend(cfg: Optional[dict] = None):
    global _backend_instance
    if _backend_instance is None:
        if cfg is None:
            cfg = _load_config()
        if cfg.get("backend", BACKEND_CHROMA) == BACKEND_QDRANT:
            _backend_instance = _QdrantBackend()
        else:
            _backend_instance = _ChromaBackend()
    return _backend_instance


# ── DEPS ──────────────────────────────────────────────────────────────────────

def _deps_installed(backend: str = BACKEND_CHROMA) -> bool:
    try:
        import sentence_transformers, rank_bm25, fitz  # noqa: F401
        if backend == BACKEND_QDRANT:
            import qdrant_client  # noqa: F401
        else:
            import chromadb  # noqa: F401
        return True
    except ImportError:
        return False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_time(seconds: float) -> str:
    return f"~{seconds:.0f}s" if seconds < 60 else f"~{seconds/60:.1f} min"

def _paper_field(paper: dict, *keys: str, default: str = "") -> str:
    """Returns first non-empty value among the given keys (supports IT/EN fallback)."""
    for key in keys:
        val = paper.get(key)
        if val:
            return str(val)
    return default

def _assign_pages(chunks: list, page_boundaries: list) -> list:
    """Maps each chunk to its page number using precomputed cumulative offsets — O(n)."""
    if not page_boundaries:
        return [1] * len(chunks)
    cum_positions = list(itertools.accumulate(len(c) for c in chunks))
    pages = []
    for pos in cum_positions:
        page = page_boundaries[-1][1]
        for boundary, pnum in page_boundaries:
            if pos <= boundary:
                page = pnum
                break
        pages.append(page)
    return pages

def _parse_qdrant_filter(filter_str: str):
    """
    Converte 'year>=2020,source_db=eric' in un oggetto Filter Qdrant.
    Operatori: = >= <= > <   Valori numerici per range, stringhe per match.
    Restituisce None se la stringa è vuota o non valida.
    """
    from qdrant_client.models import Filter, FieldCondition, Range, MatchValue
    conditions = []
    for part in filter_str.split(","):
        part = part.strip()
        m = re.match(r"(\w+)\s*(>=|<=|>|<|=)\s*(.+)", part)
        if not m:
            print(f"  Filtro ignorato (sintassi non valida): '{part}'")
            continue
        key, op, val = m.groups()
        if op == "=":
            conditions.append(FieldCondition(key=key, match=MatchValue(value=val)))
        else:
            try:
                num = float(val) if "." in val else int(val)
            except ValueError:
                print(f"  Filtro ignorato (valore non numerico per operatore range): '{part}'")
                continue
            range_map = {">=": {"gte": num}, "<=": {"lte": num}, ">": {"gt": num}, "<": {"lt": num}}
            conditions.append(FieldCondition(key=key, range=Range(**range_map[op])))
    return Filter(must=conditions) if conditions else None

def _rrf_merge(ranked_lists: list, k: int = RRF_K) -> list:
    scores: dict = {}
    for ranked in ranked_lists:
        for rank, (doc_id, _) in enumerate(ranked):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ── CHOOSE BACKEND ────────────────────────────────────────────────────────────

def op_choose_backend(backend_key: Optional[str] = None):
    cfg = _load_config()
    current = cfg.get("backend", BACKEND_CHROMA)

    backend_info = {
        BACKEND_CHROMA: {
            "label": "ChromaDB (default)",
            "notes": "Pure Python, zero config, storage in rag_db/. Ottimo per corpus < 50k doc.",
        },
        BACKEND_QDRANT: {
            "label": "Qdrant",
            "notes": (
                "Filtri avanzati su metadati (--filter year>=2020,source_db=eric), "
                "HNSW ottimizzato. Storage in rag_db/qdrant/. Richiede qdrant-client."
            ),
        },
    }

    if backend_key is None:
        print("\n## Selezione backend vettoriale\n")
        for key, info in backend_info.items():
            marker = " ◀ attivo" if key == current else ""
            print(f"  [{key}]{marker}")
            print(f"    {info['notes']}\n")

        print("Nota: cambiare backend richiede 'py hybrid_rag.py init' + re-indicizzazione.")
        choice = input(
            f"Inserisci chiave [{'/'.join(backend_info.keys())}] (invio = mantieni {current}): "
        ).strip().lower()
        if not choice:
            print(f"Nessuna modifica. Backend attivo: {current}")
            return
        backend_key = choice

    if backend_key not in backend_info:
        print(f"Chiave non valida: '{backend_key}'. Valori: {', '.join(backend_info.keys())}")
        sys.exit(1)

    if backend_key != current:
        has_data = bool(cfg.get("indexed_with"))
        if has_data:
            print(f"\nATTENZIONE: il DB attuale ('{current}') contiene dati indicizzati.")
            print("Cambiare backend richiede: rm -rf rag_db/ → py hybrid_rag.py init → re-indicizza.")
            confirm = input("Procedere comunque? [s/N] ").strip().lower()
            if confirm != "s":
                print("Annullato.")
                return

    cfg["backend"] = backend_key
    _save_config(cfg)
    print(f"\nBackend impostato: {backend_key} — {backend_info[backend_key]['label']}")
    if backend_key == BACKEND_QDRANT:
        print("Ora esegui: py hybrid_rag.py init  (installa qdrant-client e crea le collezioni)")
        print("Query con filtro: py hybrid_rag.py query '...' --filter 'year>=2020,source_db=eric'")


# ── CHOOSE MODEL ──────────────────────────────────────────────────────────────

def op_choose_model(n_papers: Optional[int] = None, model_key: Optional[str] = None):
    cfg = _load_config()
    current_key = cfg.get("model_key", DEFAULT_MODEL_KEY)

    if model_key is None:
        print("\n## Selezione modello embedding\n")
        print(f"{'Chiave':<10} {'Modello':<44} {'Disco':>7} {'RAM':>7}")
        print("-" * 72)
        for key, m in MODEL_CATALOG.items():
            marker = " ◀ attivo" if key == current_key else ""
            print(f"{key:<10} {m['label']:<44} {m['disk_mb']:>5} MB {m['ram_mb']:>5} MB{marker}")

        if n_papers:
            print(f"\n### Stime su CPU — {n_papers} paper\n")
            print(f"{'Chiave':<10} {'Indicizzazione':>16} {'Query singola':>14} {'RAM':>10}")
            print("-" * 56)
            for key, m in MODEL_CATALOG.items():
                print(
                    f"{key:<10} {_fmt_time(m['index_s_per_paper'] * n_papers):>16}"
                    f" {_fmt_time(m['query_s']):>14} {m['ram_mb']:>8} MB"
                )
            print("\n  *Stime su CPU i5/i7. Con GPU CUDA i tempi si riducono di 5–10x.")

        print("\nNote:")
        for key, m in MODEL_CATALOG.items():
            print(f"  [{key}]  {m['notes']}")

        print()
        choice = input(
            f"Inserisci chiave [{'/'.join(MODEL_CATALOG.keys())}] (invio = mantieni {current_key}): "
        ).strip().lower()
        if not choice:
            print(f"Nessuna modifica. Modello attivo: {current_key}")
            return
        model_key = choice

    if model_key not in MODEL_CATALOG:
        print(f"Chiave non valida: '{model_key}'. Valori: {', '.join(MODEL_CATALOG.keys())}")
        sys.exit(1)

    if model_key != current_key:
        indexed_with = cfg.get("indexed_with")
        backend = _get_backend(cfg)
        has_data = any(
            backend.count(c) > 0 for c in [COLLECTION_PRISMA, COLLECTION_PDF]
        )
        if has_data and indexed_with and indexed_with != model_key:
            print(f"\nATTENZIONE: il DB contiene documenti indicizzati con '{indexed_with}'.")
            print("Cambiare modello causerà incompatibilità delle dimensioni dei vettori.")
            print("Soluzione: rm -rf rag_db/ → py hybrid_rag.py init → re-indicizza")
            confirm = input("Vuoi comunque cambiare modello? [s/N] ").strip().lower()
            if confirm != "s":
                print("Annullato.")
                return

    cfg["model_key"] = model_key
    _save_config(cfg)
    m = MODEL_CATALOG[model_key]
    print(f"\nModello impostato: {model_key} — {m['label']}")
    print(f"Disco (download HuggingFace): ~{m['disk_mb']} MB | RAM: ~{m['ram_mb']} MB")
    if cfg.get("backend") == BACKEND_QDRANT:
        print(f"Nota Qdrant: il modello ha dim={m['dim']}. Re-esegui init se la dim è cambiata.")


# ── INIT ──────────────────────────────────────────────────────────────────────

def op_init():
    cfg = _load_config()
    backend_key = cfg.get("backend", BACKEND_CHROMA)

    if not _deps_installed(backend_key):
        print(f"Installazione dipendenze per backend '{backend_key}'...")
        import subprocess
        packages = ["sentence-transformers", "rank-bm25", "pymupdf"]
        if backend_key == BACKEND_QDRANT:
            packages.append("qdrant-client")
        else:
            packages.append("chromadb")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + packages,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("Errore installazione dipendenze:")
            print(result.stderr[-2000:])
            sys.exit(1)
    else:
        print("Dipendenze già installate.")

    Path(RAG_DIR).mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        _save_config({"model_key": DEFAULT_MODEL_KEY, "backend": BACKEND_CHROMA})

    model_cfg = _active_model_cfg(cfg)
    backend = _get_backend(cfg)
    backend.init_collections(vector_size=model_cfg["dim"])

    active_key = cfg.get("model_key", DEFAULT_MODEL_KEY)
    print(f"RAG inizializzato in '{RAG_DIR}/' (backend: {backend_key})")
    print(f"Modello attivo: {active_key} — {model_cfg['label']} (dim={model_cfg['dim']})")
    print(f"Suggerimento: usa 'choose-model --n-papers N' per stime su misura")
    if backend_key == BACKEND_QDRANT:
        print("Filtri disponibili in query: --filter 'year>=2020,source_db=eric'")


# ── INDEX PRISMA ──────────────────────────────────────────────────────────────

def _build_prisma_doc(paper: dict) -> str:
    pf = _paper_field
    fields = [
        ("TITOLO",             pf(paper, "titolo", "title")),
        ("AUTORI",             pf(paper, "autori", "authors")),
        ("ANNO",               pf(paper, "anno", "year")),
        ("DOI",                pf(paper, "doi")),
        ("FONTE DB",           pf(paper, "source_db")),
        ("ABSTRACT",           pf(paper, "abstract")),
        ("DESIGN",             pf(paper, "design_studio", "study_design")),
        ("FRAMEWORK TEORICO",  pf(paper, "framework_teorico", "theoretical_framework")),
        ("TIPO TECNOLOGIA",    pf(paper, "tipo_tecnologia", "technology_type")),
        ("CAMPIONE",           pf(paper, "campione", "sample")),
        ("DURATA INTERVENTO",  pf(paper, "durata_intervento", "duration")),
        ("STRUMENTI MISURA",   pf(paper, "strumenti_misura", "instruments")),
        ("OUTCOME",            pf(paper, "outcome")),
        ("EFFECT SIZE",        pf(paper, "effect_size")),
        ("IC 95%",             pf(paper, "ic_95")),
        ("QUALITA STUDIO",     pf(paper, "qualita_studio", "quality")),
        ("RISULTATI CHIAVE",   pf(paper, "risultati_chiave", "key_findings")),
        ("LIMITAZIONI",        pf(paper, "limitazioni", "limitations")),
        ("RQ RISPOSTA",        pf(paper, "rq_risposta", "rq_response")),
        ("ANNOTAZIONE",        pf(paper, "annotazione", "annotation")),
    ]
    return "\n".join(f"{k}: {v}" for k, v in fields if v)


def op_index_prisma(json_path: str):
    path = Path(json_path)
    if not path.exists():
        print(f"File non trovato: {json_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        papers = data
    elif isinstance(data, dict) and "fase4" in data:
        papers = data["fase4"].get("paper_inclusi", [])
        print("AVVISO: stai indicizzando da prisma_state.json (dati minimi).")
        print("Per un RAG di qualità superiore usa: eligibility_prisma.json o screening_prisma.json")
    elif isinstance(data, dict):
        papers = list(data.values())
    else:
        papers = []

    if not papers:
        print("Nessun paper trovato nel JSON.")
        return

    cfg = _load_config()
    model_cfg = _active_model_cfg(cfg)
    n = len(papers)
    print(f"Modello: {model_cfg['label']} | Paper: {n} | Stima CPU: {_fmt_time(model_cfg['index_s_per_paper'] * n)}")

    backend = _get_backend(cfg)
    pf = _paper_field
    docs, ids, metas = [], [], []

    for i, paper in enumerate(papers):
        raw_id = paper.get("doi") or paper.get("id") or f"paper_{i}"
        doc_id = str(raw_id).replace("/", "_").replace(":", "_")[:100]
        docs.append(_build_prisma_doc(paper))
        ids.append(doc_id)
        # year come int per filtri range in Qdrant
        year_raw = pf(paper, "anno", "year")
        try:
            year_val = int(year_raw)
        except (ValueError, TypeError):
            year_val = year_raw
        metas.append({
            "source_type": SOURCE_PRISMA,
            "title":       pf(paper, "titolo", "title")[:500],
            "authors":     pf(paper, "autori", "authors")[:300],
            "year":        year_val,
            "doi":         pf(paper, "doi"),
            "source_db":   pf(paper, "source_db"),
        })

    embeddings = _embed_docs(docs, model_cfg)
    backend.upsert(COLLECTION_PRISMA, docs, embeddings, ids, metas)

    cfg["indexed_with"] = cfg.get("model_key", DEFAULT_MODEL_KEY)
    _save_config(cfg)
    print(f"Indicizzati {len(docs)} paper PRISMA in '{COLLECTION_PRISMA}'")


# ── INDEX PDF ─────────────────────────────────────────────────────────────────

def _chunk_text(text: str, size: int = CHUNK_SIZE) -> list:
    words = text.split()
    chunks, current, current_len = [], [], 0
    for word in words:
        current.append(word)
        current_len += len(word) + 1
        if current_len >= size:
            chunk = " ".join(current)
            if len(chunk.strip()) > 50:
                chunks.append(chunk)
            current, current_len = [], 0
    if current:
        chunk = " ".join(current)
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
    return chunks


def op_index_pdf_folder(folder: str):
    try:
        import fitz
    except ImportError:
        print("pymupdf non installato. Esegui: py hybrid_rag.py init")
        sys.exit(1)

    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"Cartella non trovata: {folder}")
        sys.exit(1)

    pdfs = sorted(set(folder_path.rglob("*.pdf")))
    if not pdfs:
        print(f"Nessun PDF trovato in: {folder}")
        return

    cfg = _load_config()
    model_cfg = _active_model_cfg(cfg)
    backend = _get_backend(cfg)
    print(f"Modello: {model_cfg['label']}")

    total_chunks = 0

    for pdf_path in pdfs:
        try:
            pages_text = []
            with fitz.open(str(pdf_path)) as doc:
                for page_num, page in enumerate(doc, start=1):
                    pages_text.append((page_num, page.get_text()))

            full_text = "\n".join(t for _, t in pages_text)
            if len(full_text.strip()) < 100:
                print(f"  {pdf_path.name}: testo insufficiente, saltato")
                continue

            chunks = _chunk_text(full_text)
            stem = pdf_path.stem[:50]

            running = 0
            page_boundaries = []
            for pnum, ptxt in pages_text:
                running += len(ptxt)
                page_boundaries.append((running, pnum))

            chunk_pages = _assign_pages(chunks, page_boundaries)
            ids_c   = [f"{stem}_chunk_{j}" for j in range(len(chunks))]
            metas_c = [
                {
                    "source_type":  SOURCE_PDF,
                    "filename":     pdf_path.name,
                    "chunk_index":  j,
                    "total_chunks": len(chunks),
                    "page":         chunk_pages[j],
                }
                for j in range(len(chunks))
            ]

            embeddings_c = _embed_docs(chunks, model_cfg)
            backend.upsert(COLLECTION_PDF, chunks, embeddings_c, ids_c, metas_c)
            total_chunks += len(chunks)
            print(f"  {pdf_path.name}: {len(chunks)} chunk")

        except Exception as e:
            print(f"  {pdf_path.name}: errore — {e}")

    print(f"\nPDF indicizzati: {len(pdfs)} file, {total_chunks} chunk in '{COLLECTION_PDF}'")


# ── QUERY (Hybrid: Dense + BM25 + RRF) ───────────────────────────────────────

def op_query(
    query: str,
    n_results: int = 5,
    use_prisma: bool = True,
    use_pdf: bool = True,
    filter_str: Optional[str] = None,
):
    collections_to_search = []
    if use_prisma:
        collections_to_search.append(COLLECTION_PRISMA)
    if use_pdf:
        collections_to_search.append(COLLECTION_PDF)

    if not collections_to_search:
        print("Nessuna collezione selezionata.")
        return

    cfg = _load_config()
    active_key   = cfg.get("model_key", DEFAULT_MODEL_KEY)
    indexed_with = cfg.get("indexed_with")
    if indexed_with and indexed_with != active_key:
        print(f"AVVISO: modello attivo '{active_key}' diverso da quello usato per indicizzare '{indexed_with}'.")
        print("Considera di re-indicizzare con il modello attivo.")

    backend    = _get_backend(cfg)
    model_cfg  = _active_model_cfg(cfg)
    query_emb  = _embed_query(query, model_cfg)

    # Filtro Qdrant (ignorato su ChromaDB)
    qdrant_filter = None
    if filter_str:
        if backend.name() == BACKEND_QDRANT:
            qdrant_filter = _parse_qdrant_filter(filter_str)
        else:
            print("AVVISO: --filter è supportato solo con backend qdrant, verrà ignorato.")

    # 1. Dense search
    dense_map: dict = {}
    dense_ranked: list = []
    for coll in collections_to_search:
        for hit in backend.search(coll, query_emb, n_results * DENSE_FETCH_MULTIPLIER, qdrant_filter):
            dense_map[hit["id"]] = hit
            dense_ranked.append((hit["id"], hit["score"]))
    dense_ranked.sort(key=lambda x: x[1], reverse=True)

    # 2. BM25 search
    all_docs = []
    for coll in collections_to_search:
        all_docs.extend(backend.get_all(coll))

    if not all_docs:
        print("Nessun documento indicizzato. Esegui index-prisma o index-pdf prima.")
        return

    from rank_bm25 import BM25Okapi
    tokenized_corpus = [d["text"].lower().split() for d in all_docs]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(query.lower().split())

    bm25_ranked = sorted(
        [(all_docs[i]["id"], float(bm25_scores[i])) for i in range(len(all_docs))],
        key=lambda x: x[1], reverse=True,
    )[:n_results * DENSE_FETCH_MULTIPLIER]

    all_docs_map = {d["id"]: d for d in all_docs}
    for doc_id, _ in bm25_ranked:
        if doc_id not in dense_map:
            doc_data = all_docs_map.get(doc_id)
            if doc_data:
                dense_map[doc_id] = {**doc_data, "score": 0.0}

    # 3. RRF + output
    merged = _rrf_merge([dense_ranked, bm25_ranked], k=RRF_K)

    results = []
    for rank, (doc_id, rrf_score) in enumerate(merged[:n_results], 1):
        data = dense_map.get(doc_id, {})
        results.append({
            "rank":        rank,
            "rrf_score":   round(rrf_score, 4),
            "dense_score": round(data.get("score", 0.0), 4),
            "text":        data.get("text", ""),
            "meta":        data.get("meta", {}),
            "collection":  data.get("collection", ""),
        })

    backend_label = f"{backend.name()}"
    if filter_str and qdrant_filter:
        backend_label += f" · filtro: {filter_str}"
    print(_format_md(query, results, model_cfg["label"], backend_label))


def _format_md(query: str, results: list, model_label: str, backend_label: str) -> str:
    lines = [
        f"## Risultati RAG — Query: `{query}`",
        f"*{len(results)} risultati · Hybrid RAG (Dense + BM25 + RRF) · {model_label} · {backend_label}*",
        "",
    ]
    for r in results:
        meta        = r["meta"]
        source_type = meta.get("source_type", "")

        if source_type == SOURCE_PRISMA:
            header   = (
                f"### [{r['rank']}] {meta.get('authors', 'N/D')} "
                f"({meta.get('year', '')}) — {meta.get('title', '')}"
            )
            doi_line = f"**DOI:** {meta.get('doi', 'N/D')}"
            fonte    = "PRISMA JSON"
        else:
            chunk_n   = meta.get("chunk_index", 0) + 1
            chunk_tot = meta.get("total_chunks", "?")
            page      = meta.get("page", "?")
            header    = f"### [{r['rank']}] {meta.get('filename', 'PDF')} (chunk {chunk_n}/{chunk_tot}, p. {page})"
            doi_line  = ""
            fonte     = "PDF manuale"

        lines.append(header)
        lines.append(
            f"**Score RRF:** {r['rrf_score']} | **Dense:** {r['dense_score']} | **Fonte:** {fonte}"
        )
        if doi_line:
            lines.append(doi_line)
        lines.append("")
        preview = r["text"][:800].replace("\n", " ").strip()
        lines.append(f"> {preview}…")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# ── STATUS ────────────────────────────────────────────────────────────────────

def op_status():
    cfg         = _load_config()
    active_key  = cfg.get("model_key", DEFAULT_MODEL_KEY)
    indexed_key = cfg.get("indexed_with", "—")
    backend_key = cfg.get("backend", BACKEND_CHROMA)
    m = _active_model_cfg(cfg)

    try:
        backend = _get_backend(cfg)
        coll_names = backend.list_collections()
    except Exception as e:
        print(f"Errore apertura backend '{backend_key}': {e}\nEsegui prima: py hybrid_rag.py init")
        return

    lines = [
        "## Stato Hybrid RAG",
        f"**DB:** {RAG_DIR}/  **Backend:** {backend_key}",
        f"**Modello attivo:** {active_key} — {m['label']} (dim={m['dim']})",
        f"**RAM stimata:** ~{m['ram_mb']} MB | **Disco modello:** ~{m['disk_mb']} MB",
        f"**Indicizzato con:** {indexed_key}",
    ]
    if indexed_key != "—" and indexed_key != active_key:
        lines.append("⚠️  Modello attivo diverso da quello usato per indicizzare — re-indicizza prima di fare query.")
    lines.append("")

    if not coll_names:
        lines.append("*Nessuna collezione. Esegui `init`.*")
    for name in coll_names:
        n = backend.count(name)
        t = _fmt_time(m["index_s_per_paper"] * n) if n > 0 else "—"
        lines.append(f"- **{name}**: {n} documenti  *(re-indicizzazione stimata: {t})*")

    if backend_key == BACKEND_QDRANT:
        lines.append("")
        lines.append("Filtri disponibili: `py hybrid_rag.py query '...' --filter 'year>=2020,source_db=eric'`")

    print("\n".join(lines))


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Hybrid RAG — ricerche accademiche (Dense + BM25 + RRF)"
    )
    sub = parser.add_subparsers(dest="op")

    sub.add_parser("init", help="Installa dipendenze e inizializza il DB")

    p_cb = sub.add_parser("choose-backend", help="Seleziona backend vettoriale (chromadb / qdrant)")
    p_cb.add_argument("--backend", default=None,
                      help="Imposta direttamente senza prompt (chromadb / qdrant)")

    p_cm = sub.add_parser("choose-model", help="Seleziona modello embedding")
    p_cm.add_argument("--n-papers", type=int, default=None,
                      help="Numero paper previsti — mostra stime tempi/hardware")
    p_cm.add_argument("--model", default=None,
                      help="Imposta direttamente senza prompt (minilm / e5-large / bge-m3)")

    p_ip = sub.add_parser("index-prisma", help="Indicizza paper da JSON PRISMA")
    p_ip.add_argument("json_file", help="Percorso file JSON (eligibility_prisma.json, ecc.)")

    p_ipdf = sub.add_parser("index-pdf", help="Indicizza PDF da cartella")
    p_ipdf.add_argument("folder", help="Percorso cartella contenente i PDF")

    p_q = sub.add_parser("query", help="Ricerca ibrida nel RAG")
    p_q.add_argument("query_text", nargs="+", help="Testo della query")
    p_q.add_argument("--n", type=int, default=5, help="Numero risultati (default 5)")
    p_q.add_argument("--only-prisma", action="store_true", help="Cerca solo in PRISMA papers")
    p_q.add_argument("--only-pdf",    action="store_true", help="Cerca solo in PDF manuali")
    p_q.add_argument("--filter", dest="filter_str", default=None,
                     help="Filtro metadati Qdrant: 'year>=2020,source_db=eric' (solo backend qdrant)")

    sub.add_parser("status", help="Mostra stato DB, modello e backend attivi")

    args = parser.parse_args()

    if args.op == "init":
        op_init()
    elif args.op == "choose-backend":
        op_choose_backend(backend_key=args.backend)
    elif args.op == "choose-model":
        op_choose_model(n_papers=args.n_papers, model_key=args.model)
    elif args.op == "index-prisma":
        op_index_prisma(args.json_file)
    elif args.op == "index-pdf":
        op_index_pdf_folder(args.folder)
    elif args.op == "query":
        op_query(
            " ".join(args.query_text),
            n_results=args.n,
            use_prisma=not args.only_pdf,
            use_pdf=not args.only_prisma,
            filter_str=args.filter_str,
        )
    elif args.op == "status":
        op_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
