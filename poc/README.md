# Proof of Concept: Multi-service Airflow DAGs

Real, working DAGs that orchestrate cross-service business workflows.
These exist to demonstrate **what** gets scheduled — the question of *when*
is left to the learner in `../learner/`.

## What's here

- `docker-compose.yml` — Airflow 1.10 (Puckel image) + Postgres + httpbin for local request testing.
- `.env.example` — template for the API credentials the DAGs read from the environment.
- `dags/stripe_mailchimp_promo.py` — four-step coupon-to-campaign workflow (Stripe ↔ Mailchimp).
- `dags/stripe_portal_session_mandrill.py` — create a Stripe customer-portal session and notify the customer via Mandrill.
- `dags/http_examples.py` — minimal `SimpleHttpOperator` example against a public endpoint.

## Running locally

```bash
cp .env.example .env
# edit .env and set STRIPE_API_KEY, MAILCHIMP_API_KEY, MAILCHIMP_LIST_ID,
# MANDRILL_API_KEY, plus the recipient/customer fields.

docker compose up -d
# Airflow UI on http://localhost:8080 (admin / admin), httpbin on http://localhost:8081
```

Trigger a DAG from the UI (they all have `schedule_interval=None`, so they
do not auto-run). Pipe values flow between tasks via XCom.

## Notes

- The Puckel image is pinned at `1.10.9` to match the original PoC. For a
  current setup, switch to `apache/airflow:2.x` — the DAGs need an import
  path update (`airflow.providers.http.operators.http`) but the logic is the same.
- All API keys, list IDs and customer IDs come from the environment. There
  are no defaults: the DAGs will fail fast if a key is missing, which is the
  intended behaviour.
- Mailchimp's API requires the data-center suffix to match the key (e.g.
  `…-us2` ↔ `https://us2.api.mailchimp.com/...`). Set `MAILCHIMP_DC=us2`
  accordingly.
