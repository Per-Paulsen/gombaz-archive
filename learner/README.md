# Learner — One-Item TPP-RL

This directory does **not** contain the learner source code. It contains a
patch (`one_item.patch`) that adapts the upstream code from

> Upadhyay, U., De, A., Gomez-Rodriguez, M.
> *Deep Reinforcement Learning of Marked Temporal Point Processes.*
> NeurIPS 2018. [arXiv:1805.09360](https://arxiv.org/abs/1805.09360)
>
> <https://github.com/Networks-Learning/tpprl>

The upstream repository ships **without an explicit license**. We therefore
cannot redistribute the code here in any form. The patch represents only
the modifications, which are this repository's own contribution. To run the
adapted learner you have to clone upstream yourself and apply the patch.

## What the patch changes

See `MODIFICATIONS.md` for the full rationale. In short:

- Reduces the spaced-repetition setup from 50 items to **1 item** — the
  scheduling problem we care about is "when to fire one service", not "which
  flashcard to show next".
- Replaces the human-forgetting recall function `m(t) = exp(-n·Δt)` with
  configurable **artificial information processes** (`sqrt(t)`, Heaviside
  step functions, normal-distributed) that stand in for "underlying
  intensity an external system exposes through events".
- Re-tunes hyperparameters for the one-item, short-horizon regime
  (smaller batches, fewer epochs, different regularizer weights).
- Adds an `exp_teacher_save.py` variant that persists the trained
  scenarios for downstream plotting.
- Adds plotting code in `analyze-spaced-repetition.py` that overlays the
  agent's chosen call times against the underlying ground-truth process.

## Applying the patch

```bash
./apply.sh
```

This clones upstream into `upstream/` (gitignored) and applies
`one_item.patch` on top. Then follow the upstream README for the Python
environment (TensorFlow 1.8, NumPy 1.14, etc.). One-line summary of a run:

```bash
cd upstream
mkdir -p output-spaced-repetition
python train-teaching.py ./data/initial_difficulty.csv 0.049 0.0052 \
    ./output-spaced-repetition --q 0.005 --q-entropy 0.005
python analyze-spaced-repetition.py ./data/initial_difficulty.csv 0.049 0.0052 \
    ./output-spaced-repetition/save
```

The plots produced by `analyze-spaced-repetition.py` are the ones in
`../experiments/information-processes/`.
