from crewai import Agent
from tools.custom_tools import AdvancedPineconeVectorSearchTool, SessionDirectoryReadTool, SessionFileReadTool
from config import config
import streamlit as st
import time
from datetime import datetime
from config import get_language
language_selected = get_language()


class CollectorAgent:
    """Agent responsible for data collection, cleaning, and vectorization"""
    @staticmethod
    def create_agent():
        # Get current model configuration with validation
        selected_model = config.validate_and_fix_selected_model()
        model_config = config.AVAILABLE_MODELS[selected_model]
        provider = model_config['provider']
        
        # Set up LLM based on provider
        llm = None
        if provider == 'openai':
            from crewai.llm import LLM
            llm = LLM(
                model=f"openai/{selected_model}",
                api_key=config.OPENAI_API_KEY,
                temperature=config.TEMPERATURE
            )
        elif provider == 'anthropic':
            from crewai.llm import LLM
            llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=config.ANTHROPIC_API_KEY,
                temperature=config.TEMPERATURE
            )
        # --- Tools (core + optionals if available) ---
        tools_list = []
        try:
            from tools.custom_tools import (
                SessionDirectoryReadTool,
                SessionFileReadTool,
                MarkdownFormatterTool,
                CodeInterpreterTool,
                AdvancedPineconeVectorSearchTool,
            )

            tools_list = [
                SessionDirectoryReadTool(),
                SessionFileReadTool(),
                MarkdownFormatterTool(),
                CodeInterpreterTool(),
                AdvancedPineconeVectorSearchTool(),
            ]

            optional_names = [
                "PDFTableExtractorTool",
                "HTML2TextTool",
                "SourceCredibilityTool",
                "DeduplicateSnippetsTool",
                "CitationWeaverTool",
                "DataCleanerTool",
                "EntityResolutionTool",
                "KPIExtractorTool",
                "TrendDetectorTool",
                "NewsTimelineTool",
            ]
            import importlib
            ct = importlib.import_module("tools.custom_tools")
            for name in optional_names:
                cls = getattr(ct, name, None)
                if cls:
                    try:
                        tools_list.append(cls())
                    except TypeError:
                        tools_list.append(cls(**{}))
        except Exception:
            try:
                from tools.custom_tools import (
                    SessionDirectoryReadTool,
                    SessionFileReadTool,
                    AdvancedPineconeVectorSearchTool,
                )
                tools_list = [
                    SessionDirectoryReadTool(),
                    SessionFileReadTool(),
                    AdvancedPineconeVectorSearchTool(),
                ]
            except Exception:
                tools_list = []

        _seen, _dedup = set(), []
        for _t in tools_list:
            _name = getattr(_t, "name", getattr(_t, "__name__", repr(_t)))
            if _name not in _seen:
                _seen.add(_name)
                _dedup.append(_t)
        tools_list = _dedup

        return Agent(
            role="Data Intake & Provenance Orchestrator (DECIDE › Collect) — normalizes, enriches, versions, and audits all inputs to establish the single source of truth for the flow.",
            goal=(
"Establish a versioned, auditable **Context Pack v1** for the session by: (1) discovering and ingesting every uploaded/linked artifact; "
"(2) cleaning and normalizing text/tables with ISO-8601 dates and decimal point while preserving a **Raw** column; "
"(3) assigning per-document **quality_score [0–1]** and blocking progression if any < 0.70 with a validator report; "
"(4) recording complete **lineage** (loader→cleaner→normalizer→vectorizer + versions); "
"(5) computing **dataset_id** and **processing_duration**; "
"(6) generating a bilingual split (ES/EN) when applicable; "
"(7) detecting OCR↔parser table conflicts and flagging **manual review**; "
"(8) vectorizing into a declared **namespace** and proving 100% coverage; "
"(9) extracting quantitative facts with **units** and **timeframes**, KPIs (owner/system/cadence), criteria, risks, assumptions, and initial behavioral variables; "
"and (10) emitting a markdown **Dataset Manifest** exactly as the template requires, plus machine-readable CSV/JSON summaries for downstream agents."
            ),
            backstory=(
"You operate as the first mile of DECIDE: the **intake and provenance layer**. Nothing moves forward unless the inputs are "
"complete, comparable, and traceable. You treat every artifact (PDF, DOCX, XLSX/CSV, HTML/URL, pasted notes) as evidence that "
"must be normalized, scored, and versioned.\n\n"

"Your workflow is disciplined:\n"
"• **Discovery & Triage** — enumerate all session-scoped files/URLs; de-duplicate (hash/near-duplicate); tag type and domain (Market/CX/Finance/Tech/Ops).\n"
"• **Cleaning & Normalization** — remove boilerplate noise, unify encodings, standardize **dates (ISO-8601)** and **numbers (decimal point)** while keeping a **Raw** column; "
"split **ES/EN** content into subsections when mixed. Record exact rules and tool versions.\n"
"• **Tables & OCR Reliability** — reconcile table extraction from OCR vs. parser; if mismatches persist, mark **manual_review:true** with the affected spans and proceed conservatively.\n"
"• **Quality & Validators** — compute per-document **quality_score [0–1]** (signal/noise, completeness, parse confidence, structure integrity). "
"If any score < **0.70**, **stop advancement**, emit a validator report (which docs failed, why, and how to fix) and publish partial manifest.\n"
"• **Lineage & Versioning** — stamp **dataset_id** (DS-YYYYMMDD-HHMM-<short-hash>), **processing_start/end**, **processing_duration**, and full lineage "
"(loader→cleaner→normalizer→vectorizer with semantic versions and parameters). Nothing is implicit; everything is explainable.\n"
"• **Vectorization & Namespace** — index to a stable **namespace** (e.g., `mimetica/<domain>/YYYY-MM-DD`), document embedding model and top-k policy, "
"and confirm **100% coverage** with counts and hashes.\n"
"• **Evidence Pack** — extract quantitative facts (value + **unit** + **timeframe/geo/cohort** + source + access date), KPIs (definition/formula, owner, source system, cadence), "
"decision criteria (locked/target/candidate), early risks/assumptions/dependencies, and a minimal **behavioral baseline** (friction, defaults, framing, social proof, etc.) with linked metrics.\n\n"

"Operating principles you never compromise on:\n"
"1) **Traceability** — every material item carries provenance (Doc-ID/§ or URL + access date) and tool lineage.\n"
"2) **Comparability** — declare or enforce normalization (FX/CPI/PPP), definitions, and windows; flag non-comparable data.\n"
"3) **Safety & Licensing** — respect ToS and licenses; when unclear, summarize rather than copy; mark restricted reuse.\n"
"4) **Determinism** — produce a **Dataset Manifest** that is reproducible, with the exact template and all mandatory fields populated.\n"
"5) **Gatekeeping** — if quality is below bar, you do not let the system advance; instead, you provide a fix-forward plan.\n\n"

"The result is a session-scoped **Context Pack v1** that downstream agents (Explore, Create, Implement, Simulate, Evaluate) can trust blindly: "
"versioned, normalized, bilingual when needed, 100% indexed under a clear namespace, with quality scores, lineage, and a complete manifest."

f"You receive all the info in the selected language: **{language_selected}**."
f"Give your output and ensure all outputs respect the selected language: **{language_selected}**."
            ),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm,
            memory=False,
            cache=False,
        )

    @staticmethod
    def create_task(documents_info: str, agent, **kwargs):
        from crewai import Task
        
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")
        description = f"""
DECIDE › Collect — Establish a versioned, auditable **Context Pack v1** that becomes the single source of truth for the session.

**Time anchor (local):** {current_timestamp}  
**Date (local):** {current_date}

You must: (1) discover and enumerate ALL session-scoped artifacts; (2) clean & normalize (ISO-8601 dates, decimal point numbers) while preserving a **Raw** column;
(3) compute a per-document **quality_score [0–1]** and STOP progression if any < 0.70 (emit validator report); (4) record full **lineage** (loader→cleaner→normalizer→vectorizer with versions);
(5) compute **dataset_id** and **processing_duration**; (6) split bilingual content into **ES/EN** subsections when applicable; (7) reconcile OCR vs parser table extraction and mark **manual_review** when mismatched;
(8) index 100% of documents into a declared **namespace**; (9) extract decision-grade evidence with **units** and **timeframes**, KPIs (owner/system/cadence), early risks/assumptions,
and initial **behavioral variables** (friction, defaults, framing, social proof, timing, commitment, anchoring); (10) emit a Markdown **Dataset Manifest** exactly as per template below PLUS machine-readable CSV/JSON summaries.
(9) Give your output and ensure all outputs respect the selected language: **{language_selected}**.
────────────────────────────────────────────────────────────────────────────────────────
INPUTS (verbatim)
- Documents to process (session scope):
{documents_info}

- Time context (must be used in outputs):
  • processing_start_local = {current_timestamp}  
  • processing_date_local  = {current_date}  
  • processing_end_local   = when finished  
  • Use start/end to compute **processing_duration** (HH:MM:SS).

────────────────────────────────────────────────────────────────────────────────────────
SCOPE OF WORK (DO IN ORDER; KEEP HEADINGS IN OUTPUT)

A) Discovery & Inventory
- Enumerate every uploaded file/URL in this session; list filenames EXACTLY as provided (case/spacing preserved).
- De-duplicate by short-hash; mark near-duplicates if sim ≥ 0.95.
- Classify type (pdf/docx/xlsx/csv/html/txt), domain hint (Market/CX/Finance/Tech/Ops), and language(s).

B) Cleaning & Normalization (with Reproducibility)
- Remove boilerplate noise, fix encodings, strip control chars.
- Normalize dates to **ISO-8601** and numbers to **decimal point**; keep original values in a **Raw** column for any field altered.
- Paragraph & table segmentation; ensure stable IDs for tables and blocks.
- If mixed language in one file, split content into **ES** and **EN** subsections (others keep as-is with code ‘other’). Show % split by tokens.
- Record cleaning/normalization rules and tool versions used.

C) Tables & OCR Reliability
- Extract tables via parser; if OCR is used, extract via OCR too. If table structures disagree materially, set **manual_review:true** and list affected page/section IDs.
- Count tables per document; record parser confidence / OCR confidence if available.

D) Quality Scoring & Validators
- Compute **quality_score [0–1]** per document using signal/noise, parse confidence, completeness, structural integrity, readability.
- If any **quality_score < 0.70**, DO NOT advance; emit a **Validator Report**: which docs failed, why, suggested fixes, and blocking flag. Still publish manifest with coverage status.

E) Lineage & Versioning
- Compute **dataset_id** in the format **DS-YYYYMMDD-HHMM-<short-hash>** (hash over ordered file list + sizes + first 1KB contents).
- Record **processing_start_local** = {current_timestamp}, **processing_end_local** = <finish time>, and **processing_duration** (HH:MM:SS).
- Record lineage per document: **loader → cleaner → normalizer → vectorizer** (component name + semver + key params).
- Record tool versions (e.g., DocxLoader v1.3; RegexCleaner v2.1; NumDateNorm v1.0; e5-large-v2 dim=1024).

F) Vectorization & Namespace
- Define namespace pattern **mimetica/<domain>/YYYY-MM-DD**; if domain mixed, use **mimetica/mixed/YYYY-MM-DD**.
- Vectorize 100% of documents; record embedding model, dim, chunk policy, top-k default.
- Prove coverage: count of chunks vs expected (pages/tokens), and per-file status == “indexed”.

G) Evidence Extraction (for downstream agents)
- Extract **quantitative facts** as: value + **unit** + **timeframe/geo/cohort** + **source** + **access date**. Examples: “Churn = 3.2%/month (ES SMB cohort, 2024Q3) — Source Doc-ID §2”.
- Extract initial **KPIs**: definition/formula, owner, source system, cadence; and decision **criteria** (locked/target/candidate).
- Extract early **risks/assumptions/dependencies** (short form).
- Extract initial **behavioral variables** where visible (friction: steps/clicks/fields; defaults; framing cues; social proof; timing; commitment; anchoring/pricing patterns), and link them to measurable signals (which event/metric).

H) Output Artifacts
- Emit **Dataset Manifest** (Markdown) EXACTLY as the template below.
- Emit machine-readable **documents.csv/json** and **facts_kpis.csv/json** with: doc_id, filename, short_hash, lang_primary, tokens, tables, normalized_flags, quality_score, status, lineage fields, and extracted evidence items (fact/kpi with units, timeframes, provenance).

I) Post-conditions (must hold unless blocked by validators)
- 100% documents have status **indexed** (or explicit block with reasons).
- **dataset_id** present and correctly formed.
- **processing_duration** computed from start/end above.
- All **quality_score ≥ 0.70**; otherwise you must set a blocking flag and include Validator Report.
- **namespace** consistent with rule above.

────────────────────────────────────────────────────────────────────────────────────────
PASTE THIS EXACT TEMPLATE IN YOUR OUTPUT (fill all fields)

Dataset Manifest

Dataset ID: DS-YYYYMMDD-HHMM-<short-hash>
Fecha/Hora de Ingesta: YYYY-MM-DD HH:MM (local)
Duración de Procesado: HH:MM:SS
Namespace Vectorial: mimetica/<domain>/YYYY-MM-DD
Creador: Agent: Collector vX.Y
Cobertura: <processed>/<total> documentos indexados

Resumen de Calidad Global
Métrica\tValor
Documentos\t<N>
Formato principal\t<pdf/docx/...>
Calidad media (0–1)\t<0.00>
Tablas detectadas (total)\t<N>
Incidencias críticas\t<0/…>

Lista de Documentos
#\tFilename\tHash (corto)\tLang Primaria\tTokens\tTablas\tFechas/Números Normalizados\tQuality Score\tStatus
1\t<exact filename>\t<9af23…>\t<es/en>\t<28437>\t<12>\t<Sí/No>\t<0.94>\t<indexed|blocked>
2\t<...>\t<...>\t<...>\t<...>\t<...>\t<...>\t<...>\t<...>
…

Lineage (por documento – ejemplo)
Ruta Origen: <absolute or session path>
Loader: <name vX.Y>
Cleaner: <name vX.Y (flags...)>
Normalizer: <name vX.Y (ISO-8601, decimal point; Raw preserved)>
Vectorizer: <model (dim=), chunking, top-k>

Incidencias y Acciones
Incidencias: <ninguna crítica | resumen>
Acciones tomadas: <reglas aplicadas / exclusiones / manual_review>
Siguiente paso: <Feasibility / Explore / Blocked (see Validator Report)>

────────────────────────────────────────────────────────────────────────────────────────
FORMATTING & TRACEABILITY
- Markdown only; use the headings exactly as specified for the Manifest block.
- Every material claim includes a **provenance cue** (Doc-ID/§ or URL + access date).
- All computed values show **unit** and **timeframe**, and if you normalized, cite rule and source (FX/CPI/PPP).
- Where uncertainty exists, mark **TBD** and add to Validator Report with a collection/fix plan.

────────────────────────────────────────────────────────────────────────────────────────
ACCEPTANCE CHECKLIST (ALL MUST BE YES)
- coverage_100_percent_indexed_or_explicitly_blocked == true
- dataset_id_present == true
- processing_duration_reported == true
- all_quality_scores_≥_0_70_or_block_with_validator_report == true
- namespace_consistent == true
- numbers_and_dates_normalized_with_raw_preserved == true
- ocr_vs_parser_conflicts_marked_manual_review == true
- bilingual_split_es_en_applied_if_applicable == true
- lineage_complete_loader→cleaner→normalizer→vectorizer == true
- manifest_template_pasted_and_fully_filled == true
- extracted_facts_kpis_have_units_timeframes_provenance == true
- behavioral_variables_baseline_listed_with_signals == true

────────────────────────────────────────────────────────────────────────────────────────
TOOLS (IF AVAILABLE; FAIL GRACEFULLY)
- SessionDirectoryReadTool / SessionFileReadTool — discover and read files.
- AdvancedPineconeVectorSearchTool — confirm namespace and index coverage.
If a tool fails, proceed without it and document the fallback under HOW/Incidencias.
"""

        expected_output = """
# Dataset Manifest

Dataset ID: DS-YYYYMMDD-HHMM-<short-hash>
Fecha/Hora de Ingesta: YYYY-MM-DD HH:MM (local)
Duración de Procesado: HH:MM:SS
Namespace Vectorial: mimetica/<domain|mixed>/YYYY-MM-DD
Creador: Agent: Collector vX.Y
Cobertura: <processed>/<total> documentos indexados

## Resumen de Calidad Global
Métrica\tValor
Documentos\t<N>
Formato principal\t<pdf/docx/xlsx/csv/html/txt>
Calidad media (0–1)\t<0.00>
Tablas detectadas (total)\t<N>
Incidencias críticas\t<0/…>

## Contexto de Tiempo de Procesado
- processing_start_local: YYYY-MM-DD HH:MM:SS
- processing_end_local:   YYYY-MM-DD HH:MM:SS
- processing_duration:    HH:MM:SS

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: <N>  
- **Lista (exact filenames, case/spacing preserved)**:
  - <filename.ext> (tipo=<pdf/docx/...>, lang=<es/en/…>, size=<bytes>, short_hash=<xxxxx>)
  - …

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: <N> → [<file A> ~ <file B> (sim=0.97), …]  
- Decisión: <mantener/colapsar> — **WHY:** <evidence → inference → implication>

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: <regla> • Control chars removidos: <sí/no>
- Fechas → **ISO-8601** (ej: 2025-10-13) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: párrafos/tablas con IDs estables.
- Split bilingüe: ES/EN (si aplica) — % por tokens: ES=<x%>, EN=<y%>, other=<z%>

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | fecha_publicación | 13/10/25 | 2025-10-13 | ISO-8601 |
| D-001 | precio | 12.345,67 € | 12345.67 EUR | decimal point + unidad |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|---|---:|---:|---:|---:|---|
| D-001 | 12 | 12 | 0.92 | 0.90 | No |
| D-002 | 7 | 9 | 0.78 | 0.74 | **Sí** (mismatch) |

**Regla:** Si OCR ≠ Parser de forma material → **manual_review:true** y listar páginas/IDs afectadas.  
**WHY:** Las discrepancias de estructura invalidan cálculos si no se revisan.

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|---|---:|---:|---:|---:|---:|---|
| D-001 | 0.94 | 0.92 | 0.98 | 0.88 | **0.93** | OK |
| D-00X | 0.60 | 0.62 | 0.80 | 0.65 | **0.67** | **BLOCK** |

**Umbral:** **score < 0.70 → BLOCK**  
**Validator Report (si aplica):**
- Doc: D-00X — Motivos: <…> — Acciones sugeridas: <…> — Dueño: <…> — ETA: <…>  
**WHY:** Aguas abajo sólo deben consumir evidencia fiable.

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-YYYYMMDD-HHMM-<short-hash>
- **processing_start_local:** YYYY-MM-DD HH:MM:SS
- **processing_end_local:**   YYYY-MM-DD HH:MM:SS
- **processing_duration:**    HH:MM:SS

## Lineage global (componentes y versiones)
- Loader: <DocxLoader v1.3 / PDFMiner vX / …>
- Cleaner: <RegexCleaner v2.1 (flags)>
- Normalizer: <NumDateNorm v1.0>
- Vectorizer: <e5-large-v2 (dim=1024), chunk=512/128 overlap, top-k=8>

**WHY:** Garantiza reproducibilidad exacta.

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/<domain|mixed>/YYYY-MM-DD  
- **Cobertura (chunks):** <indexed>/<expected>  
- **Modelo de Embedding:** <name> (dim=<N>)  
- **Prueba de Búsqueda (smoke test):** consultas de control y top-k resultados

| Query | Top-1 Doc-ID | Score | Nota/Provenance |
|---|---|---:|---|
| "pricing elasticity 2024" | D-003 §4 | 0.83 | (Doc-ID §4, 2024-05-10) |
| "SLA p95 latency" | D-007 §2 | 0.79 | (Doc-ID §2, 2025-01-14) |

**WHY:** Validación mínima de recuperabilidad.

---

# Extracted Evidence (Facts, KPIs, Assumptions, Behavioral Vars)

## Quantitative Facts (con unidades y marcos)
| Fact ID | Descripción | Valor | Unidad | Marco (cohort/geo/tiempo) | Fuente (Doc-ID/§ o URL + fecha) |
|---|---|---:|---|---|---|
| F-001 | Churn mensual ES-SMB 2024Q3 | 3.2 | %/mes | ES, 2024Q3 | D-002 §3 (2024-11-02) |
| F-002 | p95 latency checkout | 320 | ms | prod, 7d | D-007 §2 (2025-01-14) |

**WHY:** Hechos con unidades y marcos permiten ROI/NPV/Payback comparables.

## KPIs & Criteria (definición + gobierno)
| KPI/Criteria | Definición/Formula | Owner | Sistema Fuente | Cadencia | Umbral/Objetivo | Provenance |
|---|---|---|---|---|---|---|
| ROI_12m | (Net Benefits / Investment)×100 | Finanzas | ERP+BI | mensual | ≥10% | D-009 §5 (2024-10-01) |
| SLA_p95 | p95 latency [ms] | SRE | APM | semanal | ≤300 ms | D-007 §2 (2025-01-14) |

**WHY:** Define reglas de decisión y control operativo.

## Early Risks / Assumptions / Dependencies
| ID | Tipo | Descripción | Prob./Conf. | Impacto (€/unit o L/M/H) | Horizonte | Señal Temprana | Mitigación | Provenance |
|---|---|---|---|---|---|---|---|---|
| R-001 | Riesgo | Vendor lead time | 0.4 | L/M/H | 60-90d | backlog > X | 2º proveedor | D-010 §2 |
| A-001 | Asunción | Conversión base = 2.1% | Conf.=M | — | Q1 | SRM OK | test A/B | D-003 §1 |

**WHY:** Anticipa incertidumbres críticas.

## Behavioral Variables (economía del comportamiento)
**Mínimos:** ≥6 intervenciones iniciales (incluye al menos: default, framing, social proof, friction reduction, timing/reminder, anchoring/pricing).

| ID | Journey/Step | Decisión Influenciada | Mecanismo | Intervención (qué/cómo/dónde) | Microcopy | Métrica Primaria (unidad, marco) | Señales/Telemetría | Owner | Provenance |
|---|---|---|---|---|---|---|---|---|---|
| B-001 | Signup → Consent | Completar registro | **Friction↓** | reducir campos 8→4, autocompletar | “Solo 2 minutos” | Completion rate % (7d) | events.signup_submit | PM | D-006 §2 |
| B-002 | Pricing → Select | Elegir plan | **Anchoring** | mostrar plan Pro primero | “Más popular” | Plan mix % (30d) | events.plan_select | Growth | D-005 §3 |

**WHY:** Pequeños cambios en choice architecture pueden mover conversiones y CAC/LTV.

---

# Machine-Readable Artifacts

## documents.csv (o .json)
Campos mínimos:  
`doc_id, filename_exact, short_hash, lang_primary, tokens, tables, normalized_dates_numbers (bool), quality_score, status, manual_review (bool), source_path, loader, cleaner, normalizer, vectorizer, namespace`

## facts_kpis.csv (o .json)
Campos mínimos:  
`item_id, type (fact/kpi/criterion/risk/assumption/dependency/behavioral), description, value, unit, timeframe, cohort_geo, source, access_date, owner, system, cadence, threshold, notes`

**WHY:** Permite a agentes downstream consumir datos sin re-trabajo.

---

# Post-conditions & Checklist

- 100% documentos con **status = indexed** (o **blocked** + Validator Report).
- **dataset_id** presente y bien formado.
- **processing_duration** calculado.
- Todos **quality_score ≥ 0.70**; si no, bloqueo explícito.
- **namespace** consistente (*mimetica/<domain|mixed>/YYYY-MM-DD*).
- Números/fechas normalizados con **Raw** preservado.
- Conflictos OCR vs Parser marcados **manual_review** con detalle.
- Split **ES/EN** aplicado si corresponde (con % por tokens).
- Lineage completo **loader→cleaner→normalizer→vectorizer**.
- Hechos/KPIs con **unidades**, **marcos** y **provenance cues**.
- Variables conductuales con **métrica primaria** y **telemetría**.

---

# WHY (Meta-Rationale, 4–6 bullets)
- **Evidence →** <evidencia clave> **Inference →** <conclusión> **Implication →** <impacto para agentes siguientes>  
- Comparabilidad garantizada por normalización (ISO-8601, decimal point) con Raw preservado.  
- Riesgos y asunciones tempranas evitan re-trabajo en Feasibility/Create.  
- Variables conductuales preparan experimentos y simulaciones con señales accionables.  
- Lineage y versionado (**dataset_id**) hacen el pack reproducible y auditable.
"""

        return Task(
            description= description,
            expected_output= expected_output,
            agent=agent,
            markdown=True,
            output_file="01_document_processing_report.md"
        )
