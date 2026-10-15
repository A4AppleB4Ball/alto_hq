# alto_hq

The company that runs Alto. Alto (the product) is the `alto` repo; its state
is the data repo. This repo holds the company: its verticals, its employees
(AI agent roles), its policies, and the record of every piece of work.

The owner manages both. Employees escalate decisions; they don't take them.

## Three repos and one local store

| Kind | What | Changes | Home |
|---|---|---|---|
| Product code | Pipelines, UI, experiment code | Branches and releases | `alto` |
| Product state | Stances, book, orders, health, shadow and experiment stores | Every run, written by the product | Data repo (`news_server` today), branch `live` only |
| Company records | Roles, policies, tasks, experiments, versions, decisions, briefs | Daily, by employees and the owner | `alto_hq` (this repo), branch `main` only |
| Employee runs | Agent session meta, transcripts | Every agent run | `alto_runs/`, local, never in git |

Company records are not in `alto`, so a status change never waits for a code
release, and code branches never carry stale copies of the paperwork.

## Verticals

| Vertical | Owns |
|---|---|
| Management | The daily brief, the approval queue, policies, budgets, owner decisions |
| Operations | The product running correctly today: incidents, repairs through owned commands, waivers |
| Engineering | Code changes and releases |
| Research | Finding better versions (experiments) and watching the live one (parity, decay) |
| Product | What Alto is: the version registry, champion vs challengers, promotion |
| Audit | Whether the checks work: rebuilds from scratch, planted defects, coverage. Reports to the owner, outside the other verticals. |

## The rules

1. **Every item has a permanent ID that encodes its type and creation time.**
   `<TYPE>-<YYYYMMDD>-<HHMM>-<slug>`, e.g. `T-20261015-1432-write-guard`.
   No shared counter, so two sessions or machines never collide.

   | Prefix | Item | Lives in |
   |---|---|---|
   | `T` | Engineering task | `engineering/tasks/` |
   | `R` | Research experiment | `research/experiments/` |
   | `C` | Cohort | `research/cohorts/` |
   | `I` | Incident | `operations/incidents/` |
   | `W` | Waiver | `operations/waivers/` |
   | `D` | Owner decision | `org/decisions/` |
   | `A` | Audit | `audit/samples/` |
   | `P` | Process change to these conventions | `org/changes/` |
   | `E` | Epic: a goal and its stories, before they are tasks | `org/epics/` |
   | `v<n>` | Product version | `product/versions/` |

2. **The ID is the join key across repos.** Nothing links by path.

   | Item | `alto` | Data repo | `alto_hq` |
   |---|---|---|---|
   | `T-…` | branch `eng/T-…` | — | `engineering/tasks/<year>/T-…/` |
   | `R-…` | branch `exp/R-…` | `experiments/R-…/` | `research/experiments/<year>/R-…/` |
   | `v<n>` | branch `staging/v<n>`, tag `v<n>` | `shadow/v<n>/` | `product/versions/v<n>/` |

   Every agent run records the item IDs it worked on.

3. **Items never move.** Status is a field in the item's file, not its folder.
   When work changes vertical (an incident needs code), a new item is created
   there with `spawned_from: <id>`. Paths and links never break.

4. **Authored and generated files are separate.** Anything computed (indexes,
   the approval queue) lives under a `_generated/` folder, is rebuilt by a
   command, and is never edited by hand. When a view and an item disagree,
   the item wins.

5. **Every file declares its schema** in frontmatter (`schema: task/v1`). One
   validator checks the repo. A format change is a schema bump plus a
   migration, never a silent edit.

6. **High-volume folders are split by year** from the start
   (`incidents/2026/…`, `briefs/2026/10/…`).

7. **A folder is created when its first item arrives.** The tree below is the
   full shape; only folders with work in them exist.

## The tree

