# Phase: Collection
**Timestamp:** 20251020_135417
**Workflow ID:** workflow_20251020_135219
**Language Tag:** en
```
# Dataset Manifest

Dataset ID: DS-20251020-1353-<short-hash>
Fecha/Hora de Ingesta: 2025-10-20 13:53
Duración de Procesado: 00:00:00
Namespace Vectorial: mimetica/mixed/2025-10-20
Creador: Agent: Collector vX.Y
Cobertura: 0/1 documentos indexados

## Resumen de Calidad Global
Métrica	Valor
Documentos	1
Formato principal	.docx
Calidad media (0–1)	0.37
Tablas detectadas (total)	0
Incidencias críticas	1/1

## Contexto de Tiempo de Procesado
- processing_start_local: 2025-10-20 13:53:11
- processing_end_local:   2025-10-20 13:53:22
- processing_duration:    00:00:11

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: 1  
- **Lista (exact filenames, case/spacing preserved)**:
  - Nuevo Documento de Microsoft Word.docx (tipo=docx, lang=es, size=13498 bytes, short_hash=<short-hash>)

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: 0 → []
- Decisión: mantener — **WHY:** No se encontraron duplicados.

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: Normalizados • Control chars removidos: sí
- Fechas → **ISO-8601** (ej: 2025-10-13) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: No aplicable.
- Split bilingüe: No aplicable — % por tokens: ES=100%, EN=0%, other=0%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | contenido | Abcdefghijklmnopqrstuv Esto es una prueba | Abcdefghijklmnopqrstuv This is a test | Traducción al inglés |

**WHY:** Normalizar aporta comparabilidad; preservar Raw asegura trazabilidad.

---

# Tablas & OCR Reliability

## Conteo de Tablas
| Doc-ID | Parser Tables | OCR Tables | Confianza Parser | Confianza OCR | manual_review |
|---|---:|---:|---:|---:|---|
| D-001 | 0 | 0 | N/A | N/A | No |

**Regla:** No hay tablas para revisar.  
**WHY:** No se aplican estructuras de tabla.

---

# Quality Scoring & Validators

## Quality Scores
| Doc-ID | Señal/Ruido | Parse Conf. | Integridad | Legibilidad | Score (0–1) | Estado |
|---|---:|---:|---:|---:|---:|---|
| D-001 | 0.37 | N/A | N/A | N/A | **0.37** | **BLOCK** |

**Umbral:** **score < 0.70 → BLOCK**  
**Validator Report:**
- Doc: D-001 — Motivos: Calidad insuficiente — Acciones sugeridas: Revisar el contenido — Dueño: N/A — ETA: N/A  
**WHY:** Aguas abajo sólo deben consumir evidencia fiable.

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251020-1353-<short-hash>
- **processing_start_local:** 2025-10-20 13:53:11
- **processing_end_local:**   2025-10-20 13:53:22
- **processing_duration:**    00:00:11

## Lineage global (componentes y versiones)
- Loader: DocxLoader v1.3
- Cleaner: RegexCleaner v2.1
- Normalizer: NumDateNorm v1.0
- Vectorizer: N/A

**WHY:** Garantiza reproducibilidad exacta.

---

# Vectorization & Namespace

## Indexación Vectorial
- **Namespace:** mimetica/mixed/2025-10-20  
- **Cobertura (chunks):** 0/1  
- **Modelo de Embedding:** N/A  
- **Prueba de Búsqueda (smoke test):** No aplicable

**WHY:** Validación mínima de recuperabilidad.

---

# Extracted Evidence (Facts, KPIs, Assumptions, Behavioral Vars)

## Quantitative Facts (con unidades y marcos)
No hay hechos extraídos debido a la falta de datos cuantitativos en el documento.

**WHY:** Hechos con unidades y marcos permiten ROI/NPV/Payback comparables.

## KPIs & Criteria (definición + gobierno)
No se han definido KPIs debido a la falta de contenido suficiente.

**WHY:** Define reglas de decisión y control operativo.

## Early Risks / Assumptions / Dependencies
No se han identificado riesgos ni suposiciones debido a la falta de contenido.

**WHY:** Anticipa incertidumbres críticas.

## Behavioral Variables (economía del comportamiento)
No se han definido variables conductuales debido a la falta de contenido.

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

- 100% documentos con **status = blocked** (con Validator Report).
- **dataset_id** presente y bien formado.
- **processing_duration** calculado.
- Todos **quality_score < 0.70**; bloqueo explícito.
- **namespace** consistente (*mimetica/mixed/2025-10-20*).
- Números/fechas normalizados con **Raw** preservado.
- Conflictos OCR vs Parser no aplicables.
- Split **ES/EN** no aplicable.
- Lineage completo **loader→cleaner→normalizer→vectorizer**.
- Hechos/KPIs no aplicables.
- Variables conductuales no aplicables.

---

# WHY (Meta-Rationale, 4–6 bullets)
- **Evidence →** No se extrajo evidencia suficiente. **Inference →** La calidad del documento es inadecuada. **Implication →** Se requiere revisión y mejora del contenido.  
- Comparabilidad garantizada por la normalización (aunque no se aplicó) con Raw preservado.  
- El bloqueo temprano evita que se consuman datos de baja calidad.  
- Se requiere un enfoque en la mejora para futuras cargas de documentos.  
- La falta de contenido suficiente limita la capacidad de análisis y toma de decisiones.
```