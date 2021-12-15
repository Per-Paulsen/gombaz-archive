# Gombaz (archived)

> Archived snapshot of a research-flavoured side project, December 2021.
> No longer maintained — published as a portfolio reference.

**Learning *when* to call business APIs, instead of running them on a fixed schedule.**

Cron is dumb. A nightly Stripe report at 03:00 is fine until the day customers
are doing something interesting at 02:55. A weekly Mailchimp campaign goes out
at the same hour even if nobody is reading mail that hour. Gombaz is a small
research-flavoured project that asks: can a model *learn* the optimal moment
to fire a service call from observed data?

The pieces in this repo:

| Folder         | What it shows                                                                 |
| ---            | ---                                                                           |
| `docs/`        | The problem, an architecture sketch (BPMN), the conceptual idea.              |
| `poc/`         | Real, working Airflow DAGs that orchestrate Stripe + Mailchimp + Mandrill workflows. The "what gets scheduled". |
| `learner/`     | A patch against [`Networks-Learning/tpprl`](https://github.com/Networks-Learning/tpprl) (NeurIPS 2018) that adapts the spaced-repetition learner from "many items / human forgetting" to **one item / artificial information processes** — the "when to schedule". |
| `experiments/` | Plots from running the adapted learner against six different information processes (constant, random, shift, sqrt, square, step). |

## The story in three steps

1. **Multi-service workflows are real and chained.** See
   `poc/dags/stripe_mailchimp_promo.py`: create a Stripe coupon → derive a
   promotion code → create a Mailchimp campaign → inject the code into the
   campaign body → send. Four API calls across two services with data
   dependencies between them.
2. **Their optimal firing time is not constant.** A campaign that depends on
   a coupon should fire when subscribers actually engage, not at a fixed cron
   slot. The "right time" is a function of an underlying *information
   process* that we usually only observe through events.
3. **It can be learned.** The `learner/` directory adapts a published Deep RL
   model for Marked Temporal Point Processes (originally trained to schedule
   spaced-repetition reviews) to schedule a single business service against
   synthetic information processes. The plots in `experiments/` show what the
   policy looks like under each process.

## Status

This is a proof-of-concept / portfolio project, not a maintained product.
The Airflow setup uses `puckel/docker-airflow:1.10.9`, which is the version
the original PoC was built on; a real deployment would target a current
Airflow 2.x image. The learner is built on TensorFlow 1.8 (matching the
upstream paper code).

## Acknowledgements

The learner is a derivative of:

> Upadhyay, U., De, A., Gomez-Rodriguez, M.
> *Deep Reinforcement Learning of Marked Temporal Point Processes.*
> NeurIPS 2018. [arXiv:1805.09360](https://arxiv.org/abs/1805.09360)

Upstream code: <https://github.com/Networks-Learning/tpprl>.