```
alto_hq/
├── README.md                          # this page
│
├── org/                               # MANAGEMENT
│   ├── verticals.yaml                 # verticals → roles → status, renamed_from, superseded_by
│   ├── policies/
│   │   ├── authority.yaml             # action class → auto | propose | owner-only
│   │   ├── trust.yaml                 # role@version → trust level, earned by outcomes
│   │   └── budgets.yaml               # tokens/$ per role per day, per task
│   ├── decisions/<year>/D-….md        # every owner decision: what, why, items covered
│   ├── epics/<year>/E-….md            # high-level plans; stories become tasks only when next
│   ├── changes/<year>/P-….md          # proposed changes to these conventions
│   ├── schemas/<type>.v<n>.yaml       # the required fields of every file type; item.v1.yaml first
│   └── CHANGELOG.md                   # convention versions (hq/v<n>) and what each changed
│
├── roles/                             # the employees: one folder per role, never per instance
│   └── <vertical>/<role>/
│       ├── role.md                    # definition; frontmatter: id, version, model, tools, budget
│       ├── CHANGELOG.md               # why each version changed
│       ├── notes.md                   # how this role works best: lessons runs proved, curated
│       └── evals/                     # cases a new version must pass before use
│
├── management/
│   ├── briefs/<year>/<month>/<date>.md    # the daily brief
│   └── _generated/approvals.md            # every item with status awaiting_owner
│
├── operations/
│   ├── incidents/<year>/I-…/
│   │   ├── incident.md                # verdict that found it, root cause, defect class, status
│   │   └── repair.md                  # owned command used, its output, the check passing again
│   ├── runbooks/<defect-class>.md     # defect class → owned repair command, risk tier
│   └── waivers/W-….md                 # accepted known issue, with an expiry date
│
├── engineering/
│   ├── tasks/<year>/T-…/
│   │   ├── task.md                    # goal, change kind, status, claim
│   │   ├── acceptance.md              # the check, written and approved before code
│   │   ├── plan.md                    # dev: one-page map and design, before code
│   │   ├── attempts/<n>/diagnosis.md  # written when an attempt stops; at most 2
│   │   ├── handoff.md                 # dev: commits, acceptance check outputs, what was not done
│   │   └── evidence.md                # QA result, golden replay, merge commit
│   └── releases/<YYYY-MM-DD>.md       # what landed, linking its tasks (v<n>.md once versions exist)
│
├── research/
│   ├── protocol/protocol-v<n>.md      # evaluation rules: costs, slippage, liquidity, holdout
│   ├── cohorts/C-…/                   # immutable: build script, csv, hash
│   ├── experiments/<year>/R-…/
│   │   ├── plan.md                    # pre-registered: question, cohort, protocol, success criterion
│   │   ├── results/                   # self-contained summary and metrics
│   │   └── conclusion.md              # outcome; the candidate version if it won
│   └── guardianship/<year>/….md       # live-vs-backtest parity and decay reports
│
├── product/
│   ├── registry.yaml                  # champion and challengers; changed only by a promotion decision
│   └── versions/v<n>/
│       ├── version.md                 # kind, layers, source items (R-, T-)
│       ├── shadow.md                  # criterion, window, start, restarts, result
│       └── promotion.md               # promoted | dropped | rolled_back, with its D- decision
│
├── audit/
│   ├── samples/<year>/A-…/            # rebuild-from-scratch and planted-defect results
│   └── coverage.md                    # which defect classes have a check
│
└── _generated/                        # indexes rebuilt from the items; never hand-edited
    ├── items.jsonl
    └── by_status.md
```

Employee runs, local and outside git:

```
alto_runs/<year>/<month>/<day>/<run-id>/
    meta.json        # role id@version, model, item ids, start/end, tokens, cost, outcome
    transcript/      # kept 90 days; meta.json kept forever
alto_runs/index.jsonl   # one line per run, append-only
```

## Change kinds

Every engineering task and product version declares one kind. The kind sets
the evidence it needs.

| Kind | Examples | Evidence |
|---|---|---|
| `decision` | Stance logic, prompts, model, ranking, target weights, trading rules, new inputs; any fix that changes stances or trades | Research evidence, then shadow, then owner promotion |
| `user-facing` | UI, cockpit, reports | Evidence pack with screenshots; owner looks |
| `internal` | Bug fix, refactor, new check, infrastructure | Tests, and the golden companies' outputs unchanged |

A product version names the layers it changes: `stance` (documents →
analysis → stance), `trading` (stances → triggers → ranking → weights →
proposal), `ui`. A trading-only challenger reads the champion's stances.

## Branches in `alto`

| Branch | Lifetime | Moves by |
|---|---|---|
| `live` | Permanent; production on the Mac and the server | Fast-forward to a staged commit, or a hotfix. Owner only. |
| `develop` | Permanent; integration | `eng/` merges after the owner reviews the evidence |
| `eng/<T-id>` | About a day | Merged into `develop`, then deleted |
| `exp/<R-id>` | Weeks | Never merged. A winner is rebuilt through `eng/` on `develop`. |
| `staging/v<n>` | The shadow period | Promoted (`live` fast-forwards to it, tag `v<n>`) or dropped |
| tag `v<n>` | Permanent | Marks a release; the version stamp on every stance |

