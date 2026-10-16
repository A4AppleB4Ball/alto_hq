---
schema: task/v1
id: T-20261016-2155-document-intelligence-slm
title: "Small models (qwen 4b/9b) identify each document's type and metadata, scored on the stored index"
status: draft
created: 2026-10-16T21:55+05:30
created_by: claude-main
kind: internal
spawned_from: E-20261016-1756-stance-inputs
related: [E-20261016-1756-stance-inputs, T-20261016-2147-checks-index-quarterly]
---

## Goal

Epic story 4. A document-intelligence step runs a small model (qwen 4b and 9b compared) over each document's first pages and returns type, reporting period and date evidence with the page it came from. The step is built and scored first on documents whose type and period are already known; wiring into intake is a later task.

## Why

Measured 2026-10-16 over 14664 indexed documents (3907 companies): 378 `quarterly_pdf` and 14 others carry no `reporting_period`; 1076 have no `processing_status`; 9100 carry `date` and 9031 `publish_date`, 7546 with a source. Types come from the source's labels (concall_ppt 5508, annual_report 4383, concall_transcript 4382, quarterly_pdf 386), not from the document. No model is configured today for this (`backend/config/llm_settings`).

## Out of scope

Replacing existing metadata; the dedup (story 5); production wiring; costly full-corpus runs.
