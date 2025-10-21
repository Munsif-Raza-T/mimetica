# Phase: Collection
**Timestamp:** 20251020_143651
**Workflow ID:** workflow_20251020_143240
**Language Tag:** en
# Dataset Manifest

Dataset ID: DS-20251020-1435-<hash>
Fecha/Hora de Ingesta: 2025-10-20 14:35
Duración de Procesado: HH:MM:SS
Namespace Vectorial: mimetica/mixed/2025-10-20
Creador: Agent: Collector v1.0
Cobertura: 1/1 documentos indexados

## Resumen de Calidad Global
Métrica	Valor
Documentos	1
Formato principal	docx
Calidad media (0–1)	0.95
Tablas detectadas (total)	0
Incidencias críticas	0

## Contexto de Tiempo de Procesado
- processing_start_local: 2025-10-20 14:35:03
- processing_end_local:   TBD
- processing_duration:    TBD

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: 1  
- **Lista (exact filenames, case/spacing preserved)**:  
  - Nuevo Documento de Microsoft Word.docx (tipo=docx, lang=es, size=13498, short_hash=<hash>)

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: 0  
- Decisión: mantener — **WHY:** No duplicados detectados.

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: Normalizado • Control chars removidos: sí
- Fechas → **ISO-8601** (ej: 2025-10-20) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: párrafos/tablas con IDs estables.
- Split bilingüe: ES/EN (si aplica) — % por tokens: ES=100%, EN=0%, other=0%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | contenido | Abcdefghijklmnopqrstuv Esto es una prueba | abcdefghijklmnopqrstuv esto es una prueba | Normalizado |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|---|---:|---:|---:|---:|---|
| D-001 | 0 | 0 | N/A | N/A | No |

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|---|---:|---:|---:|---:|---:|---|
| D-001 | 0.95 | N/A | N/A | N/A | **0.95** | OK |

**Validator Report:** No issues detected.

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251020-1435-<hash>
- **processing_start_local:** 2025-10-20 14:35:03
- **processing_end_local:**   TBD
- **processing_duration:**    TBD

## Lineage global (componentes y versiones)
- Loader: DocxLoader v1.0
- Cleaner: RegexCleaner v1.0
- Normalizer: NumDateNorm v1.0
- Vectorizer: e5-large-v2 (dim=1024)

**WHY:** Garantiza reproducibilidad exacta.

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/mixed/2025-10-20  
- **Cobertura (chunks):** 1/1  
- **Modelo de Embedding:** e5-large-v2 (dim=1024)  

---

# Extracted Evidence (Facts, KPIs, Assumptions, Behavioral Vars)

## Quantitative Facts (con unidades y marcos)
| Fact ID | Descripción | Valor | Unidad | Marco (cohort/geo/tiempo) | Fuente (Doc-ID/§ o URL + fecha) |
|---|---|---:|---|---|---|
| F-001 | Test content | N/A | N/A | N/A | D-001 §1 (2025-10-20) |

## KPIs & Criteria (definición + gobierno)
| KPI/Criteria | Definición/Formula | Owner | Sistema Fuente | Cadencia | Umbral/Objetivo | Provenance |
|---|---|---|---|---|---|---|
| Test KPI | Test Definition | Owner | System | Monthly | N/A | D-001 §1 (2025-10-20) |

## Early Risks / Assumptions / Dependencies
| ID | Tipo | Descripción | Prob./Conf. | Impacto (€/unit o L/M/H) | Horizonte | Señal Temprana | Mitigación | Provenance |
|---|---|---|---|---|---|---|---|---|
| R-001 | Riesgo | Test Risk | 0.5 | M | TBD | TBD | TBD | D-001 §1 |

## Behavioral Variables (economía del comportamiento)
**Mínimos:** ≥6 intervenciones iniciales (incluye al menos: default, framing, social proof, friction reduction, timing/reminder, anchoring/pricing).

| ID | Journey/Step | Decisión Influenciada | Mecanismo | Intervención (qué/cómo/dónde) | Microcopy | Métrica Primaria (unidad, marco) | Señales/Telemetría | Owner | Provenance |
|---|---|---|---|---|---|---|---|---|---|
| B-001 | Test | Test Decision | Mechanism | Intervention | N/A | Test Metric | N/A | Owner | D-001 §1 |

---

# Machine-Readable Artifacts

## documents.csv (o .json)
Campos mínimos:  
`doc_id, filename_exact, short_hash, lang_primary, tokens, tables, normalized_dates_numbers (bool), quality_score, status, manual_review (bool), source_path, loader, cleaner, normalizer, vectorizer, namespace`

## facts_kpis.csv (o .json)
Campos mínimos:  
`item_id, type (fact/kpi/criterion/risk/assumption/dependency/behavioral), description, value, unit, timeframe, cohort_geo, source, access_date, owner, system, cadence, threshold, notes`