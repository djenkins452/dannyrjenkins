# Content audit — 2026-11-08

Migration `website/migrations/0020_content_audit_2026_11.py` corrects these
production fields. Each rule fires only when the whole stored value still
equals the text captured here; otherwise it is skipped and reported.

| Record | Field | Correction |
| --- | --- | --- |
| HomepagePillar INNOVATION / Whole Life Journey | `body` | Approved summary (intended benefits, not results) |
| HomepagePillar INNOVATION / AI Chief of Staff | `body` | Approved summary (decision-support concept) |
| Page `profile` | `seo_description` | Approved Profile meta description |
| ResumeSection `general` / HIGHLIGHTS | `content` | Same seven highlights, one bullet each (was one bullet with seven paragraphs) |
| ConnectPage | `submit_button_label` | `SubmitSend message` or `Submit` → `Send message` (production already held `Send message`) |

`pre_change_production_values.json` holds the exact prior values, captured
read-only from production.

## Rollback

```bash
python manage.py migrate website 0019
```

Run it against production (for example via `railway ssh`). This restores the
first four rows only if they still hold the corrected text; the submit label
is never reverted. Reverting the Git commit alone does **not** change
database content. To restore by hand, paste values from the JSON into
`/admin/`.
