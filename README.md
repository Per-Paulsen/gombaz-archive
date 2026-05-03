# GombaZ (archived)

> Archived snapshot of a 2021 product prototype, pitched at UnternehmerTUM
> and to tech CEOs/CTOs in late 2021 / early 2022. No longer maintained.

**ML-powered service-orchestration platform — automating SaaS business
processes (pricing, marketing, subscriptions) where the model learns
*when* to fire each call from observed data, instead of running on a
fixed cron schedule.**

## The pitch in one paragraph

Modern SaaS stacks chain API calls across providers — create a Stripe
coupon, derive a promotion code, push it into a Mailchimp campaign, send
when subscribers are most likely to convert. Today this is hand-orchestrated
through cron jobs and Zapier-style schedulers. GombaZ asked: what if the
*timing* of each call were **learned** from outcome data instead of
hand-set? Same workflows, but the firing schedule emerges from a model
that watches what users actually do.

## The pieces in this repo

| Folder         | What it shows                                                                 |
| ---            | ---                                                                           |
| `docs/`        | The problem, an architecture sketch (BPMN), the conceptual idea.              |
| `poc/`         | Working Airflow DAGs orchestrating Stripe + Mailchimp + Mandrill workflows — the "what gets scheduled". |
| `learner/`     | A patch against [`Networks-Learning/tpprl`](https://github.com/Networks-Learning/tpprl) (NeurIPS 2018) adapting the spaced-repetition learner from "many items / human forgetting" to **one item / artificial information processes** — the "when to fire". |
| `experiments/` | Plots from running the adapted learner against six different information processes (constant, random, shift, sqrt, square, step). |

## The story in three steps

1. **Multi-service workflows are real and chained.** See
   `poc/dags/stripe_mailchimp_promo.py`: Stripe coupon → derive promotion
   code → Mailchimp campaign → inject code → send. Four API calls across
   two services with data dependencies between them.
2. **Their optimal firing time is not constant.** A campaign that depends
   on a coupon should fire when subscribers actually engage, not at a
   fixed cron slot. The "right time" is a function of an underlying
   *information process* that we usually only observe through events.
3. **It can be learned.** The `learner/` directory adapts a published Deep
   RL model for Marked Temporal Point Processes (originally trained to
   schedule spaced-repetition reviews) to schedule a single business
   service against synthetic information processes. The plots in
   `experiments/` show what the policy looks like under each process.

## Status

Prototype-stage product, pitched at UnternehmerTUM and to 5+ tech CEOs/CTOs
in late 2021 / early 2022. Not taken to production. The Airflow setup uses
`puckel/docker-airflow:1.10.9`, the version the PoC was built on; a real
deployment would target a current Airflow 2.x image. The learner is built
on TensorFlow 1.8 (matching the upstream paper code).

## Acknowledgements

The learner is a derivative of:

> Upadhyay, U., De, A., Gomez-Rodriguez, M.
> *Deep Reinforcement Learning of Marked Temporal Point Processes.*
> NeurIPS 2018. [arXiv:1805.09360](https://arxiv.org/abs/1805.09360)

Upstream code: <https://github.com/Networks-Learning/tpprl>.
