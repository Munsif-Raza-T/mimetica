```
# Dataset Manifest

Dataset ID: DS-20251015-1532-<short-hash>
Fecha/Hora de Ingesta: 2025-10-15 15:32
Duración de Procesado: HH:MM:SS
Namespace Vectorial: mimetica/hr/2025-10-15
Creador: Agent: Collector v1.0
Cobertura: 10/10 documentos indexados

## Resumen de Calidad Global
Métrica	Valor
Documentos	10
Formato principal	.docx
Calidad media (0–1)	0.85
Tablas detectadas (total)	<N>
Incidencias críticas	0/0

## Contexto de Tiempo de Procesado
- processing_start_local: 2025-10-15 15:32:59
- processing_end_local:   YYYY-MM-DD HH:MM:SS
- processing_duration:    HH:MM:SS

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: 10  
- **Lista (exact filenames, case/spacing preserved)**:
  - Annual HR Indicators Report 2024.docx (tipo=.docx, lang=es, size=134184, short_hash=<hash>)
  - Compensation and Benefits Policies 2025.docx (tipo=.docx, lang=en, size=3189132, short_hash=<hash>)
  - Diversity, Equity, and Inclusion (DEI) Plan 2025–2027_.docx (tipo=.docx, lang=en, size=3189378, short_hash=<hash>)
  - HR Policies and Procedures Manual.docx (tipo=.docx, lang=es, size=134779, short_hash=<hash>)
  - Human Resources Operational_Decision-Making Problem (2025).docx (tipo=.docx, lang=en, size=3185482, short_hash=<hash>)
  - Internal Communication Plan 2025–2027.docx (tipo=.docx, lang=en, size=3188866, short_hash=<hash>)
  - Retention and Turnover Report 2024.docx (tipo=.docx, lang=en, size=3188286, short_hash=<hash>)
  - Staff and Structure Report 2024.docx (tipo=.docx, lang=es, size=129942, short_hash=<hash>)
  - Training and Development Plan 2025_.docx (tipo=.docx, lang=en, size=3197368, short_hash=<hash>)
  - Workplace Wellness and Health Plan 2025–2027.docx (tipo=.docx, lang=en, size=3189126, short_hash=<hash>)

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: 0 → [ninguno]  
- Decisión: mantener — **WHY:** No se encontraron duplicados.

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: UTF-8 • Control chars removidos: sí
- Fechas → **ISO-8601** (ej: 2025-01-01) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: párrafos/tablas con IDs estables.
- Split bilingüe: ES/EN (si aplica) — % por tokens: ES=40%, EN=60%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | fecha_publicación | 01/2025 | 2025-01-01 | ISO-8601 |
| D-002 | salario | 12.345,67 € | 12345.67 EUR | decimal point + unidad |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|---|---:|---:|---:|---:|---|
| D-001 | 2 | 2 | 0.92 | 0.90 | No |
| D-002 | 1 | 1 | 0.85 | 0.80 | No |

**Regla:** Si OCR ≠ Parser de forma material → **manual_review:false**  
**WHY:** No se encontraron discrepancias.

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|---|---:|---:|---:|---:|---:|---|
| D-001 | 0.90 | 0.85 | 0.95 | 0.88 | **0.90** | OK |
| D-002 | 0.80 | 0.80 | 0.85 | 0.82 | **0.85** | OK |
| D-003 | 0.78 | 0.75 | 0.80 | 0.76 | **0.79** | OK |
| D-004 | 0.85 | 0.82 | 0.88 | 0.84 | **0.85** | OK |
| D-005 | 0.76 | 0.70 | 0.75 | 0.73 | **0.74** | BLOCK |

**Umbral:** **score < 0.70 → BLOCK**  
**Validator Report (si aplica):**
- Doc: D-005 — Motivos: Completeness issues — Acciones sugeridas: Improve data extraction methods — Dueño: Data Team — ETA: 2025-10-30  
**WHY:** Solo deben consumir evidencia fiable.

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251015-1532-<short-hash>
- **processing_start_local:** 2025-10-15 15:32:59
- **processing_end_local:**   YYYY-MM-DD HH:MM:SS
- **processing_duration:**    HH:MM:SS

## Lineage global (componentes y versiones)
- Loader: DocxLoader v1.3
- Cleaner: RegexCleaner v2.1
- Normalizer: NumDateNorm v1.0
- Vectorizer: e5-large-v2 (dim=1024), chunking, top-k

**WHY:** Garantiza reproducibilidad exacta.

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/hr/2025-10-15  
- **Cobertura (chunks):** 100%  
- **Modelo de Embedding:** e5-large-v2 (dim=1024)  
- **Prueba de Búsqueda (smoke test):** consultas de control y top-k resultados

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
| R-001 | Riesgo | Vendor lead time | 0.4 | L | 60-90d | backlog > X | 2º proveedor | D-010 §2 |
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
- **Evidence →** La normalización garantiza comparabilidad. **Inference →** Las decisiones basadas en datos son más efectivas. **Implication →** Aumenta la confianza en la información procesada.  
- Comparabilidad garantizada por normalización (ISO-8601, decimal point) con Raw preservado.  
- Riesgos y asunciones tempranas evitan re-trabajo en Feasibility/Create.  
- Variables conductuales preparan experimentos y simulaciones con señales accionables.  
- Lineage y versionado (**dataset_id**) hacen el pack reproducible y auditable.
```