Hotfix: `eng/<T-id>` from `live`, merged to `live` (version `v<n>.<m>`), then
to `develop`.

## Members and member versions

- **A role is a member type; instances are runs.** Three engineers at once are
  three runs of `engineering/engineer`. Different expertise is a different
  role (`engineer-stance`, `engineer-trading`), not an instance.
- **A role version is its `role.md` version.** Every run records
  `role@version` and the model.
- **A new role version passes the role's `evals/` before use.** A minor change
  (wording, budget) keeps the role's trust level. A major change (scope,
  tools, model) resets it to propose-only until outcomes earn it back.
- **Claims.** The run working an item writes `claimed_by: <run-id>` and
  `lease_until` into the item. An expired lease frees the item, so a crashed
  session never locks it and two runs never take the same one.
- **Claude Code** loads agents from `alto/.claude/agents/`. Those files are
  generated from `roles/` at the pinned versions.

## How these conventions change

The structure and schemas are expected to change as the company learns. They
change by one route only: friction and warnings, a proposal, owner approval, a
migration, the validator passing. Never by an employee's ad-hoc edit.

- **Minimal schemas.** A field is required only when a tool or a decision
  reads it. Everything else is free text in the body.
- **Unknown fields warn, they don't fail.** The validator counts them. A field
  that keeps appearing is a candidate for the schema; a required field that is
  always empty is a candidate for removal.
- **Friction is recorded where it happens.** Closing any item takes an
  optional `friction:` line: what the template lacked, or what had to be
  worked around.
- **Changes are `P-` items.** Each states the problem with the item IDs that
  hit it, the change, and the migration. The chief of staff batches them from
  friction lines and warning counts; the owner approves the batch.
- **One version at a time.** The conventions are versioned (`hq/v<n>`, in
  `org/CHANGELOG.md`). A schema bump ships with a migration that moves every
  existing file, and the validator must pass over the whole repo.
- **On a schedule.** Weekly at first, monthly once settled.

The current version is `hq/v2`.

## Edge cases

| Case | Handling |
|---|---|
| Two sessions create items at the same moment | Time-based IDs with a slug; no shared counter |
| An incident needs code | It spawns a `T-` task. The incident closes when the task is merged and the original check passes again. |
| An approved plan or acceptance check is edited | The approval records the file's hash. A changed hash returns the item to `awaiting_owner`; results cite the hash they ran under. |
| A task fails twice | Each attempt writes a diagnosis; status becomes `needs_owner`. A retry needs a new acceptance check or approach. |
| A branch is abandoned | Item status `abandoned`, branch deleted, record kept. A cleanup check flags any branch with no open item. |
| Experiment data deleted by retention, result still cited | `results/` stands alone: summary, metrics, cohort hash, protocol version |
| A cohort needs correcting | Cohorts are immutable. A new `C-` with `supersedes:`; old results stay tied to the old one. |
| The evaluation protocol changes | A new `protocol-v<n>`. Results compare only within one protocol version. |
| Two challengers in shadow | Each has its own `shadow/v<n>/` store and registry entry, against the same champion |
| A shadow run is interrupted | `shadow.md` counts restarts. Too many invalidates the shadow rather than quietly extending it. |
| A promoted version is rolled back | `promotion.md` → `rolled_back` with a `D-`; `live` moves to the previous tag; the registry champion reverts |
| A hotfix | Version `v<n>.<m>`, recorded in the registry like any version |
| A role is renamed or split | Stable role IDs. Rename records `renamed_from`; a split retires the old role with `superseded_by`. Old runs still resolve. |
| A vertical is added | An entry in `verticals.yaml`, then `roles/<new>/` and `<new>/`. Nothing moves. |
| The owner acts | Recorded as a decision or a run with role `owner` |
| Secrets in transcripts | Transcripts stay in `alto_runs/`, never in git. Records here hold summaries only. |
| A file format needs a new field | Schema bump, validator, migration |
| A branch is rebased and its commit disappears | Evidence records the merge commit on `develop` or `live`, never a branch commit |
| No brief by 08:30 | A watcher on the other machine detects the absence and opens an incident |
| A generated view disagrees with the items | Views are rebuilt from items; a hand edit to `_generated/` is overwritten and flagged |
