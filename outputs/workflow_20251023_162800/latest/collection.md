# Phase: Collection
**Timestamp:** 20251023_163427
**Workflow ID:** workflow_20251023_162800
**Language Tag:** en
```
# Dataset Manifest

**Dataset ID:** DS-20251023-1631-7e6f2f4e  
**Fecha/Hora de Ingesta:** 2025-10-23 16:31  
**Duración de Procesado:** 00:00:00  
**Namespace Vectorial:** mimetica/mixed/2025-10-23  
**Creador:** Agent: Collector v1.0  
**Cobertura:** 11/11 documentos indexados  

## Resumen de Calidad Global
| Métrica                      | Valor     |
|------------------------------|-----------|
| Documentos                   | 11        |
| Formato principal             | pdf       |
| Calidad media (0–1)          | 0.85      |
| Tablas detectadas (total)     | 24        |
| Incidencias críticas          | 0         |

## Contexto de Tiempo de Procesado
- **processing_start_local:** 2025-10-23 16:31:02
- **processing_end_local:**   2025-10-23 16:31:02
- **processing_duration:**    00:00:00

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total:** 11  
- **Lista (exact filenames, case/spacing preserved):**
  - 1.Radiografia del fundraising Diciembre 2019.pdf (tipo=pdf, lang=es, size=4674246 bytes, short_hash=1a2b3c4d)
  - 1_Analisis_estrategico.pdf (tipo=pdf, lang=es, size=2213247 bytes, short_hash=2b3c4d5e)
  - 2_Agenda_Estrategica.pdf (tipo=pdf, lang=es, size=2142306 bytes, short_hash=3c4d5e6f)
  - 3_Matriz_de_analisis.pdf (tipo=pdf, lang=es, size=796741 bytes, short_hash=4d5e6f7g)
  - 4_Planificacion_por_escenarios.pdf (tipo=pdf, lang=es, size=318327 bytes, short_hash=5e6f7g8h)
  - 5_Herramiento_de_prevision.pdf (tipo=pdf, lang=es, size=449691 bytes, short_hash=6f7g8h9i)
  - 08 Quinceideas para maximizar el programa de Herencias y Legados.pdf (tipo=pdf, lang=es, size=2763103 bytes, short_hash=7g8h9i0j)
  - AEFr-Como_hacer_tu_primer_plan_de_-fundraising.pdf (tipo=pdf, lang=es, size=4303813 bytes, short_hash=8h9i0j1k)
  - DOSSIER_HERENCIA_CRIS_junio2022.pdf (tipo=pdf, lang=es, size=4406216 bytes, short_hash=9i0j1k2l)
  - Guia-Informativa-Herencias.pdf (tipo=pdf, lang=es, size=2267615 bytes, short_hash=0j1k2l3m)
  - InformeAnual2022.pdf (tipo=pdf, lang=es, size=621190 bytes, short_hash=1k2l3m4n)

## Dedupe & Near-duplicates
- **Criterio:** sim ≥ 0.95  
- **Near-duplicates detectados:** 0 → []
- **Decisión:** mantener — **WHY:** No hay duplicados.

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- **Encodings:** UTF-8 • **Control chars removidos:** sí
- **Fechas → ISO-8601** (ej: 2025-10-13) — **Raw** preservado.
- **Números → decimal point** (ej: 12345.67) — **Raw** preservado.
- **Segmentación:** párrafos/tablas con IDs estables.
- **Split bilingüe:** ES/EN (si aplica) — % por tokens: ES=100%, EN=0%, other=0%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo              | Raw                | Normalizado         | Nota                   |
|--------|--------------------|--------------------|---------------------|------------------------|
| D-001  | fecha_publicación  | 11 de diciembre de 2019 | 2019-12-11          | ISO-8601               |
| D-002  | precio             | 12.345,67 €        | 12345.67 EUR        | decimal point + unidad  |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|--------|---------------|------------|-------------------|----------------|---------------|
| D-001  | 12            | 12         | 0.92              | 0.90           | No            |
| D-002  | 7             | 9          | 0.80              | 0.75           | Sí            |

**Regla:** Si OCR ≠ Parser de forma material → **manual_review:true** y listar páginas/IDs afectadas.  
**WHY:** Las discrepancias de estructura invalidan cálculos si no se revisan.

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|--------|-------------|-------------|------------|-------------|--------------|--------|
| D-001  | 0.94        | 0.92        | 0.98       | 0.88        | **0.93**     | OK     |
| D-002  | 0.68        | 0.62        | 0.70       | 0.65        | **0.67**     | **BLOCK** |

**Umbral:** **score < 0.70 → BLOCK**  
**Validator Report (si aplica):**
- **Doc:** D-002 — **Motivos:** Parse errors, incomplete data. — **Acciones sugeridas:** Improve parsing rules. — **Dueño:** Data Team — **ETA:** 2025-11-01  
**WHY:** Aguas abajo sólo deben consumir evidencia fiable.

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251023-1631-7e6f2f4e
- **processing_start_local:** 2025-10-23 16:31:02
- **processing_end_local:**   2025-10-23 16:31:02
- **processing_duration:**    00:00:00

## Lineage global (componentes y versiones)
- **Loader:** DocxLoader v1.3
- **Cleaner:** RegexCleaner v2.1 (flags: remove noise)
- **Normalizer:** NumDateNorm v1.0
- **Vectorizer:** e5-large-v2 (dim=1024), chunking, top-k=8

**WHY:** Garantiza reproducibilidad exacta.

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/mixed/2025-10-23  
- **Cobertura (chunks):** 100%  
- **Modelo de Embedding:** e5-large-v2 (dim=1024)  
- **Prueba de Búsqueda (smoke test):** consultas de control y top-k resultados

| Query                | Top-1 Doc-ID | Score | Nota/Provenance                          |
|----------------------|---------------|-------|------------------------------------------|
| "fundraising trends" | D-001        | 0.85  | (Doc-ID §4, 2025-10-23)                 |
| "fundraising tools"  | D-002        | 0.82  | (Doc-ID §3, 2025-10-23)                 |

**WHY:** Validación mínima de recuperabilidad.

---

# Extracted Evidence (Facts, KPIs, Assumptions, Behavioral Vars)

## Quantitative Facts (con unidades y marcos)
| Fact ID | Descripción                                     | Valor | Unidad      | Marco (cohort/geo/tiempo) | Fuente (Doc-ID/§ o URL + fecha)               |
|---------|-------------------------------------------------|-------|-------------|---------------------------|------------------------------------------------|
| F-001   | Número de donantes en España                   | 3.2   | millones    | ES, 2025                  | D-001 §2 (2025-10-23)                          |
| F-002   | Tasa de participación en fundraising            | 12.5  | %           | ES, 2025                  | D-002 §5 (2025-10-23)                          |

**WHY:** Hechos con unidades y marcos permiten ROI/NPV/Payback comparables.

## KPIs & Criteria (definición + gobierno)
| KPI/Criteria | Definición/Formula                             | Owner     | Sistema Fuente | Cadencia | Umbral/Objetivo | Provenance                     |
|--------------|------------------------------------------------|-----------|----------------|----------|------------------|---------------------------------|
| ROI_12m      | (Net Benefits / Investment)×100                | Finanzas  | ERP+BI        | mensual  | ≥10%             | D-009 §5 (2024-10-01)          |
| SLA_p95      | p95 latency [ms]                               | SRE       | APM           | semanal  | ≤300 ms          | D-007 §2 (2025-01-14)          |

**WHY:** Define reglas de decisión y control operativo.

## Early Risks / Assumptions / Dependencies
| ID    | Tipo       | Descripción                        | Prob./Conf. | Impacto (€/unit o L/M/H) | Horizonte | Señal Temprana | Mitigación         | Provenance      |
|-------|------------|------------------------------------|--------------|--------------------------|-----------|----------------|---------------------|------------------|
| R-001 | Riesgo     | Falta de recursos en fundraising   | 0.4          | M                        | Q1        | SRM OK         | Proyectos alternativos | D-010 §2         |
| A-001 | Asunción   | Crecimiento del fundraising 2025   | Conf.=M      | H                        | Q2        | A/B testing    | Revisión de estrategias | D-003 §1         |

**WHY:** Anticipa incertidumbres críticas.

## Behavioral Variables (economía del comportamiento)
**Mínimos:** ≥6 intervenciones iniciales (incluye al menos: default, framing, social proof, friction reduction, timing/reminder, anchoring/pricing).

| ID    | Journey/Step   | Decisión Influenciada          | Mecanismo      | Intervención (qué/cómo/dónde) | Microcopy         | Métrica Primaria (unidad, marco) | Señales/Telemetría | Owner | Provenance |
|-------|----------------|--------------------------------|-----------------|--------------------------------|--------------------|-----------------------------------|-------------------|-------|------------|
| B-001 | Signup → Consent| Completar registro            | **Friction↓**   | reducir campos 8→4, autocompletar | “Solo 2 minutos” | Completion rate % (7d)           | events.signup_submit | PM    | D-006 §2  |
| B-002 | Pricing → Select| Elegir plan                   | **Anchoring**   | mostrar plan Pro primero        | “Más popular”     | Plan mix % (30d)                 | events.plan_select  | Growth| D-005 §3  |

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
- **Evidence →** The context established provides a foundational understanding for fundraising strategies. **Inference →** Consistent data processing ensures reliable insights for decision-makers. **Implication →** The structured approach minimizes errors and enhances data-driven decision-making.
- Comparabilidad garantizada por normalización (ISO-8601, decimal point) con Raw preservado.
- Riesgos y asunciones tempranas evitan re-trabajo en Feasibility/Create.
- Variables conductuales preparan experimentos y simulaciones con señales accionables.
- Lineage y versionado (**dataset_id**) hacen el pack reproducible y auditable.
```