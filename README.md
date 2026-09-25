# SAASSP - DP Progress & AI-Assisted Feedback Module

A working implementation of the module described in `SAASSP_Proposal_Final.docx`,
`SAASSP_SRS.docx` and `SAASSP_SDD.docx`: students configure a module's assessment
structure, upload marks, get a continuous weighted DP progress percentage and
threshold band, and receive AI-assisted feedback (Gemini) after every upload.

This is real, runnable code - not a mockup. The DP calculation engine and the
full student flow are covered by automated tests (see "Running the tests" below).

## What's implemented

Matches the SRS use cases 1:1:

| SRS use case | Where |
|---|---|
| 3.2.1 Login | `app/auth.py` |
| 3.2.2 Register and Select Programme and Modules | `app/student.py` (`select_programme`, `select_modules`) |
| 3.2.3 Configure Assessment Structure | `app/student.py` (`configure_assessment`) |
| 3.2.4 Upload Assessment Mark | `app/student.py` (`upload_mark`) |
| 3.2.5 Receive AI-Assisted Feedback | `app/feedback_service.py`, invoked from `upload_mark` |
| 3.2.6 View DP Progress Dashboard | `app/student.py` (`dashboard`, `module_detail`) |
| 3.2.7 View Student Progress (Academic Staff, read-only) | `app/staff.py` |
| 3.2.8 Manage Programme and Module Data | `app/admin.py` (`programmes`) |
| 3.2.9 Manage User Accounts | `app/admin.py` (`users`) |

The deterministic core - weighted best-N-of-M DP progress, the six threshold
bands, and blip-tolerant trend classification - lives entirely in
`app/dp_engine.py`, separate from the AI Feedback Service, exactly as
specified in SDD Section 3.1 ("This engine never depends on the AI Feedback
Service").

**Not implemented** (out of scope per the SRS/SDD): module recommendations,
prerequisite/co-requisite checking, credit/graduation tracking,
machine-learning risk classification, lecturer-side assessment configuration,
and the conversational AI chatbot.

## Setup

```bash
cd saassp
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

By default the app uses a local SQLite file (`app/saassp.db`) so you can try
it with zero extra setup. To use MySQL instead (matching the SDD's deployment
target), set `DATABASE_URL` before running anything below:

```bash
# Windows/XAMPP example, matching the proposal's local dev setup:
export DATABASE_URL="mysql+pymysql://saassp_user:password@localhost/saassp_app"
```

To enable real AI-assisted feedback, set a Gemini API key:

```bash
export GEMINI_API_KEY="your-key-here"
```

Without it, the app still works fully - `upload_mark` just stores "AI feedback
wasn't available this time" instead of generated text, exactly as SRS 3.2.5's
Alternative Path specifies.

### Load the dataset and create accounts

```bash
python seed_data.py
```

This loads `data/programmes.csv`, `data/modules.csv` and
`data/programme_modules.csv` (the same dataset you provided), and creates:

- Admin: `admin@saassp.local` / `admin123`
- Academic Staff: `staff@saassp.local` / `staff123`

Students self-register from the login page.

### Run it

```bash
python run.py
```

Then open http://localhost:5000. Register a Student account, select a
programme and modules, configure a module's assessment structure, and upload
a mark to see DP progress and feedback appear.

## Running the tests

```bash
pip install pytest   # already in requirements.txt
pytest tests/ -v
```

- `tests/test_dp_engine.py` - 13 unit tests on the DP calculation engine in
  isolation: the weighted-progress formula, best-N-of-M displacement, all six
  threshold bands, and trend classification (including the exact "started
  badly, recovered" and "tolerates one reversal" scenarios worked through
  while designing this).
- `tests/test_app_smoke.py` - 2 integration tests that drive the real Flask
  routes (register → select programme → select modules → configure → upload
  marks) and check the number shown on the page matches what the engine
  itself computes, plus that the 100%-weighting validation actually blocks
  a bad configuration.

All 15 currently pass.

## Project layout

```
saassp/
  app/
    __init__.py          application factory
    models.py             SQLAlchemy models (SDD 4.1 data dictionary)
    dp_engine.py           DP Progress Calculation Engine (SDD 3.1)
    feedback_service.py    AI Feedback Service / Gemini client (SDD 3.1)
    auth.py                 Login / Register routes
    student.py              Student-facing routes
    staff.py                 Academic Staff routes
    admin.py                  Administration routes
    templates/                 Jinja2 templates (Bootstrap 5, UNIZULU navy/gold)
    static/css/style.css
  data/                        the CSV dataset you provided
  tests/
    test_dp_engine.py
    test_app_smoke.py
  seed_data.py
  run.py
  config.py
  requirements.txt
```

## Known gaps to close before a real deployment

- Passwords are hashed (Werkzeug) but there's no password-reset flow yet.
- CSRF protection (Flask-WTF) isn't wired in - add it before exposing this
  beyond local testing.
- The admin CSV importer trusts well-formed input; malformed CSVs will raise
  rather than showing a friendly per-row error.
- No pagination on the admin programme/user lists - fine for now, will need
  it once the real dataset (37 programmes, 120 modules) is fully loaded
  alongside a real cohort of users.
