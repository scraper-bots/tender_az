Because healthcare data exchange needs **shared semantics, reliable transport, security, auditability, and support for clinical workflows** — things that simple spreadsheets or ad-hoc JSON files do **not** provide at scale. HL7 standards (especially v2 and FHIR) exist precisely to solve those problems. Modern HL7 (FHIR) _does_ use JSON as one serialization option, but simply exchanging generic JSON or spreadsheets between systems would create safety, interoperability, and operational problems.

---

# Why spreadsheets are (almost always) a bad idea

Spreadsheets are useful for human-level ad-hoc work, but they fail for clinical integration for many reasons:

- **No agreed semantics** — a column named `DOB` in one file might be `DateOfBirth` in another; units, formats, coding systems and meanings vary wildly.
    
- **No standard validation** — spreadsheets are error-prone (typos, accidental reordering, mixed types), and there’s no machine-readable schema enforcement.
    
- **Poor provenance & audit trail** — regulatory environments require who changed what and when; spreadsheets lack tamper-evident, auditable change logs.
    
- **Security & privacy** — spreadsheets are often emailed or put on shared drives without proper encryption, access control, or patient consent tracking.
    
- **Concurrency & transactions** — clinical systems need safe concurrent updates and transactional guarantees; spreadsheets offer none.
    
- **Scale & automation** — automated systems (EHRs, devices, labs, registries) expect well-defined machine interfaces, not files that need manual processing.
    
- **Clinical risk** — data errors (wrong patient, wrong units) can directly jeopardize patient safety.
    

For these reasons spreadsheets are sometimes used for small one-off tasks (reports, simple lists) but are unacceptable for production clinical data exchange.

---

# Why HL7 (and similar standards) exist — what they provide

HL7 family standards (v2, v3, CDA, and now FHIR) address the real needs of healthcare systems:

- **Shared semantics & structure**: message types (ADT for admissions, ORU for results, ORM for orders) with defined segments and fields reduce ambiguity.
    
- **Terminology binding**: standards mandate or expect use of code systems (LOINC, SNOMED CT, ICD, RxNorm) so “heart rate” or “WBC” are unambiguous.
    
- **Reliable messaging patterns**: acknowledgements (ACK), retries, asynchronous flows, and message sequencing are part of operational expectations.
    
- **Transport & connectivity**: HL7 has well-known transports (MLLP, web services, enterprise queues) and integration engines (middleware) to manage routing, buffering, and transformations.
    
- **Backward compatibility & pragmatic flexibility**: HL7 v2 is deliberately permissive so diverse legacy systems can interoperate without breaking.
    
- **Conformance & profiles**: conformance statements and implementation guides (e.g., IHE profiles, national guides) define exact expectations for real projects.
    
- **Security & audit**: standards and implementations account for authentication, authorization, encryption, and logging needed for compliance (HIPAA, GDPR, local laws).
    
- **Ecosystem & tooling**: validators, integration engines (Mirth, Rhapsody), terminology servers, and large vendor adoption reduce integration effort.
    

In short: HL7 isn't chosen for nostalgia — it's chosen because it encodes all the operational, semantic, and safety requirements that clinical integration needs.

---

# What about JSON? (And FHIR)

“JSON” itself is only a serialization format. It tells you _how_ to encode data, not _what_ the fields mean or how messages should be routed/acknowledged.

- **FHIR** (Fast Healthcare Interoperability Resources) is the modern HL7 standard that **uses JSON (and XML)** as native serializations and provides:
    
    - A resource-based model (Patient, Observation, Medication).
        
    - **Well-defined semantics** and terminology bindings.
        
    - Standard RESTful API patterns, search, pagination, and OAuth2/Security profiles.
        
    - Conformance tooling, profiles, and community implementation guides.
        
- So, many modern healthcare integrations _do_ use JSON — but **they use JSON that conforms to FHIR**, not arbitrary JSON authored by a clinician in Excel.
    

Problems with arbitrary JSON (non-standard):

- Without a shared schema and terminology binding, different systems will interpret fields differently.
    
- No agreed transaction model (how do you signal “this is an update vs a new record”?).
    
- No community of implementers, profiles, validators — you end up building all of that yourself.
    

---

# The practical reality: legacy, cost, and inertia

- **Large installed base**: Many hospitals/vendors run systems built decades ago that speak HL7 v2. Rewriting them is expensive and risky.
    
- **Incremental migration**: Organizations often run HL7 v2 internally and add FHIR APIs for new apps. Coexistence is common.
    
- **Integration middleware**: Integration engines transform HL7→FHIR→internal formats. That reduces the need to reengineer every system.
    
- **Regulation & procurement**: Contracts and certification often require support for specific standards — vendors must support those to sell.
    
- **Clinical workflows are complex**: Order lifecycles, cancel/replaces, result interpretations, consent — these require semantic rules, not just data dumps.
    

---

# Example: HL7 v2 ADT message vs FHIR Patient JSON

HL7 v2 (very short ADT^A01 example):

```
MSH|^~\&|HOSP|RAD|LIS|LAB|20250811||ADT^A01|12345|P|2.5
EVN|A01|20250811
PID|1||123456^^^HOSP^MR||SMITH^JOHN||19800101|M|||123 Main St^^Anytown^ST^12345||555-1234
```

FHIR Patient (JSON):

```
{
  "resourceType": "Patient",
  "id": "123456",
  "name": [{ "family": "Smith", "given": ["John"] }],
  "gender": "male",
  "birthDate": "1980-01-01",
  "address": [{ "line": ["123 Main St"], "city": "Anytown", "state": "ST", "postalCode": "12345" }]
}
```

Both are machine-readable — the difference is that FHIR defines the data model, search, links between resources (e.g., encounter→patient), and security patterns, whereas raw JSON without a model would not.

---

# Migration & real-world recommendations

If you’re designing or improving health IT interoperability:

1. **Prefer standards, not ad-hoc formats**: Use FHIR for modern APIs and HL7 v2 or CDA where the ecosystem requires it.
    
2. **Use terminology services**: enforce code systems (LOINC, SNOMED, RxNorm) at input and exchange boundaries.
    
3. **Use integration engines**: handle transforms, routing, persistence, and retries in middleware rather than direct file exchanges.
    
4. **Validate & version**: implement schema/structure validation and track versions and conformance statements.
    
5. **Design for security & audit**: OAuth2, TLS, role-based access, consent capture, and immutable audit logs are essential.
    
6. **Start small & iterate**: build FHIR facades on legacy systems to expose canonical APIs without rewriting core systems.
    
7. **Engage clinical stakeholders**: ensure data semantics align with clinical workflows (critical for safety).
    
8. **Invest in patient identity matching**: patient matching is hard; robust identifier strategies and matching logic are necessary.
    

---

# Final point (practical): doctors vs healthcare IT engineers

When you say “doctors” — remember clinicians care about patient care, not data modeling. The people choosing standards are usually health IT teams, vendors, and national/regional authorities who must ensure safe, scalable exchange. Clinicians will use UIs and apps that _should hide_ this complexity — but the underlying infrastructure must be robust, standardized, and auditable, which is why HL7/FHIR (not spreadsheets) are used in production.

---

If you want, I can:

- show a concrete mapping example (HL7 v2 → FHIR) for a specific message type (e.g., lab result ORU → Observation),
    
- draft a short conformance profile for a simple use case, or
    
- list common integration engines and tooling patterns used in hospitals.
    

Which would be most useful to you?