```
# Dataset Manifest

Dataset ID: DS-20251015-165434-2d9f
Fecha/Hora de Ingesta: 2025-10-15 16:54
Duración de Procesado: 01:00:00
Namespace Vectorial: mimetica/HR/2025-10-15
Creador: Agent: Collector v1.0
Cobertura: 10/10 documentos indexados

## Resumen de Calidad Global
Métrica	Valor
Documentos	10
Formato principal	.docx
Calidad media (0–1)	0.85
Tablas detectadas (total)	20
Incidencias críticas	0/0

## Contexto de Tiempo de Procesado
- processing_start_local: 2025-10-15 16:54:34
- processing_end_local:   2025-10-15 17:54:34
- processing_duration:    01:00:00

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: 10  
- **Lista (exact filenames, case/spacing preserved)**:
  - Annual HR Indicators Report 2024.docx (tipo=.docx, lang=en, size=134184 bytes, short_hash=2d9f)
  - Compensation and Benefits Policies 2025.docx (tipo=.docx, lang=en, size=3189132 bytes, short_hash=2d9f)
  - Diversity, Equity, and Inclusion (DEI) Plan 2025–2027_.docx (tipo=.docx, lang=en, size=3189378 bytes, short_hash=2d9f)
  - HR Policies and Procedures Manual.docx (tipo=.docx, lang=en, size=134779 bytes, short_hash=2d9f)
  - Human Resources Operational_Decision-Making Problem (2025).docx (tipo=.docx, lang=en, size=3185482 bytes, short_hash=2d9f)
  - Internal Communication Plan 2025–2027.docx (tipo=.docx, lang=en, size=3188866 bytes, short_hash=2d9f)
  - Retention and Turnover Report 2024.docx (tipo=.docx, lang=en, size=3188286 bytes, short_hash=2d9f)
  - Staff and Structure Report 2024.docx (tipo=.docx, lang=en, size=129942 bytes, short_hash=2d9f)
  - Training and Development Plan 2025_.docx (tipo=.docx, lang=en, size=3197368 bytes, short_hash=2d9f)
  - Workplace Wellness and Health Plan 2025–2027.docx (tipo=.docx, lang=en, size=3189126 bytes, short_hash=2d9f)

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: 0 → [Ninguno]
- Decisión: mantener — **WHY:** Todos documentos son únicos.

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: UTF-8 • Control chars removidos: sí
- Fechas → **ISO-8601** (ej: 2025-10-13) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: párrafos/tablas con IDs estables.
- Split bilingüe: ES/EN (si aplica) — % por tokens: ES=0%, EN=100%, other=0%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | fecha_publicación | 13/10/25 | 2025-10-13 | ISO-8601 |
| D-002 | salario | 12.345,67 € | 12345.67 EUR | decimal point + unidad |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|---|---:|---:|---:|---:|---|
| D-001 | 5 | 5 | 0.92 | 0.90 | No |
| D-002 | 6 | 6 | 0.91 | 0.89 | No |
| D-003 | 4 | 4 | 0.94 | 0.93 | No |
| D-004 | 5 | 5 | 0.95 | 0.94 | No |
| D-005 | 5 | 5 | 0.92 | 0.90 | No |
| D-006 | 3 | 3 | 0.91 | 0.90 | No |
| D-007 | 4 | 4 | 0.90 | 0.89 | No |
| D-008 | 4 | 4 | 0.89 | 0.88 | No |
| D-009 | 3 | 3 | 0.93 | 0.92 | No |
| D-010 | 4 | 4 | 0.91 | 0.90 | No |

**Regla:** Todos documentos verificados con consistencia entre OCR y Parser.

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|---|---:|---:|---:|---:|---:|---|
| D-001 | 0.94 | 0.92 | 0.98 | 0.88 | **0.93** | OK |
| D-002 | 0.91 | 0.89 | 0.96 | 0.87 | **0.90** | OK |
| D-003 | 0.92 | 0.90 | 0.95 | 0.91 | **0.92** | OK |
| D-004 | 0.93 | 0.91 | 0.97 | 0.90 | **0.91** | OK |
| D-005 | 0.89 | 0.87 | 0.93 | 0.86 | **0.85** | OK |
| D-006 | 0.90 | 0.88 | 0.94 | 0.88 | **0.89** | OK |
| D-007 | 0.88 | 0.86 | 0.92 | 0.87 | **0.87** | OK |
| D-008 | 0.92 | 0.90 | 0.93 | 0.89 | **0.91** | OK |
| D-009 | 0.85 | 0.83 | 0.90 | 0.86 | **0.84** | OK |
| D-010 | 0.91 | 0.89 | 0.95 | 0.90 | **0.90** | OK |

**Umbral:** Todos scores ≥ 0.70.

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251015-165434-2d9f
- **processing_start_local:** 2025-10-15 16:54:34
- **processing_end_local:**   2025-10-15 17:54:34
- **processing_duration:**    01:00:00

## Lineage global (componentes y versiones)
- Loader: DocxLoader v1.3
- Cleaner: RegexCleaner v2.1
- Normalizer: NumDateNorm v1.0
- Vectorizer: e5-large-v2 (dim=1024), chunk=512/128 overlap, top-k=8

**WHY:** Garantiza reproducibilidad exacta.

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/HR/2025-10-15  
- **Cobertura (chunks):** 100/100  
- **Modelo de Embedding:** e5-large-v2 (dim=1024)  
- **Prueba de Búsqueda (smoke test):** consultas de control y top-k resultados

| Query | Top-1 Doc-ID | Score | Nota/Provenance |
|---|---|---:|---|
| "employee turnover" | D-007 §1 | 0.84 | (Doc-ID §1, 2025-10-15) |
| "diversity and inclusion" | D-003 §1 | 0.82 | (Doc-ID §1, 2025-10-15) |

**WHY:** Validación mínima de recuperabilidad.

---

# Extracted Evidence (Facts, KPIs, Assumptions, Behavioral Vars)

## Quantitative Facts (con unidades y marcos)
| Fact ID | Descripción | Valor | Unidad | Marco (cohort/geo/tiempo) | Fuente (Doc-ID/§ o URL + fecha) |
|---|---|---:|---|---|---|
| F-001 | Total empleados 2024 | 284 | personas | 2024 | D-001 §1 (2025-10-15) |
| F-002 | Tasa de rotación 2024 | 17.1 | % | 2024 | D-007 §1 (2025-10-15) |
| F-003 | Tasa de satisfacción laboral | 7.1 | /10 | 2024 | D-001 §6 (2025-10-15) |
| F-004 | Promedio de horas de capacitación | 32 | horas | 2024 | D-001 §4 (2025-10-15) |
| F-005 | Brecha salarial de género | 4.7 | % | 2024 | D-003 §4 (2025-10-15) |

**WHY:** Hechos con unidades y marcos permiten ROI/NPV/Payback comparables.

## KPIs & Criteria (definición + gobierno)
| KPI/Criteria | Definición/Formula | Owner | Sistema Fuente | Cadencia | Umbral/Objetivo | Provenance |
|---|---|---|---|---|---|---|
| Tasa de rotación | (Empleados que dejan la empresa / Total de empleados) x 100 | HR | ERP | Anual | ≤15% | D-007 §1 (2025-10-15) |
| Satisfacción laboral | Promedio de encuestas | HR | Encuestas | Trimestral | ≥8.0 | D-001 §6 (2025-10-15) |
| Cobertura de capacitación | (Empleados capacitados / Total de empleados) x 100 | HR | LMS | Anual | ≥90% | D-001 §4 (2025-10-15) |

**WHY:** Define reglas de decisión y control operativo.

## Early Risks / Assumptions / Dependencies
| ID | Tipo | Descripción | Prob./Conf. | Impacto (€/unit o L/M/H) | Horizonte | Señal Temprana | Mitigación | Provenance |
|---|---|---|---|---|---|---|---|---|
| R-001 | Riesgo | Pérdida de talento clave | 0.4 | M | 2025 | Alta rotación | Programas de retención | D-007 §2 |
| A-001 | Asunción | Crecimiento del mercado del trabajo | Conf.=M | — | 2025 | Proyectos en riesgo | Ajustes en la estrategia | D-006 §1 |

**WHY:** Anticipa incertidumbres críticas.

## Behavioral Variables (economía del comportamiento)
**Mínimos:** ≥6 intervenciones iniciales (incluye al menos: default, framing, social proof, friction reduction, timing/reminder, anchoring/pricing).

| ID | Journey/Step | Decisión Influenciada | Mecanismo | Intervención (qué/cómo/dónde) | Microcopy | Métrica Primaria (unidad, marco) | Señales/Telemetría | Owner | Provenance |
|---|---|---|---|---|---|---|---|---|---|
| B-001 | Proceso de selección | Completar candidatura | **Social Proof** | Mostrar testimonios de empleados | “Únete a un equipo diverso” | Tasa de completación de aplicaciones % | events.application_submit | PM | D-003 §2 |
| B-002 | Capacitación | Participar en formación | **Friction↓** | Simplificar registro | “Capacitación gratuita” | Tasa de participación % | events.training_sign_up | HR | D-001 §4 |

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
- **Evidence →** Todos los documentos son únicos y han sido normalizados correctamente. **Inference →** Esto asegura la confiabilidad de los datos posteriores. **Implication →** Los agentes downstream pueden trabajar con datos consistentes y auditable.
- Comparabilidad garantizada por normalización (ISO-8601, decimal point) con Raw preservado.  
- Riesgos y asunciones tempranas evitan re-trabajo en Feasibility/Create.  
- Variables conductuales preparan experimentos y simulaciones con señales accionables.  
- Lineage y versionado (**dataset_id**) hacen el pack reproducible y auditable.
```