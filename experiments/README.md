# Experiments

These plots are produced by running the learner from `../learner/` against
six synthetic information processes. Each subfolder contains:

- `calls.png` — the agent's chosen call times across a test batch, drawn as
  vertical ticks against the underlying process curve `m(t)`.
- `number.png` — the cumulative number of calls over time.

The selected runs all use the configuration `4 epochs × 48 iters × batch 12`
where comparable, so the same training budget is applied across processes.
The `shift` and `square` cases use `4×28×12` because the larger setting was
not run for those processes.

## The six processes

| Folder      | `m(t)` shape                          | What it represents                         |
| ---         | ---                                   | ---                                        |
| `constant`  | flat                                  | Baseline. Optimal policy is uniform calls. |
| `random`    | noise around a constant               | Same baseline plus stochasticity in feedback. |
| `step`      | five Heaviside jumps at fixed days    | Periodic bursts of business activity.      |
| `shift`     | Heaviside jumps shifted in time       | Same shape, late arrival — tests whether the agent re-aligns. |
| `sqrt`      | `m(t) = √t`                           | Slowly growing intensity (e.g. seasonal ramp). |
| `square`    | square wave                           | Strict on/off business-hours pattern.      |

## How to read the plots

The `calls.png` view is the most informative one. A successful policy will
**concentrate ticks where `m(t)` is high** and stay quiet during low-intensity
intervals. For `constant`, ticks should be roughly equispaced. For `step`,
ticks should cluster shortly after each jump. For `sqrt`, density of ticks
should rise over time.

The `number.png` view shows the same information as a step function and is
useful for comparing total budget consumption across processes.

## Reproducing

See `../learner/README.md` and `../learner/MODIFICATIONS.md`. Each plot
corresponds to a different `recall(item, t)` definition inside
`tpprl/exp_teacher.py`, swapped in by editing that one function before
training. The full grid of runs (more parameter combinations per process) is
not shipped here — only the representative panel above.
