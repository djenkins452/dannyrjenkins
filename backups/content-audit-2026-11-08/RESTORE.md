# Content audit — 2026-11-08

Migration `website/migrations/0020_content_audit_2026_11.py` corrects these
production fields. Each rule fires only when the whole stored value still
equals the text captured here; otherwise it is skipped and reported.

| Record | Field | Correction |
| --- | --- | --- |
| HomepagePillar INNOVATION / Whole Life Journey | `body` | Approved summary (intended benefits, not results) |
| HomepagePillar INNOVATION / AI Chief of Staff | `body` | Approved summary (decision-support concept) |
| HomepagePillar INNOVATION / Kairos Core HQ | `body` | Approved summary (stated as an aim, not a result) |
| Page `profile` | `seo_description` | Approved Profile meta description |
| ResumeSection `general` / HIGHLIGHTS | `content` | Same seven highlights, one bullet each (was one bullet with seven paragraphs) |
| ConnectPage | `submit_button_label` | `SubmitSend message` or `Submit` → `Send message` (production already held `Send message`) |

`pre_change_production_values.json` holds the exact prior values, captured
read-only from production.

## Verifying the deploy

The `migrate` step in the Procfile prints one line per rule:

- `corrected` — the stored text matched the captured value and was replaced.
- `already aligned` — the field already held the approved text. This is an
  acceptable result (the submit-label rules normally report it).
- `SKIPPED` — the stored text differs from both values, usually because it
  was edited in admin after capture. Nothing was changed. Investigate each
  one: check the field's stored value in `/admin/` and the rendered page, and
  decide whether it is already acceptable or needs a manual edit.

There is no required number of `corrected` lines; what matters is that every
rule ends `corrected` or `already aligned`, or a `SKIPPED` rule has been
checked by hand.

## Fixture and deployments

`website/fixtures/initial_content.json` was refreshed to match the content
captured here, with these corrections applied. Normal deployments keep
existing content: `bootstrap_prod` seeds the fixture only into an empty
database and never touches existing records. Running
`bootstrap_prod --rebuild-from-fixture` by hand is different: it overwrites
fixture records with the fixture text, so any admin edits made after
2026-11-08 would be lost.

## Rollback

```bash
python manage.py migrate website 0019
```

Run it against production (for example via `railway ssh`). This restores the
pillar, Profile, and highlights rows only if they still hold the corrected text; the submit label
is never reverted. Reverting the Git commit alone does **not** change
database content. To restore by hand, paste values from the JSON into
`/admin/`.
