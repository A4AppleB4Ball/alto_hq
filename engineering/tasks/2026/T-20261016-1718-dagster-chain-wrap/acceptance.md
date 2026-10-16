# Acceptance: dagster-chain-wrap (DRAFT, not approved)

Depends on completeness-check and dagster-environment. A pilot first: two
companies, then the owner decides the fleet. No LLM run beyond the pilot
without the owner.

1. **Pilot, batched.** One Dagster run over two named companies calls each
   existing CLI stage once with both companies (producers, intake, quarterly,
   stance), not one run per company. Event log shown.
2. **Per-company verdicts.** For each company the stored records show every
   asset state and the completeness verdict with state and reason, readable
   by a short Python query (no UI).
3. **A failure stops only its company.** Inject a failing step for one
   company (temp copy): the other company's stance still materialises; the
   failed company's stance does not and its reason is in the record.
4. **Not wrong-but-green.** A run with a failing company is not reported as
   a clean success by the query; the failing company is listed.
5. **Product code unchanged** except entry points that must accept a
   company list; each such change has a test failing before and passing
   after. The scheduler jobs listed as moved are disabled in
   `pipeline_scheduler.yaml` only when the owner approves cut-over.
6. **Repo checks.** Boundary test, entry-point imports, suite vs base.
