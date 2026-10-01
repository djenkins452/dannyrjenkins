# Fact alignment — 2026-09-30

Migration `website/migrations/0018_align_professional_facts.py` corrected
stale professional facts in production content:

| Record | Field | Correction |
| --- | --- | --- |
| CaseStudy `compensation-transformation` | `role` | Segal shown as a current, ongoing redesign, separate from the completed rebuild |
| CaseStudy `compensation-transformation` | `outcome` | Removed unsupported offer-stage loss claim |
| ResumeSection `general` / SUMMARY | `content` | `~$33M monthly` → `$500M+ annual payroll` |
| ResumeSection `general` / CURRENT_ROLE | `content` | Title order, payroll scale, Kronos → Infor WFM go-live story |
| ResumeSection `general` / HIGHLIGHTS | `content` | Kronos → Infor WFM go-live story |

`pre_change_production_values.json` holds the exact field values as they were
in production immediately before the migration (captured from the live
rendered pages, which output these fields verbatim).

## Rollback

Preferred, reverses only the sentences this migration changed:

```bash
python manage.py migrate website 0017
```

Run it against production (for example `railway run` / `railway ssh`, or a
one-off Railway command). Reverting the Git commit alone does **not** change
database content.

Full restore of the exact prior values, if admin edits have happened since:
paste the values from `pre_change_production_values.json` into the matching
fields in `/admin/`.
