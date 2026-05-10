# DRJ Domain Registry

A **domain** is a user-facing concept area on the public site — something that has its own page or its own name in the top nav. Being in `INSTALLED_APPS` does not make something a domain; this site has exactly one first-party Django app (`website`), and inside that app the domains are organized by what a visitor reads, not by Django machinery.

Each domain entry below names the canonical model(s), the page(s) it powers, what state / outputs it produces, and its dependencies. Status is **production** unless noted.

---

## 1. Home

One-line purpose: the landing page — name, headshot, positioning copy, vision section, two-column split (Enterprise Leadership left / Innovation right) with three pillars each, closing link to Profile.

URL: `/` → `website.views.home`. Template: `website/templates/home.html`.

Canonical models:
- `SiteConfig` (singleton, pk=1) — owns `homepage_headline`, `homepage_positioning_line`, `homepage_subheadline`, `vision_eyebrow`/`vision_heading`/`homepage_vision`, `enterprise_column_eyebrow`/`enterprise_column_heading`/`enterprise_section_intro`/`enterprise_section_closing`, `innovation_column_eyebrow`/`innovation_column_heading`/`innovation_section_intro`, and `read_profile_link_label`.
- `HomepagePillar` — the three bullets under each column. Filtered by `category` (`ENTERPRISE` vs `INNOVATION`), ordered by `order`.

Dependencies: none — Home composes from `SiteConfig` + `HomepagePillar` directly. It does not read from `EnterpriseOverview` or `InnovationOverview` (those drive their own pages).

Status: production.

---

## 2. Profile

One-line purpose: executive narrative page — title, intro, ordered narrative blocks.

URL: `/profile/` → `website.views.profile`. Template: `website/templates/profile.html`. Verbose name in admin: "Profile pages".

Canonical models:
- `Page` (slug must be `'profile'`) — title, eyebrow, intro, SEO fields.
- `NarrativeBlock` (FK to `Page`) — eyebrow / heading / body, ordered by `order`.

The `Page` model is generic by design (the docstring notes "Used for /profile/ and future narrative pages") but only `slug='profile'` is currently routed.

Dependencies: none.

Status: production. The `placeholder` view in `views.py` is the only other intended user of `Page`; it is unrouted dead code from Phase 1 — flag for cleanup.

---

## 3. Enterprise Leadership

One-line purpose: the operator's HR-operations remit at scale — hero, Scope, Impact, three function blocks (Compensation, HRIS, Payroll), closing system-integration block.

URL: `/enterprise-leadership/` → `website.views.enterprise_leadership`. Template: `website/templates/enterprise_leadership.html`.

Canonical models:
- `EnterpriseOverview` (singleton) — page chrome: `page_eyebrow`, `hero_heading`, `hero_lead`, `scope_label` (drives both eyebrow and H2 of Scope block), `scope`, `impact_label`, `impact`, `function_section_eyebrow`, `function_section_heading`, `system_integration_eyebrow`, `system_integration_heading`, `system_integration`.
- `EnterpriseFunction` — one row per function (Compensation / HRIS / Payroll). Per-row labels (`responsibilities_label`, `platforms_and_tools_label`, `role_and_accountability_label`) plus the three body fields (`responsibilities`, `systems_led`, `organizational_role`). Ordered by `order`.

Dependencies: none. The Home page advertises this domain via `enterprise_column_*` on `SiteConfig` but does not read from `EnterpriseOverview` directly.

Status: production.

---

## 4. Innovation

One-line purpose: Beacon Innovation positioning, Whole Life Journey overview, Data → Signals → Decisions architecture diagram, AI Chief of Staff concept, "what this demonstrates" closing.

URL: `/innovation/` → `website.views.innovation`. Template: `website/templates/innovation.html`.

Canonical model:
- `InnovationOverview` (singleton) — every visible string on the page, including the six SVG diagram labels (`diagram_box_1..3_label`, `diagram_caption_1..3`), is a CharField. The architecture diagram itself is inline SVG in the template (not a CMS image).

Dependencies: links out to a specific case study slug at the bottom (`unified-life-wlj`) via `wlj_case_study_link_label`.

Status: production.

---

## 5. Case Studies

One-line purpose: a structured library of operator-led work, each with a fixed Problem → Role → Approach → Outcome shape.

URLs:
- `/case-studies/` → `website.views.case_study_index` — list page.
- `/case-studies/<slug>/` → `website.views.case_study_detail` — per-study page.

Canonical models:
- `CaseStudiesIndexPage` (singleton) — index-page chrome: `page_eyebrow`, `page_title`, `page_lead`, `read_more_label`, `empty_state_label`. Verbose name in admin: "Case Studies".
- `CaseStudy` (per-record) — `title`, `slug`, `category` (`ENTERPRISE` | `INNOVATION`), `summary`, four body fields (`problem`, `role`, `approach`, `outcome`), `published`, `published_at`, `order`, SEO. Verbose name in admin: "Case Studies — Entries".

The eight per-detail-page labels (Problem / The problem / Role / My role / etc.) and two breadcrumbs and the chip suffix all live on `SiteConfig` under the collapsed "Case Studies — universal labels" fieldset. They apply uniformly to every `CaseStudy`.

Dependencies: none.

Status: production. Four entries currently published.

---

## 6. Perspectives

One-line purpose: short-form arguments about HR operations — written as an operator, not a blog.

URLs:
- `/perspectives/` → `website.views.perspective_index`.
- `/perspectives/<slug>/` → `website.views.perspective_detail`.

