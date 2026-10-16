# Acceptance: document-intelligence-slm (draft)

A spike-sized pilot: a stratified sample, scored against stored labels, then
the owner decides the corpus run. Read-only on `news_server/data`; outputs in
a temp dir. The first-pages text comes from the already-extracted docling
output on disk, not a new extraction.

1. **Sample from stored state.** 200 documents drawn by a seeded script
   across the four types and across BSE/NSE/Screener/StockEdge/Stockscans
   sources, from documents whose `type` and `reporting_period` the index
   already holds. The sample list and seed are saved; the counts per type and
   source are printed.
2. **Model comparison.** Both qwen sizes run on all 200 with the same prompt
   (goal-stated, no rule lists). Type accuracy, period accuracy and the share
   with evidence quoted from the page are tabled per model, plus seconds per
   document and the machine used.
3. **Disagreements read, not averaged.** Every disagreement with the stored
   label is listed with the page text; QA reads 20 and says whether the
   stored label or the model was right.
4. **The unlabelled slice.** Run on the 378 `quarterly_pdf` documents with
   no `reporting_period`: the output states how many get a period with
   evidence and shows 10 for the owner. Nothing is written to any index.
5. **Failure is loud.** A page-less or unreadable document returns an
   explicit failure record, never a guessed type; a test shows it.
6. **No code in production paths.** `git diff --stat` touches only a new
   feature folder and its tests; `python -m pytest <that folder> -q` passes.
