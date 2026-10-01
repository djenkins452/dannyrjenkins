"""Align published professional facts with verified current status (Sep 2026).

One-shot, reviewable content correction. Runs once on deploy via the
Procfile's `migrate` step, like any migration. It is the explicit, versioned
equivalent of an admin edit, not a fixture re-sync: it rewrites only the exact
stale sentences listed in CORRECTIONS and leaves every other word alone.

Corrections:
- Segal: the compensation case study presented the completed rebuild as work
  done with Segal. The Segal engagement is a separate, active redesign. The
  earlier rebuild stays as a completed accomplishment.
- Offer-stage loss: removed an unquantified outcome claim that is not
  supported by a defensible metric.
- Kronos -> Infor WFM: removed "no operational disruption" / on-schedule
  framing. Go-live was November 2025, after three readiness-based delays,
  with a managed defect list and ongoing stabilization.
- Payroll scale: "~$33M disbursed monthly" understated the verified
  $500M+ annual payroll.
- Official title word order: Director of HRIS, Compensation, and Payroll.

Safety:
- Substring replacement per (record, field). If the stale text is present it
  is replaced; if the corrected text is already present the rule is skipped
  (idempotent); if neither is present the field was edited in admin since,
  so it is left untouched and reported.
- Reverse migration swaps each correction back to the exact prior text.
  Exact prior field values are also archived in
  backups/fact-alignment-2026-09-30/pre_change_production_values.json.
"""

from django.db import migrations

# (model, lookup, field, stale text, corrected text)
CORRECTIONS = [
    (
        'casestudy', {'slug': 'compensation-transformation'}, 'role',
        'I led the rebuild end to end, reporting to senior HR leadership and '
        'partnering with Segal to accelerate the work and align to best practices.',
        'I led the rebuild end to end, reporting to senior HR leadership. '
        'Building on that foundation, I am now leading an active enterprise '
        'compensation redesign in partnership with Segal; that engagement is ongoing.',
    ),
    (
        'casestudy', {'slug': 'compensation-transformation'}, 'outcome',
        'Managers could clearly explain pay decisions. Recruiting saw a '
        'measurable reduction in offer-stage loss. Compensation moved',
        'Managers could clearly explain pay decisions. Compensation moved',
    ),
    (
        'resumesection', {'version__slug': 'general', 'section_type': 'SUMMARY'}, 'content',
        'roughly $33M disbursed monthly across three payroll cycles',
        'more than $500M in annual payroll across three payroll cycles',
    ),
    (
        'resumesection', {'version__slug': 'general', 'section_type': 'CURRENT_ROLE'}, 'content',
        '<strong>Director of Compensation, HRIS, and Payroll</strong>',
        '<strong>Director of HRIS, Compensation, and Payroll</strong>',
    ),
    (
        'resumesection', {'version__slug': 'general', 'section_type': 'CURRENT_ROLE'}, 'content',
        '~$33M disbursed monthly across three payroll cycles (monthly, biweekly, supplemental).',
        '$500M+ in annual payroll across three payroll cycles (biweekly, monthly, supplemental).',
    ),
    (
        'resumesection', {'version__slug': 'general', 'section_type': 'CURRENT_ROLE'}, 'content',
        'Delivered a full-lifecycle replacement of a legacy UKG Kronos deployment '
        'with Infor Workforce Management — RFP through vendor management, hard '
        'cutover deadline, no operational disruption.',
        'Executive sponsor of the replacement of UKG Kronos with Infor Workforce '
        'Management for 7,000–7,500 employees and contractors — delayed go-live '
        'three times until readiness criteria were met, went live in November 2025 '
        'at Kronos end of life with a managed defect list, and continue '
        'post-go-live stabilization under controlled governance (about 85% '
        'complete as of September 2026).',
    ),
    (
        'resumesection', {'version__slug': 'general', 'section_type': 'HIGHLIGHTS'}, 'content',
        'Kronos &rarr; Infor WFM cutover delivered on a hard end-of-life deadline '
        'with no operational disruption.',
        'Kronos &rarr; Infor WFM conversion for 7,000–7,500 employees and '
        'contractors, governed by readiness: go-live delayed three times to protect '
        'payroll, then completed in November 2025 at Kronos end of life with a '
        'managed defect list and controlled stabilization.',
    ),
]


def _apply(apps, pairs, direction):
    for model_name, lookup, field, old, new in CORRECTIONS:
        src, dst = pairs(old, new)
        Model = apps.get_model('website', model_name)
        for obj in Model.objects.filter(**lookup):
            value = getattr(obj, field) or ''
            label = f'{model_name}{lookup}.{field}'
            if src in value:
                setattr(obj, field, value.replace(src, dst))
                obj.save(update_fields=[field])
                print(f'  [{direction}] corrected {label}')
            elif dst in value:
                print(f'  [{direction}] already aligned {label}')
            else:
                print(f'  [{direction}] SKIPPED {label}: expected text not found (edited in admin?)')


def forwards(apps, schema_editor):
    _apply(apps, lambda old, new: (old, new), 'forward')


def backwards(apps, schema_editor):
    _apply(apps, lambda old, new: (new, old), 'reverse')


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0017_resume_assembly_v1'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
