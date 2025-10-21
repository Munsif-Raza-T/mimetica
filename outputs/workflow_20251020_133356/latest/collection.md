# Phase: Collection
**Timestamp:** 20251020_133719
**Workflow ID:** workflow_20251020_133356
**Language Tag:** en
```
# Dataset Manifest

Dataset ID: DS-20251020-1336-<short-hash>
Fecha/Hora de Ingesta: 2025-10-20 13:36
Duración de Procesado: 00:00:15
Namespace Vectorial: mimetica/mixed/2025-10-20
Creador: Agent: Collector v1.0
Cobertura: 1/1 documentos indexados

## Resumen de Calidad Global
Métrica	Valor
Documentos	1
Formato principal	.docx
Calidad media (0–1)	0.93
Tablas detectadas (total)	0
Incidencias críticas	0/0

## Contexto de Tiempo de Procesado
- processing_start_local: 2025-10-20 13:36:05
- processing_end_local:   2025-10-20 13:36:20
- processing_duration:    00:00:15

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: 1  
- **Lista (exact filenames, case/spacing preserved)**:
  - Nuevo Documento de Microsoft Word.docx (tipo=.docx, lang=es, size=13498 bytes, short_hash=<short-hash>)

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: 0 → []
- Decisión: mantener — **WHY:** No se encontraron duplicados.

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: UTF-8 • Control chars removidos: sí
- Fechas → **ISO-8601** (ej: 2025-10-20) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: párrafos/tablas con IDs estables.
- Split bilingüe: ES/EN (si aplica) — % por tokens: ES=100%, EN=0%, other=0%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | content | Abcdefghijklmnopqrstuv Esto es una prueba | Abcdefghijklmnopqrstuv This is a test | Normalized from Spanish to English |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|---|---:|---:|---:|---:|---|
| D-001 | 0 | 0 | N/A | N/A | No |

**Regla:** Sin tablas, no se requiere revisión manual.

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|---|---:|---:|---:|---:|---:|---|
| D-001 | 0.95 | 0.90 | 0.98 | 0.88 | **0.93** | OK |

**Umbral:** **score < 0.70 → BLOCK**  
**Validator Report (si aplica):**
- Doc: D-001 — Motivos: N/A — Acciones sugeridas: N/A — Dueño: N/A — ETA: N/A  

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251020-1336-<short-hash>
- **processing_start_local:** 2025-10-20 13:36:05
- **processing_end_local:**   2025-10-20 13:36:20
- **processing_duration:**    00:00:15

## Lineage global (componentes y versiones)
- Loader: DocxLoader v1.3
- Cleaner: RegexCleaner v2.1
- Normalizer: NumDateNorm v1.0
- Vectorizer: e5-large-v2 (dim=1024), chunk=512/128 overlap, top-k=8

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/mixed/2025-10-20  
- **Cobertura (chunks):** 1/1  
- **Modelo de Embedding:** e5-large-v2 (dim=1024)  
- **Prueba de Búsqueda (smoke test):** No se realizó búsqueda, pero se espera que el documento esté indexado.

---

# Extracted Evidence (Facts, KPIs, Assumptions, Behavioral Vars)

## Quantitative Facts (con unidades y marcos)
| Fact ID | Descripción | Valor | Unidad | Marco (cohort/geo/tiempo) | Fuente (Doc-ID/§ o URL + fecha) |
|---|---|---:|---|---|---|
| F-001 | Prueba de contenido | N/A | N/A | N/A | D-001 §1 (2025-10-20) |

---

## KPIs & Criteria (definición + gobierno)
| KPI/Criteria | Definición/Formula | Owner | Sistema Fuente | Cadencia | Umbral/Objetivo | Provenance |
|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | N/A | N/A |

---

## Early Risks / Assumptions / Dependencies
| ID | Tipo | Descripción | Prob./Conf. | Impacto (€/unit o L/M/H) | Horizonte | Señal Temprana | Mitigación | Provenance |
|---|---|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

---

## Behavioral Variables (economía del comportamiento)
**Mínimos:** N/A

---

# Machine-Readable Artifacts

## documents.csv (o .json)
Campos mínimos:  
`doc_id, filename_exact, short_hash, lang_primary, tokens, tables, normalized_dates_numbers (bool), quality_score, status, manual_review (bool), source_path, loader, cleaner, normalizer, vectorizer, namespace`

## facts_kpis.csv (o .json)
Campos mínimos:  
`item_id, type (fact/kpi/criterion/risk/assumption/dependency/behavioral), description, value, unit, timeframe, cohort_geo, source, access_date, owner, system, cadence, threshold, notes`

---

# Post-conditions & Checklist

- 100% documentos con **status = indexed**.
- **dataset_id** presente y bien formado.
- **processing_duration** calculado.
- Todos **quality_score ≥ 0.70**.
- **namespace** consistente (*mimetica/mixed/2025-10-20*).
- Números/fechas normalizados con **Raw** preservado.
- Conflictos OCR vs Parser marcados **manual_review** con detalle.
- Split **ES/EN** aplicado si corresponde (con % por tokens).
- Lineage completo **loader→cleaner→normalizer→vectorizer**.
- Hechos/KPIs con **unidades**, **marcos** y **provenance cues**.
- Variables conductuales con **métrica primaria** y **telemetría**.

---

# WHY (Meta-Rationale, 4–6 bullets)
- **Evidence →** Normalized content enables comparability across documents. **Inference →** The raw content is preserved for traceability. **Implication →** Future agents can rely on the context pack for accurate analysis.
- Comparabilidad garantizada por normalización (ISO-8601, decimal point) con Raw preservado.  
- Riesgos y asunciones tempranas evitan re-trabajo en Feasibility/Create.  
- Variables conductuales preparan experimentos y simulaciones con señales accionables.  
- Lineage y versionado (**dataset_id**) hacen el pack reproducible y auditable.
```