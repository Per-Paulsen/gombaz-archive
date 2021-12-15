# Modifications against `Networks-Learning/tpprl`

The upstream code is built around **Spaced Repetition** for human learning:
50 flashcards, each with its own forgetting curve `n_i(t) = n_0 · (1−α)^k`,
agent decides when to schedule the next review. Reward = recall probability
under an exponential forgetting model.

The Gombaz adaptation reframes the same model as **scheduling a single
business service against an unknown information process**. The changes below
are what makes that work.

## Files touched

| File                              | Lines changed | Nature                                |
| ---                               | ---           | ---                                   |
| `data/initial_difficulty.csv`     | 1             | 50 items → 1 item                     |
| `train-teaching.py`               | ~20           | Hyperparameter retune; new module     |
| `tpprl/exp_teacher.py`            | ~60           | Replace recall function; bookkeeping  |
| `tpprl/exp_teacher_save.py`       | new           | Save-aware variant of `exp_teacher`   |
| `analyze-spaced-repetition.py`    | ~70           | Add overlay plots of policy vs process |
| `tpprl/cells.py`                  | 3             | Comments only                         |
| `README.md`                       | 2             | Path fix                              |

## Why each change

### 1. One item instead of fifty

`data/initial_difficulty.csv` is reduced to a single value (`1.9310604`).
Rationale: a business service ("send promo campaign") is one entity that
fires repeatedly. Modelling it as 1 of 50 flashcards adds parameters that
have no real-world referent. The single value is treated by the rest of the
pipeline as the initial intensity scale of the (single) process.

### 2. Recall replaced by artificial information processes

In upstream `tpprl/exp_teacher.py`, `Student.prob_recall` is

```python
return np.exp(-(self.ns[item] * (t - self.last_review_times[item])))
```

We replace this with a `recall(item, t)` that returns a **deterministic
function of absolute time `t`** — the "information process" the agent has
to learn against:

```python
m_t = math.sqrt(t)
# or: 5-step Heaviside cascade,
# or: heavily-shifted Heaviside ramps,
# or: np.random.normal(3, 1)
```

These replace the human-forgetting interpretation with a generic
"intensity-of-business-relevant-events". The six categories under
`../experiments/information-processes/` correspond to:

- `constant`  — flat `m(t) = const`
- `random`    — `m(t)` is noise around a constant
- `step`      — sharp Heaviside steps at discrete days
- `shift`     — same shape, shifted in time
- `sqrt`      — slowly growing `m(t) = √t`
- `square`    — periodic square wave

### 3. Hyperparameter retune

The original setup trains for 1000 epochs × 50 iters with batch size 32,
intensity regularizer `q = 0.00025`, until 20000 batches. For one item over
14 days that is wildly excessive. We use:

| Parameter      | Upstream | One-item |
| ---            | ---      | ---      |
| `epochs`       | 1000     | 8        |
| `num_iters`    | 50       | 28       |
| `batch_size`   | 32       | 12       |
| `q` (intensity)| 0.00025  | 0.005    |
| `until`        | 20000    | 1250     |
| `decay_rate`   | 0.02     | 0.01     |

`MAX_EVENTS` in `exp_teacher.py` is also dropped from `100000` to `200`,
because a single service over a 14-day window simply cannot fire that many
times in any plausible regime.

### 4. `exp_teacher_save.py`

A copy of `exp_teacher.py` instrumented to retain the simulated scenarios
across calls so the analyze script can plot the agent's chosen call times
against the ground-truth process curve. Kept as a sibling module rather
than a flag on the original to avoid surprising upstream behaviour.

### 5. `analyze-spaced-repetition.py` plotting

Adds a Matplotlib block that, for each test batch, draws:

- the underlying `m(t)` curve,
- the agent's chosen call times as vertical ticks,
- the cumulative count of calls.

These are exactly the PNGs in `../experiments/information-processes/`.

## What is *not* changed

- The TPPRExpMarkedCellStacked recurrent cell (only comment annotations).
- The exponential CDF sampler (`exp_sampler.py`).
- The Smart-Broadcasting code path (`exp_broadcaster.py`,
  `train-broadcasting.py`, `analyze-broadcasting.py`). It still works as
  upstream, we just don't use it.
- The `redqueen`/`broadcast_ref` baselines required by the broadcasting
  code path — only needed if you want to re-run that.