Canonical models:
- `PerspectivesIndexPage` (singleton) — index-page chrome (mirrors `CaseStudiesIndexPage`). Verbose name: "Perspectives".
- `Perspective` (per-record) — title, eyebrow, deck, lead, closing, ordered `PerspectiveSection` children, publication metadata, SEO. Verbose name: "Perspectives — Entries".
- `PerspectiveSection` (FK to `Perspective`) — heading + body, ordered by `order`.

Three universal labels (back link, closing eyebrow, back-to-all link) live on `SiteConfig` under "Perspectives — universal labels".

Dependencies: none.

Status: production.

---

## 7. Connect

One-line purpose: contact form page. Submissions are emailed to the operator and never stored.

URL: `/connect/` → `website.views.connect`. Template: `website/templates/connect.html`.

Canonical model:
- `ConnectPage` (singleton) — page hero (`page_eyebrow`, `page_title`, `intro`), `form_prelude`, six form-label fields (`name_label`, `email_label`, `inquiry_label`, `message_label`, `message_optional_label`, `submit_button_label`), success state (`success_heading`, `success_body`). Verbose name: "Connect".

The form itself is `website.forms.ContactForm` — not model-backed. Inquiry choices (Executive conversation / Role discussion / Advisory or speaking / Resume request) are defined in code, not admin, because they shape backend handling. Submissions are sent via `EmailMessage` to `settings.EMAIL_HOST_USER` with `reply_to=[user.email]` so a reply goes back to the visitor, not the SMTP account.

Legacy mailto-CTA fields (`conversation_*`, `resume_*`) remain on `ConnectPage` for schema compatibility but are not rendered. They live in a collapsed admin fieldset marked "no longer rendered."

Dependencies: requires `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` env vars in production. Without them, the email backend silently falls back to console (see `resume/settings.py` lines 190–193) — this is intentional for local dev but means a deploy without those env vars set would not actually deliver mail.

Status: production.

---

## 8. Resume

One-line purpose: tailored resume pages reachable at `/resume/<slug>/`. Not linked from public nav. URL is shared by the operator on request.

URL: `/resume/<slug>/` → `website.views.resume_version`. Only renders if `is_active=True` on the `ResumeVersion`.

Canonical models:
- `ResumeVersion` — `slug`, `name` (deck under H1), `type` (`HR_OPS` | `TOTAL_REWARDS` | `GENERAL`), `is_active`, `updated_at`. Verbose name: "Resume — Versions".
- `ResumeSection` (FK to `ResumeVersion`) — `section_type` (`SUMMARY` | `CURRENT_ROLE` | `PRIOR_ROLES` | `EDUCATION` | `HIGHLIGHTS` | `CUSTOM`), optional `heading` override, `content` HTML body, `order`.

Page chrome (eyebrow prefix `"Resume"`, the H1 which uses `SiteConfig.brand_wordmark`, and `resume_print_button_label`) lives on `SiteConfig` under "Resume — page chrome".

Dependencies: reads `brand_wordmark` and the two resume-chrome fields from `SiteConfig`.

Status: production.

---

## Cross-cutting: Global chrome

Not a "page" but rendered on every page — the top header (brand wordmark, mobile menu toggle, seven nav labels) and the footer (year + owner name, contact email, LinkedIn URL + label). Lives entirely on `SiteConfig`. Edited via the "Header — brand & navigation" and "Footer — contact & social" fieldsets at the top and bottom of the SiteConfig admin form.

The staff-only help panel (`website/templates/partials/admin_help.html`) is also rendered on every page but only when `request.user.is_staff`. It is admin-internal text, not user-facing content, so it is exempt from Law #5 ("Every visible string must be configurable through admin").

---

## Support apps

Apps present in `INSTALLED_APPS` but **not** domains:

- `django.contrib.admin` — admin UI infrastructure.
- `django.contrib.auth` — superuser login (the only auth surface; no public account system exists or is planned).
- `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages` — Django plumbing.
- `django.contrib.staticfiles` — paired with WhiteNoise for production static serving.
- `tinymce` (django-tinymce) — heading-stripped rich-text editor for HTMLField bodies.
- `whitenoise.runserver_nostatic` — disables Django's dev static handler so WhiteNoise serves locally too.

The `website` app is the only first-party app and contains every domain above. There is no `apps/` directory pattern here. Being in `INSTALLED_APPS` does not make something a domain; the domains are the eight pages plus the cross-cutting global chrome.

---

## Where truth lives — quick lookup

| Domain | Singleton page-chrome model | Per-record model |
|---|---|---|
| Home | `SiteConfig` (homepage_* fields) | `HomepagePillar` |
| Profile | `Page` (slug='profile') | `NarrativeBlock` |
| Enterprise Leadership | `EnterpriseOverview` | `EnterpriseFunction` |
| Innovation | `InnovationOverview` | — |
| Case Studies | `CaseStudiesIndexPage` | `CaseStudy` |
| Perspectives | `PerspectivesIndexPage` | `Perspective` + `PerspectiveSection` |
| Connect | `ConnectPage` | — (`ContactForm` is request-only) |
| Resume | `SiteConfig` (resume_* fields) | `ResumeVersion` + `ResumeSection` |
| Global chrome | `SiteConfig` (nav_*, footer_*, brand_*) | — |

Universal cross-record labels (case study eyebrows / perspective eyebrows / resume page chrome) all live on `SiteConfig` under collapsed fieldsets.

---

Last updated: 2026-05-04.
