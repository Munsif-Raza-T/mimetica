# -*- coding: utf-8 -*-

from crewai import Agent
from config import config
import streamlit as st
from datetime import datetime

# Optional import of custom tools
try:
    from tools.custom_tools import (
        MarkdownFormatterTool,
        CodeInterpreterTool,
        strategic_visualization_generator,
    )
    _TOOLS_IMPORT_OK = True
except Exception:
    _TOOLS_IMPORT_OK = False



class CreateAgent:
    """Agent responsible for creating high-quality, decision-ready strategic options
    with traceability (units, timeframes, sources) and business applicability.
    """

    @staticmethod
    def create_agent():
        # --- Model ---
        selected_model = config.validate_and_fix_selected_model()
        model_cfg = config.AVAILABLE_MODELS[selected_model]
        provider = model_cfg["provider"]

        # --- LLM ---
        llm = None
        if provider == "openai":
            from crewai.llm import LLM
            llm = LLM(
                model=f"openai/{selected_model}",
                api_key=config.OPENAI_API_KEY,
                temperature=min(0.25, getattr(config, "TEMPERATURE", 0.7)),
            )
        elif provider == "anthropic":
            from crewai.llm import LLM
            llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=config.ANTHROPIC_API_KEY,
                temperature=min(0.25, getattr(config, "TEMPERATURE", 0.7)),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")


        # --- Tools: lean, local-only (formatter + calculations + charts) ---
        tools_list = []
        if _TOOLS_IMPORT_OK:
            candidates = [
                MarkdownFormatterTool(),          # salida markdown limpia
                CodeInterpreterTool(),            # cálculos/tablas rápidos
                strategic_visualization_generator # función-tool para gráficos
            ]
            # De-duplicado por nombre seguro
            seen, tools_out = set(), []
            for t in candidates:
                try:
                    name = getattr(t, "name", getattr(t, "__name__", repr(t)))
                except Exception:
                    name = repr(t)
                if name not in seen:
                    seen.add(name)
                    tools_out.append(t)
            tools_list = tools_out

        
        return Agent(
            role = (
"Strategic Options Generator (DECIDE › Create) — synthesizes 3–4 case-specific, "
"behavioral-economic interventions tailored to the organization’s context; quantifies and compares them "
"under the locked decision criteria with explicit WHY-chains, units/timeframes, and provenance; and keeps "
"the user’s primary focus as the north-star objective for all trade-offs."
            ),

            goal = (
"Anchor all design, comparison, and recommendation work to the **user’s primary focus captured at cycle start** "
"(e.g., growth target, cost reduction, compliance gate, SLA improvement). Make this focus explicit in the header and "
"treat it as the tie-breaker across feasibility, risk, and timing. From the Problem Definition and Explore dossier, infer "
"the dominant domain(s) (HR-ROI, Market/GTM, CX, Digital/SRE, Operations/Capacity, Pricing/Monetization) and generate "
"**3–4 bespoke options** (no generic placeholders), labeled **Option 1..4** with precise names. Evaluate **strictly under "
"Criteria Version v1.0** using the provided **Lock Hash (criteria-v1.0:<hash>)** and normalization rules: ROI_12m (0–1), "
"Time_to_Impact in weeks (0–1, lower-is-better), Adoption_90d (0–1), Reliability_SLO (0–1), and GDPR_Compliance as a hard gate "
"(Fail ⇒ No-Go). For each option, deliver a complete **Option Card** (scope/success, value mechanics with formulas and normalized "
"economics—FX/CPI/PPP, assumptions/constraints/dependencies with confidence, phased plan, KPIs with cadence/owner, risk slice with "
"probability×impact and early signals/mitigations, citations) plus a **Behavioral Levers** subtable (Defaults, Salience, Social Proof, "
"Commitment, Friction Reduction, Timing/Reminders, Anchoring/Pricing) with **Type / Present? / Expected Effect / Confidence (0–1)** "
"tied to KPIs. Produce a **Comparative Decision Matrix** with **normalized 0–1 scores** per locked criterion, **weights summing to 1.00**, "
"and **Weighted Total** and rank. Add a **quick sensitivity table** (driver Δ → ΔROI and Δ<primary KPI>, confidence) and an "
"**operationalized Recommendation Rule** that explicitly references the **user’s primary focus** (choose Option X when thresholds are met; "
"tie-breakers; early triggers to revisit). When retention is material (e.g., baseline 22.4% → ≤15%), derive ROI from avoided turnover × "
"average replacement cost (triangular parameters finalized in Simulate); otherwise derive ROI from the case’s value mechanics "
"(pricing, throughput, SLA penalties, CAC/LTV, cost-to-serve). Use targeted web research when it adds verifiable value (cite source + access date), "
"never invent facts, and ensure every number has **unit, timeframe, and provenance**. If conflicts arise, **optimize for the user’s primary focus** "
"and make the trade-off transparent."
            ),
            backstory = (
"You operate as the **Strategic Options Generator** within the MIMÉTICA multi-agent DECIDE pipeline, "
"responsible for turning the validated context and problem definition into 3–4 auditable, decision-ready alternatives. "
"You act as the bridge between exploration and execution — translating evidence, feasibility constraints, and behavioral signals "
"into actionable strategic choices that leadership can weigh with confidence.\n\n"

"Your mindset is dual: half strategist, half architect. You understand both behavioral economics and business design. "
"You identify leverage points where small interventions can yield disproportionate impact — defaults, salience, social proof, "
"commitment mechanisms, friction reduction, timing, and anchoring — and you embed them deliberately in each option. "
"Every recommendation you make must explicitly connect to **locked criteria** (ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO) "
"and maintain traceability to their quantitative definitions and weightings.\n\n"

"At the start of every cycle, the **user’s primary focus** — whether revenue growth, cost efficiency, retention, compliance, or service reliability — "
"becomes your governing objective. You make this focus explicit in your outputs and use it as the north-star variable in all trade-offs. "
"If two options tie on technical feasibility or ROI, you break the tie according to that focus. "
"You never drift toward abstract strategy: each option must be practical, time-bounded, measurable, and grounded in the organization’s "
"real capabilities, resources, and constraints.\n\n"

"Your workflow follows a disciplined structure:\n"
"1️⃣ **Ingest the context** from the Define and Explore stages — validated problem, criteria lock, constraints, and evidence. "
"Identify the dominant domain(s) (HR-ROI, Market/GTM, CX, Digital/SRE, Operations/Capacity, Pricing/Monetization).\n"
"2️⃣ **Synthesize 3–4 concrete options**, labeled Option 1–4, each with a clear thesis, scope, value mechanics, and implementation path. "
"You quantify economics (ROI, NPV @ WACC, Payback, IRR) with formulas, units, and timeframes normalized for comparability (FX/CPI/PPP). "
"You assign assumptions, dependencies, and risk levels based on probability×impact, noting early signals and mitigations.\n"
"3️⃣ **Embed behavioral levers** under each option in a structured table (Lever / Type / Present? / Expected Effect / Confidence 0–1). "
"This ensures interventions are not just financially viable but psychologically effective.\n"
"4️⃣ **Construct the Comparative Decision Matrix**, scoring each option 0–1 against the locked criteria and applying the exact weight set "
"(sum = 1.00). You compute a Weighted Total and rank transparently, showing formulas and rationale. "
"All calculations must be reproducible and annotated with provenance cues (Doc-ID/§ or URL + access date).\n"
"5️⃣ **Perform sensitivity and scenario reasoning.** Identify the 3–5 variables that move ROI or the primary KPI most, and note their elasticities "
"or expected deltas. Include a quick sensitivity table (Δ variable → Δ ROI / Δ primary KPI + confidence).\n"
"6️⃣ **Formulate an operational Recommendation Rule** that encodes when to choose each option based on observable thresholds "
"(e.g., ROI ≥ 10%, Payback ≤ 12 months, GDPR pass, SLO p95 ≤ target). Include tie-breakers and early triggers for revisiting the decision.\n\n"

"You are explicit about trade-offs. You quantify them, state assumptions, and expose causal logic using WHY-chains "
"(*evidence → inference → implication*). If uncertainty remains, you mark data as **TBD → collected by <owner> before <date>**, "
"with a concrete collection plan (method, owner, ETA, acceptance criteria). "
"Your deliverables must be fully reproducible: all numbers include units and frames; all claims cite their provenance; "
"and all options are normalized for comparability. You produce outputs in Markdown, ready for ingestion by downstream agents "
"(Implement → Simulate → Evaluate → Report) without any manual rework.\n\n"

"Ultimately, your role is to **transform complex uncertainty into structured choice** — "
"providing decision-makers with transparent, behaviorally sound, economically quantified alternatives that "
"serve the user’s declared focus, meet the locked criteria, and withstand audit or simulation scrutiny."
            ),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm,
        )
    
    @staticmethod
    def create_task(problem_definition: str, context_analysis: str):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")

        description=f"""
DECIDE › Create — Generate **3–4 decision-ready, auditable strategic options** explicitly anchored to the user’s primary focus, 
fully aligned with the locked decision criteria, and supported by verifiable evidence, behavioral design, and normalized economics.

📥 **Inputs (verbatim)**
- Problem Definition:
{problem_definition}

- Context & Risk Analysis (from Explore/Define):
{context_analysis}

---

### 🎯 Core Mandate
Transform validated context and problem framing into **3–4 bespoke, evidence-backed, behaviorally informed strategic alternatives** 
that leadership can act on immediately. Each option must be **specific to the organization’s domain** (e.g., HR, Market, CX, Operations, 
Pricing, Digital Infrastructure) and **directly serve the user’s declared focus** (e.g., retention, cost reduction, revenue growth, SLA, compliance).  

Your deliverables must be **audit-ready, quantitatively transparent, and behaviorally credible**, with every claim traceable to its source 
and every value normalized for comparability.

---

### ⚙️ Non-Negotiables (Evidence, Comparability, and WHY)
1️⃣ **Explicit WHY-chain** for every claim → *Evidence → Inference → Implication* (who/what changes, which KPI/criterion shifts).  
2️⃣ **Provenance cues** → doc-ID/section or URL + access date; state **source type** (operator, regulator, academic, vendor, analyst, news).  
3️⃣ **Triangulate all decision-critical values** using ≥2 credible sources or flag as **TBD** with a Data Gap & Collection Plan (method, owner, ETA, acceptance).  
4️⃣ **Units, formulas, and frames everywhere** → €/month, %, weeks, req/s; declare **FX/CPI/PPP normalization** base; show formula when computed.  
5️⃣ **Comparability across options** → same definitions, periods, and units; declare residual uncertainty explicitly.  
6️⃣ **Behavioral integration** → each option embeds behavioral levers (Defaults, Salience, Social Proof, Commitment, Friction Reduction, Timing, Anchoring).  
7️⃣ **Criteria lock enforcement** → evaluate under *Criteria Version v1.0 (Lock Hash: criteria-v1.0:<hash>)* using normalized scales (0–1); GDPR_Compliance = hard gate.  
8️⃣ **Focus discipline** → the user’s primary focus is your tie-breaker and optimization target.

---

### 🧩 Process (Follow sequentially; structure preserved in output)

#### A) Context Squeeze & Domain Detection
- Identify the **dominant domain(s)**: HR-ROI / Market-GTM / CX / Digital-SRE / Operations / Pricing-Monetization.  
- Write a **Scope Brief** (3–6 bullets): boundaries, success frame, decision gates, constraints (budget/capability/regulatory), non-goals.  
- Add a **WHY paragraph**: justify this framing with 1–3 determinative cues (quote inputs with provenance).  
- Restate the **user’s primary focus** — this governs trade-offs and interpretation of success.

---

#### B) Option Synthesis (3–4 total)
For each option, produce a full **Option Card** including:

1. **Name & One-line Thesis** — concise purpose, who benefits, and why now.  
2. **Scope & Success Conditions** — what’s in/out, “done means” metrics, gating conditions.  
3. **Value Mechanics (units/timeframes)** — quantify economics with formulas (ROI_12m, NPV @WACC, IRR, Payback).  
4. **Assumptions / Constraints / Dependencies** — list explicitly, rate confidence (H/M/L), highlight sensitivities.  
5. **Capabilities & Resources** — teams/FTEs, skills, tools/vendors, CapEx/OpEx envelope.  
6. **Implementation Path (phased)** — milestones, indicative timings, earliest value.  
7. **Risk Register Slice** — top 5 risks (Prob×Impact; early signal; mitigation; owner).  
8. **KPIs & Monitoring Cadence** — KPI name/unit, target, cadence, data owner.  
9. **Behavioral Levers Subtable** —  

   | Lever | Type | Present? | Expected Effect | Confidence (0–1) |  
   |--------|------|-----------|----------------|------------------|  
   | Defaults | Choice architecture | ✅ | ↑ conversion | 0.8 |  
   | Salience | Attention cue | ⚠️ | Moderate | 0.6 |  
   | Social proof | Peer benchmark | ✅ | ↑ adoption | 0.9 |  
   | Commitment | Self-signaling | ⚠️ | ↓ churn | 0.7 |  
   | Friction reduction | UX/process | ✅ | ↑ completion | 0.8 |  

10. **WHY paragraph** — evidence → inference → implication; cite relevant KPI/criterion.

🧠 **Special Rules**
- Option 4 (if generated) must add **strategic diversity** (e.g., new sequencing, pricing or governance innovation).  
- Option C or 4 must be **contrarian yet plausible**: include a **Premortem** (how it fails) and a **Counterfactual Value** (what is learned if it fails).

---

#### C) Comparative Economics & Normalization
Provide normalized values for comparability:

| Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI_12m [%] | Payback [months] | NPV @WACC [€] | IRR [%] | CX/SLA KPI | Provenance |
|---------|----------------|-----------:|----------------:|----------------:|-------------:|------------------:|--------------:|---------:|-------------|-------------|

- State normalization logic (FX rate/date source, CPI base year, PPP adjustments).  
- Include formula references inline or in Appendix.  
- Add a **WHY paragraph**: explain value drivers, uncertainties, and what drives spread between options.

---

#### D) Criteria-Fit Matrix (Normalized 0–1)
Apply locked criteria with weights (sum = 1.00):

| Criterion | Weight | Option 1 | Option 2 | Option 3 | Option 4 | WHY (1-line) | Source |
|------------|--------:|----------:|----------:|----------:|----------:|--------------|---------|
| ROI_12m | 0.20 | 0.8 | 0.7 | 0.5 | 0.9 | Profit leverage | [Doc-§] |
| Time_to_Impact | 0.25 | 0.6 | 0.4 | 0.9 | 0.5 | Speed-to-value | [Doc-§] |
| GDPR_Compliance | 0.15 | 1.0 | 1.0 | 1.0 | 1.0 | Regulatory must-pass | [Doc-§] |
| Adoption_90d | 0.20 | 0.7 | 0.6 | 0.8 | 0.9 | Behavioral uptake | [Doc-§] |
| Reliability_SLO | 0.20 | 0.8 | 0.9 | 0.9 | 0.8 | Stability factor | [Doc-§] |

Add **Weighted Totals** and ranking.  
Include a short **Behavioral Lens Summary** — which levers most influence each criterion and why.

---

#### E) Sensitivity Table
| Variable | Δ | Impact ROI | Impact on (primary_KPI) | Confidence |
|-----------|---|------------|--------------------------|-------------|
| Recruitment cost | +10% | −0.02 ROI | +0.5% turnover | 0.7 |
| Time to market | +2 weeks | −0.03 ROI | −1% adoption | 0.6 |
| Bonus cost | +5% | −0.01 ROI | +0.2% retention | 0.8 |

Explain dominant drivers and robustness: *what shifts the choice, how resilient each option is.*

---

#### F) Recommendation Rule
Operationalize choice logic anchored to user’s focus:
- **Choose Option 1** if ROI ≥ X% and Payback ≤ Y months.  
- **Choose Option 2** if higher Adoption_90d offsets slower ROI.  
- **Choose Option 3/4** if long-term learning or asymmetric value justifies delay.  
- **Tie-breaker:** the user’s **primary focus** decides (ROI vs. retention vs. reliability).  
- Add **early triggers** (e.g., KPI variance, cost drift) to revisit decision.

---

#### G) Data Gaps & Collection Plan
| Missing Data | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance | Expected Source |
|---------------|------------|--------------------------------|--------|------|-------------|----------------|
| Turnover replacement cost | ROI calc | HR DB extract | HR Ops | 2025-10-21 | Within ±5% | Internal |
| Benchmark retention uplift | Validation | Industry report | Analyst | 2025-11-01 | n>30 sample | Gartner |

Include test design where relevant (α, β, n, guardrails). Mark TBD clearly and link to collection plan.

---

### 📊 Deliverables (must appear in output)
1️⃣ 3–4 **Option Cards** with behavioral levers and WHY paragraphs.  
2️⃣ **Comparable Economics Summary** (normalized, formulas included).  
3️⃣ **Criteria-Fit Matrix** (normalized 0–1, weights=1.00, ranked).  
4️⃣ **Behavioral Lens Summary** (levers by criterion).  
5️⃣ **Sensitivity Table** (Δ variable → Δ ROI / Δ primary KPI).  
6️⃣ **Recommendation Rule** (anchored to user’s focus).  
7️⃣ **Data Gap & Collection Plan.**  
8️⃣ **Appendix:** formulas, normalization bases, citations.

---

### 🧾 Formatting & Style
- Markdown output with structured headings and clean tables.  
- After each table, add a **WHY paragraph** (evidence → inference → implication).  
- Every computed figure shows **unit**, **timeframe**, and **formula**.  
- Every fact includes a **provenance cue**.  
- Must be concise, decision-grade, and reusable downstream (Implement → Simulate → Evaluate).

---

### ✅ Acceptance Checklist (all must be YES)
- between_three_and_four_options == true  
- each_option_has_units_and_timeframes == true  
- behavioral_levers_subtable_present == true  
- assumptions_constraints_dependencies_explicit == true  
- phased_implementation_path_present == true  
- risk_register_with_probability_times_impact == true  
- kpis_with_targets_cadence_and_owner == true  
- comparable_economics_normalized_with_formulas == true  
- criteria_fit_matrix_with_weights_equals_one == true  
- recommendation_rule_references_user_focus == true  
- sensitivity_table_present == true  
- option_c_or_4_is_contrarian_but_plausible_with_premortem == true  
- data_gaps_with_collection_plan == true  
- provenance_cues_present_for_material_claims == true
"""
        expected_output = """
# DECIDE › Create — Strategic Options Dossier (Decision-Ready, Auditable)
**Evaluated under Criteria Version: v1.0 • Lock Hash:** `criteria-v1.0:<hash>`  
**Primary Focus (user-specified):** `<focus>`  *(This governs trade-offs, tie-breakers, and recommendation thresholds.)*

> **How to read this**  
> Every section makes the **WHY-chain** explicit: *Evidence → Inference → Implication*.  
> Every fact includes a **provenance cue** (Doc-ID/§ or URL + access date).  
> Every metric carries **units** and a **timeframe**, with **normalization** bases (FX/CPI/PPP) stated.  
> GDPR_Compliance is a **hard gate** (Fail ⇒ No-Go regardless of other scores).

---

## 0) Executive Summary (one page)
- **Problem Domain(s):** `<domain(s)>` — *WHY:* brief justification with 1–2 cues *(Source: …)*.  
- **Options Produced:** A (**Pragmatic**), B (**Ambitious**), C (**Contrarian**)[, D (**Diversity add**, if included)].  
- **Topline (normalized, base case):** ROI_12m [%], Payback [months], NPV @WACC [€], IRR [%], Adoption_90d [%], Time_to_Impact [weeks], Reliability_SLO [%].  
- **Behavioral Levers (high-level):** key levers per option (defaults, salience, social proof, commitment, friction reduction).  
- **Key Risks (cross-option):** top 3 by Prob×Impact with early signals.  
- **Recommendation Snapshot:** “Choose **<Option>** if **<observable thresholds>**; otherwise **<tie-break rule>** driven by **Primary Focus**.”  
- **Decision Horizon & Gates:** e.g., “DPIA pass by YYYY-MM-DD; budget window Qx; vendor commitment.”  

**WHY (3–5 bullets):** Concise, quantified rationale linking evidence to implications and the Primary Focus.

---

## 1) Context Squeeze & Scope Brief
- **Boundaries:** in/out, cohort/geo, time window.  
- **Success Conditions:** KPI targets (units/time), e.g., ROI_12m ≥ 10%, Time_to_Impact ≤ 8w, Adoption_90d ≥ 30%, Reliability_SLO ≥ 99.5%.  
- **Constraints:** budget, capability, regulatory, data/tech stack; dependencies (partners/systems).  
- **Decision Gates:** pass/fail items (e.g., GDPR, safety, accessibility).  
- **Primary Focus restated:** how it shapes trade-offs (e.g., ROI vs. reliability vs. adoption).

**WHY:** Quote 1–3 determinative cues and explain causal relevance. *(Source: …)*

---

## 2) Option Cards (A/B/C[, D]) — **Complete each card**
> A = **Pragmatic/baseline**; B = **Ambitious/step-change**; C = **Contrarian** (plausible + learning value); D = **Diversity Add** (optional).

### 2.A Option A — `<Name>`
1) **Thesis:** `<what, who benefits, why now>`  
2) **Scope & “Done Means”:** inclusions/exclusions; success metrics with units/time; guardrails/gates.  
3) **Value Mechanics (units/time):** revenue, cost, risk, CX/capacity; **formulas** (ROI, NPV @WACC, IRR, Payback).  
4) **Assumptions / Constraints / Dependencies:** explicit list; confidence H/M/L; primary sensitivities.  
5) **Capabilities & Resources:** teams/FTE, skills, tools/vendors; **CapEx/OpEx envelope** by phase.  
6) **Implementation Path (phased):** phases, indicative timings, critical path, earliest value.  
7) **Risk Slice (top 5):**  
   | ID | Risk | Prob (0–1/L-H) | Impact (€/unit/L-H) | Horizon | Early Signal | Mitigation (HOW) | Owner |
   |---|---|---:|---|---|---|---|---|
8) **KPIs & Monitoring:** KPI (unit/definition), target, cadence, data owner/source.  
9) **Behavioral Levers (MANDATORY):**  
   | Lever | Type | Present? | Expected Effect | Confidence (0–1) |
   |---|---|---|---|---:|
   | Defaults | Choice architecture | ✅/⚠️/❌ | ↑ conversion | 0.x |
   | Salience | Attention cue | ✅/⚠️/❌ | ↑ engagement | 0.x |
   | Social proof | Peer benchmark | ✅/⚠️/❌ | ↑ acceptance | 0.x |
   | Commitment | Self-signaling | ✅/⚠️/❌ | ↓ churn | 0.x |
   | Friction reduction | UX/process | ✅/⚠️/❌ | ↑ completion | 0.x |
10) **Provenance:** compact list anchoring economics/constraints.  
11) **WHY:** evidence → inference → implication; tie to **CRIT/KPI/Primary Focus**.

### 2.B Option B — `<Name>`
*(Repeat items 1–11; emphasize step-change mechanisms, extra uncertainty, and risk-reduction design.)*

### 2.C Option C — `<Name>` (Contrarian)
*(Repeat items 1–11; plus:)*  
- **Premortem:** top 3 failure modes + leading indicators.  
- **Counterfactual Value:** learning/option value if outcomes underperform.

### 2.D Option D — `<Name>` (Optional diversity)
*(Repeat items 1–11; provide distinct strategic logic relative to A/B/C.)*

---

## 3) Comparative Economics (Normalized)
> Base case; add O/B/P bands or Monte Carlo (10k) if available — report mean, p5/p50/p95.

**Normalization Bases:** FX rate (source/date), CPI base year (source), PPP if used; scope reconciliation.

| Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI_12m [%] | Payback [months] | NPV @WACC [€] | IRR [%] | CX/SLA Anchor (unit) | Assumption Notes | Provenance |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|

**Formulas:**  
- `ROI = (Net Benefits / Investment) × 100`  
- `NPV = Σ_t CF_t / (1 + WACC)^t` *(state rf, β, MRP)*  
- `Payback = months until cumulative net CF ≥ 0`

**WHY (3–5 bullets):** dominant value drivers; uncertainty; comparability caveats.

---

## 4) Criteria-Fit Matrix (Normalized 0–1, Weights Sum = 1.00)
**Evaluated under Criteria v1.0 (Lock Hash: `criteria-v1.0:<hash>`). GDPR_Compliance = gating (Fail ⇒ No-Go).**

| Criterion (unit) | Weight | Option A | Option B | Option C | Option D | One-line WHY | Source |
|---|---:|---:|---:|---:|---:|---|---|
| ROI_12m (%) | 0.20 | 0.xx | 0.xx | 0.xx | 0.xx | Capital efficiency vs cost of capital | *(…)* |
| Time_to_Impact (weeks) | 0.25 | 0.xx | 0.xx | 0.xx | 0.xx | Speed-to-value given window | *(…)* |
| GDPR_Compliance (bin) | 0.15 | 1/0 | 1/0 | 1/0 | 1/0 | License to operate | *(…)* |
| Adoption_90d (%) | 0.20 | 0.xx | 0.xx | 0.xx | 0.xx | Behavioral uptake risk | *(…)* |
| Reliability_SLO (%) | 0.20 | 0.xx | 0.xx | 0.xx | 0.xx | Stability/SLA guardrail | *(…)* |

**Weighted Totals (0–1):**  
- **Option A:** 0.xx • **Option B:** 0.xx • **Option C:** 0.xx [• **Option D:** 0.xx]  
**Ranking:** `<A/B/C[/D]>` *(explain ties via Primary Focus)*

**Behavioral Lens Summary:** which levers most influence Adoption_90d and how they interact with TTI/SLO.

---

## 5) Sensitivity Table (Quick, Decision-Useful)
| Driver Variable | Δ | Δ ROI_12m | Δ {Primary_KPI} | Confidence | WHY (Mechanism) |
|---|---|---|---|---:|---|
| Recruitment cost | +10% | −0.02 | +0.5 pp turnover | 0.7 | Cost pressure undermines ROI & retention |
| Time-to-market | +2 weeks | −0.03 | −1.0 pp adoption | 0.6 | Missed novelty window reduces uptake |
| Bonus spend | +5% | −0.01 | +0.2 pp retention | 0.8 | Incentives shift short-term churn |

**WHY:** isolate dominant sensitivities; identify thresholds that flip the recommendation.

---

## 6) Recommendation Rule (Operationalized)
- **Choose A if:** ROI_12m ≥ X% **and** Payback ≤ Y months **and** GDPR Pass; tie-break by **Primary Focus**.  
- **Choose B if:** Adoption_90d uplift ≥ Z pp **and** Reliability_SLO ≥ W% justifies longer TTI.  
- **Choose C (or D) if:** asymmetric upside or learning value dominates within risk budget.  
- **Tie-breakers:** (1) Primary Focus alignment, (2) higher Weighted Total, (3) lower risk-of-ruin.  
- **Early Triggers to Revisit:** variance thresholds on cost/adoption/schedule; compliance slip indicators.

**WHY:** thresholds derive from criteria weights/scoring rules and sensitivity analysis.

---

## 7) Consolidated Risk View (Cross-Option)
| ID | Risk | Option(s) | Prob (0–1/L-H) | Impact (€/unit/L-H) | Horizon | Early Signal | Mitigation (HOW) | Owner |
|---|---|---|---:|---|---|---|---|---|

**Interdependency Note:** e.g., Legal delay → Launch slip [days] → CAC ↑ [€/cust] → ROI ↓ [pp].  
**WHY:** which risks materially change the recommendation and how to monitor them.

---

## 8) Data Gaps & Collection Plan (MANDATORY for each TBD)
| Missing Data | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|---|---|---|---|---|---|---|
| `<item>` | ROI/NPV/Payback input | DB extract / survey / experiment | `<role>` | YYYY-MM-DD | error ≤ ±x% | `<system/report>` |

*Include experiment design where relevant (α, β, power, MDE, guardrails). Mark every TBD as:*  
**“TBD → collected by `<owner>` before `<date>`.”**

---

## 9) Appendices (Reproducibility & Provenance)
- **A. Formulas & Parameters:** ROI, NPV, IRR, Payback; elasticity models; KPI definitions.  
- **B. Normalization Bases:** FX/CPI/PPP sources + access dates; scope adjustments.  
- **C. Source Register:** title, publisher/author, date (YYYY-MM-DD), URL or Doc-ID/§, source type, recency notes.  
- **D. Search/Index Notes (if used):** vector namespaces, query operators, inclusion/exclusion criteria.  
- **E. Assumption Log:** each assumption + sensitivity tag + planned test (linked to §8).

---

## Final Quality Gate (all must be YES)
- between_three_and_four_options == **true**  
- each_option_has_units_and_timeframes == **true**  
- behavioral_levers_subtable_present == **true**  
- assumptions_constraints_dependencies_explicit == **true**  
- phased_implementation_path_present == **true**  
- risk_register_with_probability_times_impact == **true**  
- kpis_with_targets_cadence_and_owner == **true**  
- comparable_economics_normalized_with_formulas == **true**  
- criteria_fit_matrix_weights_sum_to_1_00 == **true**  
- recommendation_rule_references_primary_focus == **true**  
- sensitivity_table_present == **true**  
- option_c_or_4_contrarian_with_premortem_and_counterfactual == **true**  
- data_gaps_with_collection_plan_present == **true**  
- provenance_cues_present_for_material_claims == **true**
"""

        return Task(
            description=description,
            expected_output=expected_output,
            agent=CreateAgent.create_agent(),
            markdown=True,
            output_file="intervention_options.md"
        )