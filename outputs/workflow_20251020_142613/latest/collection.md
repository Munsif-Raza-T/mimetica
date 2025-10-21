# Phase: Collection
**Timestamp:** 20251020_142812
**Workflow ID:** workflow_20251020_142613
**Language Tag:** en
# Dataset Manifest

Dataset ID: DS-20251020-1426-<short-hash>
Fecha/Hora de Ingesta: 2025-10-20 14:26
Duración de Procesado: 00:00:00
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
- processing_start_local: 2025-10-20 14:26:58
- processing_end_local:   2025-10-20 14:27:16
- processing_duration:    00:00:18

---

# Inventory & Coverage

## Inventario de Archivos (exactos)
- **Total**: 1  
- **Lista (exact filenames, case/spacing preserved)**:
  - Nuevo Documento de Microsoft Word.docx (tipo=.docx, lang=es, size=13498 bytes, short_hash=<short-hash>)

## Dedupe & Near-duplicates
- Criterio: sim ≥ 0.95  
- Near-duplicates detectados: 0 → []
- Decisión: mantener — **WHY:** No duplicados

---

# Cleaning & Normalization (with Raw Preservation)

## Reglas Aplicadas
- Encodings: UTF-8 • Control chars removidos: sí
- Fechas → **ISO-8601** (ej: 2025-10-20) — **Raw** preservado.
- Números → **decimal point** (ej: 12345.67) — **Raw** preservado.
- Segmentación: párrafos/tablas con IDs estables.
- Split bilingüe: ES/EN (si aplica) — % por tokens: ES=0%, EN=100%, other=0%

## Ejemplos de Normalización (muestra)
| Doc-ID | Campo | Raw | Normalizado | Nota |
|---|---|---|---|---|
| D-001 | texto | Esto es una prueba | Esto es una prueba | N/A |
| D-001 | fecha | 20/10/25 | 2025-10-20 | ISO-8601 |

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
| D-001 | 0.94 | 0.92 | 1.0 | 0.88 | **0.93** | OK |

---

# Versioning & Lineage

## Dataset & Tiempo
- **dataset_id:** DS-20251020-1426-<short-hash>
- **processing_start_local:** 2025-10-20 14:26:58
- **processing_end_local:**   2025-10-20 14:27:16
- **processing_duration:**    00:00:18

## Lineage global (componentes y versiones)
- Loader: DocxLoader v1.3
- Cleaner: RegexCleaner v2.1
- Normalizer: NumDateNorm v1.0
- Vectorizer: e5-large-v2 (dim=1024)

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
| F-001 | Texto del documento | N/A | N/A | N/A | D-001 §1 (2025-10-20) |

---

# Machine-Readable Artifacts

## documents.csv
```csv
doc_id,filename_exact,short_hash,lang_primary,tokens,tables,normalized_dates_numbers,quality_score,status,manual_review,source_path,loader,cleaner,normalizer,vectorizer,namespace
D-001,Nuevo Documento de Microsoft Word.docx,<short-hash>,es,5,0,True,0.93,indexed,False,<path_to_document>,DocxLoader v1.3,RegexCleaner v2.1,NumDateNorm v1.0,e5-large-v2,mimetica/mixed/2025-10-20
```

## facts_kpis.csv
```csv
item_id,type,description,value,unit,timeframe,cohort_geo,source,access_date,owner,system,cadence,threshold,notes
F-001,fact,Texto del documento,N/A,N/A,N/A,N/A,D-001 §1,2025-10-20,N/A,N/A,N/A,N/A
```