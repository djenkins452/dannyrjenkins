# DRJ Prompt Library Index

Operational governance for `dannyrjenkins` — the personal executive resume / portfolio site at `dannyrjenkins.com`. Five working files plus this index.

## Why this exists

The site has accumulated a real architecture: structured singletons, per-record models with fixed sub-section ordering, an admin reorganized to mirror site nav, a "every visible string is in admin" rule. When the operator drops into a chat with an LLM and says "add a thing" or "fix this bug," the LLM should already know the rules — what a domain is, where truth lives, what's forbidden — without re-deriving them from the codebase every time.

These files are the LLM's onboarding material. The architecture / debugging mode prompts pull the laws and the domain registry into the system prompt; the LLM then has enough context to push back on requests that violate the rules and to direct fixes at the canonical source rather than wherever the symptom appeared.

## Files

### `03_REFERENCE/DRJ ARCHITECTURE LAWS.md`

Fourteen non-negotiable rules with rationale and a forbidden / required pattern pair for each. Topics include: admin DB as the single source of truth, headings live in CharFields not TinyMCE, singleton `pk=1` enforcement, structured fields vs freeform body, the `|default:` template fallback rule, no silent failures on side-effecting code, the fixture-is-bootstrap-only rule, `DEBUG` env-driven, modify-before-adding, admin ordering mirrors site nav, no async/queue infra, presentational changes don't generate schema migrations, and the deploy-to-prod-on-push reality. Read this whenever you propose a structural change.

### `03_REFERENCE/DRJ DOMAIN REGISTRY.md`

Eight domains (Home, Profile, Enterprise Leadership, Innovation, Case Studies, Perspectives, Connect, Resume) plus the cross-cutting global chrome. For each: URL, view, template, canonical singleton + per-record models, the universal labels that apply across records, dependencies on other domains, and status. Ends with a "Support apps" section that explicitly distinguishes what's in `INSTALLED_APPS` from what's actually a domain. Use this whenever you ask "where does the canonical value for X live?"

### `02_CLAUDE/DRJ CLAUDE ARCHITECTURE MODE.md` and `01_CHATGPT/DRJ CHATGPT ARCHITECTURE MODE.md`

System prompts for design / refactor sessions. ChatGPT version emphasizes architectural challenge — the AI should question whether the proposed change belongs in the existing model at all, or whether it's a parallel pipeline trying to sneak in. Claude version emphasizes implementation discipline — once a direction is agreed, the AI should stage the change in the right files in the right order, with the right migration shape (presentational via `get_form` overrides, structural via real migrations).

### `02_CLAUDE/DRJ CLAUDE DEBUGGING MODE.md` and `01_CHATGPT/DRJ CHATGPT DEBUGGING MODE.md`

System prompts for debugging. The shared workflow is six steps: Trace the symptom → identify the canonical source per the Domain Registry → audit upstream and downstream → root-cause → minimal fix → verify (route returns 200, default render unchanged, no schema migration if presentational only, no silent regression on a related route). Both versions include a Canonical-Source Map table derived from the Domain Registry so the AI can jump from "the case study Outcome heading is wrong" to "edit `SiteConfig.case_study_outcome_heading`" without searching.

## Files that are deliberately not in this library

**Signal Ontology** — this project has no signal / event-driven layer. There are no Django signal receivers (`@receiver`, `post_save`, `pre_save`), no event bus, no async queue. `bootstrap_prod` is procedural and runs once per deploy. A document describing a signal layer would be ceremonial, so the file is intentionally absent rather than stubbed.

**AI / Chief-of-Staff Mode** — the site does not use AI at runtime. There is no LLM call, no AI inference, no embeddings store, no vector DB. The only "AI" in the project is the operator using these prompts during development. The architecture-mode and debugging-mode files are about *how* to use AI to develop the project, not about an AI feature inside the project.

## Typical workflow

1. **Operator opens a chat with Claude or ChatGPT.** Pastes the relevant Mode file as the system prompt. For ChatGPT this goes in the "Custom Instructions" box; for Claude it goes at the top of the conversation. Both Mode files reference the Architecture Laws and the Domain Registry by name — the operator pastes those alongside if the model needs them in-context, or the model fetches them from the repo.

2. **Operator describes the problem.** Plain language. "The submit button on /connect/ should say Submit, not Request a Conversation." Or: "I want to add a press-quotes section to the Profile page."

3. **AI applies the rules.** Architecture mode pushes back if the request violates a law (e.g., "you'd be hardcoding a string — that's forbidden by Law #5; the right move is to add a CharField to ConnectPage and bind it via `|default:`"). Debugging mode traces the symptom to the canonical source per the Domain Registry, never patches the symptom site directly.

4. **AI produces structured output.** Architecture mode → Current State / Problem / Existing Systems Review / Proposed Change / Architectural Fit / Risk / Implementation Plan / Verification. Debugging mode → Trace / Canonical Source / Audit / Root Cause / Minimal Fix / Verify.

5. **Operator reviews, applies, validates.** Site rendering remains byte-equivalent unless the change is intentional. `manage.py check` is clean. Routes return 200. Push deploys to production.

## Maintenance

These files are written from the codebase as it stands today. When a major architectural shift lands (a new domain, a new model layer, a deprecated invariant), update the affected file in this library in the same commit. The "Last updated" footer on each file is the canary — if it lags the code, the file is suspect.

If you can't find a rule for a situation in the Architecture Laws, that's a signal: either the situation is genuinely novel (in which case add a law or note it as an open question for the operator) or the law exists but isn't sharp enough yet (in which case rewrite the existing law to cover the case).

---

Last updated: 2026-05-04.
