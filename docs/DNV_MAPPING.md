DNV Synergi Alignment (Conceptual Mapping)
=========================================

Scope: Conceptual alignment of SafetyMind data model and workflows with common DNV Synergi concepts. This is non-proprietary, vendor-neutral guidance to ease migration and reporting.

High-level Concepts
-------------------
- Event: The core record of a near-miss or incident/accident
- Classification: Event type, consequence categories, severity band
- Workflow: Draft → Submitted → Under Review → Closed
- Causes: Immediate vs. Underlying/Root
- Actions: Corrective and Preventive Actions (CAPA)

Field Mapping
-------------
- SafetyMind.report.id ↔ Synergi Event ID (surrogate key)
- SafetyMind.report.title ↔ Event Title
- SafetyMind.report.description ↔ Event Description / Narrative
- SafetyMind.report.event_type (NearMiss|Incident|Accident) ↔ Classification: Event Type
- SafetyMind.report.consequence (Injury|Environmental|AssetDamage|ProcessSafety|Security|Other) ↔ Consequence Categories
- SafetyMind.report.severity (Insignificant..Catastrophic) ↔ Severity / Risk Level band
- SafetyMind.report.status (Draft|Submitted|UnderReview|Closed) ↔ Workflow Status
- SafetyMind.report.location ↔ Site / Location
- SafetyMind.report.activity ↔ Activity / Task
- SafetyMind.report.occurred_at ↔ Occurrence Date/Time
- SafetyMind.report.reported_by ↔ Reporter (PII, redacted by default in exports)
- SafetyMind.report.extra ↔ Custom fields / extended attributes

Causes & Actions
----------------
- SafetyMind AI may suggest immediate and underlying causes (rules/ML), but final cause coding is human-reviewed.
- Recommended corrective actions are suggestions only; approval and assignment should be handled by governance workflow.

Severity Alignment
------------------
- Suggested weight mapping for severity index:
  - Insignificant: 1
  - Minor: 2
  - Moderate: 3
  - Major: 4
  - Catastrophic: 5
- Severity index is an average weight across records, useful for trend tracking; it is not a risk matrix replacement.

Benchmarking Notes (Oil & Gas)
------------------------------
- Near-miss rate: near_misses per 200,000 hours worked
- Incident rate: recordable incidents per 200,000 hours worked
- Severe share: fraction of Major+Catastrophic events
- Interpretation: higher near-miss reporting with low incident rate may indicate strong reporting culture.

Data Governance
---------------
- PII: redact in exports by default; limit fields to job roles rather than names where possible
- Retention: configure per policy; ensure secure deletion
- Access: future support for RBAC/SSO/OIDC

Migration Tips
--------------
- Use `export` (CSV/JSON) to align extract fields with Synergi import templates.
- Map enumerations directly; add translations where codes differ.
- For custom fields, put key/value in `extra` and define a local codebook.
