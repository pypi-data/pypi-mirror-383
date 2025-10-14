# cadelphi

<p align="center">
  <img src="https://cadelphi.optiwisdom.com/static/img/cadelphi-logo.png" alt="cadelphi logo" width="220" />
</p>

<p align="center">
  <a href="https://www.optiwisdom.com" target="_blank" rel="noopener noreferrer">
    <img src="https://cadelphi.optiwisdom.com/static/img/optiwisdom-logo.png" alt="Optiwisdom logo" width="320" />
  </a>
</p>

cadelphi is a FastAPI-based toolkit for running Computerized Argument Delphi (CAD) sessions inspired by the
methodology described in the IEEE paper *Computerized Argument Delphi Method*. The application collects arguments,
walks participants through a structured three-step Likert voting flow, and provides an administrative console for
monitoring discussions.

![Cadelphi infographic](https://cadelphi.optiwisdom.com/static/img/cadelphi-infographic.png)

## Features

- 🌐 **Web interface for participants:** Contributors can submit optional arguments, rate existing arguments on a
  five-point Likert scale, and leave feedback during a guided three-step session.
- 🧠 **Adaptive selection strategies:** Configure random, positive-affinity, or negative-affinity argument sequences
  that mirror CAD literature on exposing participants to supportive or dissenting viewpoints.
- 🌍 **Bilingual experience:** The UI supports English and Turkish with an in-app language switcher. Seed data is
  provided in both languages so you can explore the workflow immediately.
- 🗃️ **Persistent storage:** SQLAlchemy models backed by SQLite capture participants, arguments, votes, and comments.
- 📊 **Rich admin console:** Review hierarchical topic trees, inspect votes and comments, visualise the argument graph
  with configurable edge metrics, and adjust system settings from a password-protected dashboard.
- 🛡️ **Security-minded defaults:** Argon2 password hashing, per-request CSRF tokens, session hardening, and guarded
  admin APIs reduce common attack surfaces.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\\Scripts\\activate
pip install --upgrade pip
pip install -e .
```

## Running the application

Launch the bundled Uvicorn entrypoint on port 7882:

```bash
cadelphi
```

When running on your workstation you can browse to `http://127.0.0.1:7882/`. On remote servers replace the host
with the machine's reachable address, for example `http://<your-server-ip>:7882/` for the participant portal and
`http://<your-server-ip>:7882/admin` for the admin console.

## Default account and sample data

On first start the database is populated with English and Turkish demonstration datasets covering two discussion
topics each. The default administrator credentials are:

- Username: `admin`
- Password: `password`

Sign in and update the password from the **Settings** page before using the system in production.

## Troubleshooting

### "SessionMiddleware must be installed to access request.session"

This assertion occurs when a request reaches the CSRF helper before Starlette's
`SessionMiddleware` has attached a session mapping to the request scope. Update
to the current release (or apply the same patch) so that the middleware checks
for the session mapping before touching it and gracefully skips token seeding
when the session is missing. If you maintain forks with custom middleware,
ensure that any logic accessing `request.session` either:

1. Runs inside middleware added **after** `SessionMiddleware`, or
2. Checks `"session" in request.scope` before dereferencing the property.

For manual hotfixes, edit `cadelphi/app.py` and replace the CSRF middleware with
the version that guards `request.scope.get("session")` and only calls
`ensure_csrf_token` when the result is a mutable mapping.

### "UNIQUE constraint failed: admin_settings.admin_username"

This error appears when the application tries to insert the built-in `admin` user even though the account already
exists in the database. Earlier revisions seeded the default administrator more than once during startup, so subsequent
launches hit SQLite's unique-constraint protection on the `admin_username` column.

The current codebase now checks for the username explicitly before attempting the insert. Upgrade to this release (or
remove any additional admin-seeding logic) and the server will start normally. If you previously ended up with multiple
rows in `admin_settings` because of local testing, delete the duplicates or remove the `.cadelphi/cadelphi.db` file so a
fresh database can be generated.

## Security considerations

- Admin passwords are hashed with `passlib[argon2]` for modern resistance against brute-force attacks.
- All form submissions include per-session CSRF tokens that are validated on the server.
- Admin-only JSON endpoints (graph data and summaries) enforce authentication and respond with `401 Unauthorized`
  when accessed without a valid session.
- Session cookies are signed by Starlette's `SessionMiddleware`; override the secret via the `CADELPHI_SECRET_KEY`
  environment variable for deployments.

## Reference

- Seker, Sadi Evren. "Computerized argument Delphi technique." *IEEE Access* 3 (2015): 368-380. https://ieeexplore.ieee.org/document/7089162

## Development tips

- Target Python 3.11+ with FastAPI and SQLAlchemy 2.0 style APIs.
- Use `uvicorn cadelphi.app:app --reload --port 7882` during development to enable live code reloading.
- Switch the backing database by setting the `CADELPHI_DB` environment variable to any SQLAlchemy-compatible DSN.

## What to do next

Need a quick checklist for validating the latest branding refresh and prepping a release? See
[docs/next_steps.md](docs/next_steps.md) for the recommended workflow from local testing through packaging and
deployment.

## License

Distributed under the MIT License.
