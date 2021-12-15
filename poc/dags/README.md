# DAGs

Three DAGs, picked to be self-contained illustrations:

- **`stripe_mailchimp_promo.py`** — the most interesting one. Five tasks, two
  diamond-shaped data dependencies, two external services. This is the kind
  of cross-service workflow Gombaz wants to schedule intelligently.
- **`stripe_portal_session_mandrill.py`** — short, two-step. Shows a
  one-shot personalised customer interaction (portal-link mail).
- **`http_examples.py`** — trivial `SimpleHttpOperator` against local
  httpbin, useful as a smoke test for the Airflow setup itself.

All DAGs have `schedule_interval=None` and must be triggered manually.
Credentials come from environment variables (see `../.env.example`); the
DAG will fail-fast on import if something is missing.
