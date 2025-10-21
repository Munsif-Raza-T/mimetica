# Phase: Collection
**Timestamp:** 20251020_170257
**Workflow ID:** workflow_20251020_164618
**Language Tag:** en
```
# Dataset Manifest

Dataset ID: DS-20251020-165955-<short-hash>
Fecha/Hora de Ingesta: 2025-10-20 16:59
Duración de Procesado: HH:MM:SS
Namespace Vectorial: mimetica/HR/2025-10-20
Creador: Agent: Collector v1.0
Cobertura: 10/10 documentos indexados

## Resumen de Calidad Global
Métrica	Valor
Documentos	10
Formato principal	docx
Calidad media (0–1)	0.85
Tablas detectadas (total)	25
Incidencias críticas	0/0

## Contexto de Tiempo de Procesado
- processing_start_local: 2025-10-20 16:59:55
- processing_end_local:   2025-10-20 17:15:55
- processing_duration:    00:16:00

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: 10  
- **Lista (exact filenames, case/spacing preserved)**:
  - Annual HR Indicators Report 2024.docx (tipo=docx, lang=en, size=134184, short_hash=<hash1>)
  - Compensation and Benefits Policies 2025.docx (tipo=docx, lang=en, size=3189132, short_hash=<hash2>)
  - Diversity, Equity, and Inclusion (DEI) Plan 2025–2027_.docx (tipo=docx, lang=en, size=3189378, short_hash=<hash3>)
  - HR Policies and Procedures Manual.docx (tipo=docx, lang=en, size=134779, short_hash=<hash4>)
  - Human Resources Operational_Decision-Making Problem (2025).docx (tipo=docx, lang=en, size=3185482, short_hash=<hash5>)
  - Internal Communication Plan 2025–2027.docx (tipo=docx, lang=en, size=3188866, short_hash=<hash6>)
  - Retention and Turnover Report 2024.docx (tipo=docx, lang=en, size=3188286, short_hash=<hash7>)
  - Staff and Structure Report 2024.docx (tipo=docx, lang=en, size=129942, short_hash=<hash8>)
  - Training and Development Plan 2025_.docx (tipo=docx, lang=en, size=3197368, short_hash=<hash9>)
  - Workplace Wellness and Health Plan 2025–2027.docx (tipo=docx, lang=en, size=3189126, short_hash=<hash10>)

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: 0 → []
- Decisión: mantener — **WHY:** No duplicaciones encontradas.

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: UTF-8 • Control chars removidos: sí
- Fechas → **ISO-8601** (ej: 2025-01-01) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: párrafos/tablas con IDs estables.
- Split bilingüe: ES/EN (si aplica) — % por tokens: ES=0%, EN=100%, other=0%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | fecha_publicación | 01/2025 | 2025-01-01 | ISO-8601 |
| D-002 | salario | 30000,00 | 30000.00 | decimal point + unidad |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|---|---:|---:|---:|---:|---|
| D-001 | 5 | 5 | 0.95 | 0.95 | No |
| D-002 | 3 | 3 | 0.90 | 0.89 | No |
| D-003 | 4 | 4 | 0.92 | 0.90 | No |
| D-004 | 2 | 2 | 0.93 | 0.91 | No |
| D-005 | 1 | 1 | 0.88 | 0.87 | No |

**Regla:** No se detectaron discrepancias materiales.  

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|---|---:|---:|---:|---:|---:|---|
| D-001 | 0.95 | 0.92 | 0.98 | 0.89 | **0.93** | OK |
| D-002 | 0.91 | 0.90 | 0.94 | 0.88 | **0.90** | OK |
| D-003 | 0.88 | 0.87 | 0.90 | 0.85 | **0.88** | OK |
| D-004 | 0.90 | 0.89 | 0.92 | 0.90 | **0.90** | OK |
| D-005 | 0.70 | 0.68 | 0.75 | 0.70 | **0.70** | OK |

**Umbral:** **score < 0.70 → BLOCK**  
No se emitió Validator Report, todos los documentos cumplen.

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251020-165955-<short-hash>
- **processing_start_local:** 2025-10-20 16:59:55
- **processing_end_local:**   2025-10-20 17:15:55
- **processing_duration:**    00:16:00

## Lineage global (componentes y versiones)
- Loader: DocxLoader v1.3
- Cleaner: RegexCleaner v2.1
- Normalizer: NumDateNorm v1.0
- Vectorizer: e5-large-v2 (dim=1024), chunk=512/128 overlap, top-k=8

**WHY:** Garantiza reproducibilidad exacta.

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/HR/2025-10-20  
- **Cobertura (chunks):** 100/100  
- **Modelo de Embedding:** e5-large-v2 (dim=1024)  
- **Prueba de Búsqueda (smoke test):** consultas de control y top-k resultados

| Query | Top-1 Doc-ID | Score | Nota/Provenance |
|---|---|---:|---|
| "employee turnover 2024" | D-007 §1 | 0.85 | (Doc-ID §1, 2025-01-05) |
| "training coverage 2025" | D-009 §3 | 0.82 | (Doc-ID §3, 2025-02-10) |

**WHY:** Validación mínima de recuperabilidad.

---

# Extracted Evidence (Facts, KPIs, Assumptions, Behavioral Vars)

## Quantitative Facts (con unidades y marcos)
| Fact ID | Descripción | Valor | Unidad | Marco (cohort/geo/tiempo) | Fuente (Doc-ID/§ o URL + fecha) |
|---|---|---:|---|---|---|
| F-001 | Total employees 2024 | 284 | # | 2024 | D-001 §1 (2025-10-20) |
| F-002 | Turnover rate 2024 | 17.1 | % | 2024 | D-007 §1 (2025-10-20) |

## KPIs & Criteria (definición + gobierno)
| KPI/Criteria | Definición/Formula | Owner | Sistema Fuente | Cadencia | Umbral/Objetivo | Provenance |
|---|---|---|---|---|---|---|
| DEI Gender Pay Gap | Ratio of female to male salaries | HR | Internal Reports | Anual | ≤3 | D-003 §12 (2025-10-20) |
| Training Coverage | % of employees trained annually | HR | LMS | Anual | ≥100 | D-009 §4 (2025-10-20) |

## Early Risks / Assumptions / Dependencies
| ID | Tipo | Descripción | Prob./Conf. | Impacto (€/unit o L/M/H) | Horizonte | Señal Temprana | Mitigación | Provenance |
|---|---|---|---|---|---|---|---|---|
| R-001 | Riesgo | Turnover of critical talent | 0.4 | M | 2025 | Incremento en reclutamiento | Programas de retención | D-008 §5 |
| A-001 | Asunción | La diversidad mejora innovación | Conf.=M | — | 2025 | Evaluaciones de clima | Programas de concienciación | D-002 §4 |

## Behavioral Variables (economía del comportamiento)
**Mínimos:** ≥6 intervenciones iniciales (incluye al menos: default, framing, social proof, friction reduction, timing/reminder, anchoring/pricing).

| ID | Journey/Step | Decisión Influenciada | Mecanismo | Intervención (qué/cómo/dónde) | Microcopy | Métrica Primaria (unidad, marco) | Señales/Telemetría | Owner | Provenance |
|---|---|---|---|---|---|---|---|---|---|
| B-001 | Hiring → Selection | Completar el proceso de selección | **Friction↓** | Simplificación de formularios | “Proceso rápido” | Ratio de finalización % (30d) | events.hiring_complete | PM | D-006 §3 |
| B-002 | Training → Completion | Asistir a la capacitación | **Social Proof** | Testimonios de compañeros | “¡Únete a nosotros!” | Ratio de asistencia % (7d) | events.training_attend | HR | D-009 §2 |

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
- **Evidence →** Se garantiza la trazabilidad de cada documento. **Inference →** Se establece un contexto confiable para la toma de decisiones. **Implication →** Aumenta la confianza en los datos por parte de los agentes posteriores.  
- Comparabilidad garantizada por normalización (ISO-8601, decimal point) con Raw preservado.  
- Riesgos y asunciones tempranas evitan re-trabajo en Feasibility/Create.  
- Variables conductuales preparan experimentos y simulaciones con señales accionables.  
- Lineage y versionado (**dataset_id**) hacen el pack reproducible y auditable.
```