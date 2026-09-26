# 05 · Conversion and funnels: CTAs, lead forms, proof, price, risk reversal, urgency, funnels

Wave 2 · agent F (files `01`, `lead-forms.yaml`, experiments) and continuation agent F2 (`02`, `03`, this index) · 2026-09-24. How a
page leads to action and does not deceive. Boundaries: the canon for forms and dark patterns — `../../ux-research/`; norms,
consents and proof approval — I (`../08-legal-trust-a11y/`); copy — text (`../../text-research/04-copy-by-block/`); presentation —
creative (conversion blocks — L0); event dictionary and A/B — P (F names the events); blocks — E (`../04-blocks/blocks.yaml`).
Not a legal opinion.

## Files

| File | What it covers | Lines |
|---|---|---|
| `01-cta-and-lead-capture.md` | CTA: one action and repetition along the storyline, one name, a secondary path, header, sticky on mobile; lead form: question protocol, presets by task and temperature, steps; quizzes and calculators (position for E); phone, call, **messengers in Russia as of 2026-09**, booking, chat; anti-spam without CAPTCHA; consent and events; “thank you”; **capture pop-ups and exit-intent — a position with conditions** | 578 |
| `02-proof-pricing-risk.md` | Which argument resolves which doubt and where it is placed; minimums for proof blocks; platform rating; honest substitutes when the inventory is empty; the on-site part of collection; price display, “from N ₽”, full cost, plans and comparison, “popular”, decoy, old price, annual billing; guarantee and a risk-free first step; honest urgency and the life of a promotion | 535 |
| `03-multi-page-funnels.md` | The funnel as a chain of steps: what is passed along, one name, presentation levels; ad → landing page → form → “thank you” → contact; webinar; waitlist; trial period; lead magnet and follow-up emails (the cost of unsubscribing); tag → lead → deal (consent log, offline conversions); repeat visit; multi-page site funnel; event references — `event:<id>` from P's dictionary | 458 |
| `lead-forms.yaml` | v1.0 (J; v0.9 — F): defaults (layout, validation, consents, anti-spam, hidden fields, “thank you”, events), 17 fields with `why`, 13 presets (`callback`, `consultation-request`, `quote-request`, `quiz-quote`, `calculator-inline`, `booking`, `b2b-request`, `event-registration`, `waitlist`, `lead-magnet`, `newsletter-subscribe`, `contact-message`, `trial-start`), placement, 12 prohibitions; reference from `page-plan` — `form.ref: lead-forms.yaml#<id>` | 486 |

Experiments: `../99-raw/experiments/F/01-quiz-forms-ru/` (15 Russian quiz and calculator pages, 10 valid: questions, fields,
consents, incentives, rolling deadlines; the forms were not submitted), `F/02-forms-cta-sample-m/` (summary of
`../02-site-types/pages.csv` M: preliminary — 66 rows, 40 pages; final — 140 rows, 70 pages, X2 recount `summary-final.tsv`). Notes —
`../99-raw/notes/wave2/F-notes.md`; report — `../99-raw/reports/wave2-F-report.md`.

## Workflow for the generator agent

1. Brief → the page's single action (`conversion.action`) and channels (`conversion.channels`; Russia — form and phone) → `01` §1, §6.
2. Form preset from `lead-forms.yaml` by task and traffic temperature; each field — with a `why` → `01` §3.
3. CTA and form placements along the storyline; a sticky CTA on a long mobile page → `01` §1.2, §2, §4.
4. Arguments — tailored to doubts at decision points, only from approved facts; no facts — honest substitutes → `02` §1.
5. Price, full cost, plans, guarantee, honest deadline → `02` §2–§4.
6. Steps after the form: “thank you”, confirmation, response time, emails, hidden fields, offline conversions → `01` §9–§10, `03`.

## Folder digest

1. One target action, many CTA placements; one action label for the whole page and the email sequence.
2. A form field stays only if the next sales step uses its answer; a service request — 2 fields, maximum 3 visible.
3. Quiz — when the answers change the offer (3–7 questions, honest progress, contact last); calculator — up to 3
   parameters (hard maximum 5), result without a phone number.
4. Russia 2026-09: channels — form and phone; messenger — MAX, Telegram and WhatsApp only as an addition and not as the only one.
5. Personal data consent — a separate unchecked checkbox with a log; anti-spam — honeypot, time trap, limits; no CAPTCHA.
6. Conversion — a server-confirmed success; “thank you” — status, timeframe, channel, one next step.
7. Capture pop-ups — on click; auto-show — non-modal after engagement and only by the client's decision; exit-intent — no.
8. Proof — at the decision point and only from facts; price — on the page and as the full cost; “popular” — based on data.
9. Guarantee — a contract clause next to the price and the form; urgency — only a real date or live remaining stock; after the deadline, the block disappears.
10. Tag → lead → deal: hidden fields, consent log and CRM statuses in Metrica; funnel success — lead quality.