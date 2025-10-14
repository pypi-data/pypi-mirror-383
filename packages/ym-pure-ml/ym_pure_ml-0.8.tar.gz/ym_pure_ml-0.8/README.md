# PureML — a tiny, transparent deep-learning framework in NumPy

PureML is a learning-friendly deep-learning framework built entirely on top of **NumPy**. It aims to be **small, readable, and hackable** while still being practical for real experiments and teaching.

- **No hidden magic** — a minimal autodiff Tensor + clear VJPs
- **Batteries included** — core layers (Affine, Dropout, BatchNorm1d), common losses, an SGD optimizer, and a simple `DataLoader`
- **Self-contained dataset demo** — a ready-to-use MNIST reader and an end-to-end “MNIST Beater” model
- **Portable persistence** — zarr-backed `ArrayStorage` with zip compression for saving/loading model state

> If you like **scikit-learn’s** simplicity and wish **deep learning** felt the same way for small/medium projects, PureML is for you.

---

## Install

PureML targets Python **3.11+** and NumPy **2.x**.

```bash
# (Option A) From PyPI (when available)
pip install pureml

# (Option B) From source
git clone https://github.com/<you>/pureml.git
cd pureml
pip install -e .
```

The only runtime deps are: `numpy`, `zarr` (plus lightweight helpers listed in `requirements.txt`).

---

## Quickstart: Train MNIST in a few lines

```python
from pureml.models.neural_networks import MNIST_BEATER
from pureml.datasets import MnistDataset

# 1) Load data (train uses one-hot labels; test gives class indices)
with MnistDataset("train") as train, MnistDataset("test") as test:
    # 2) Build the tiny network: Affine(784→256) → ReLU → Affine(256→10)
    model = MNIST_BEATER().train()

    # 3) Fit on the training set
    model.fit(train, batch_size=128, num_epochs=5)

    # 4) Switch to eval: model.predict returns class indices
    model.eval()
    # Example: run on one batch from the test set
    X_test, y_test = test[:128]
    preds = model(X_test)
    print(preds.data[:10])  # class ids
```

What you get out of the box:

- A tiny network that learns MNIST
- Clean logging of epoch loss
- An inference mode (`.eval()`) that returns class indices directly

---

## Core concepts

### 1) Tensors & Autodiff
PureML wraps NumPy arrays in a small `Tensor` that records operations and exposes `.backward()` for gradients. The Tensor supports:
- Elementwise + matmul ops (`+ - * / **`, `@`, `.T`)
- Reshaping helpers like `.reshape(...)` and `.flatten(...)`
- Non-grad ops like `.argmax(...)`
- A `no_grad` context manager for inference/metrics

> The goal is **clarity**: gradients are implemented as explicit vector-Jacobian products (VJPs) you can read in one file.

### 2) Layers
- **Affine (Linear)** — `Y = X @ W + b` (with sensible init)
- **Dropout**
- **BatchNorm1d** — with running mean/variance buffers and momentum

Layers expose:
- `.parameters` (trainables)
- `.named_buffers()` (non-trainable state)
- `.train()` / `.eval()` modes (with a per-layer `on_mode_change` hook)

### 3) Losses
- `MSE`
- `BCE` (probabilities) and `Sigmoid+BCE` (logits)
- `CCE` (categorical cross-entropy; supports `from_logits=True`)

### 4) Optimizers & Schedulers
- **SGD** (learning rate, optional momentum/weight decay depending on your version)
- Drop-in schedulers are easy to add; see the `optimizers` module.

### 5) Data utilities
- Minimal `Dataset` protocol (`__len__`, `__getitem__`)
- `DataLoader` with batching, shuffling, slice fast-paths, and an optional seeded RNG
- Helpers like `one_hot(...)` and `multi_hot(...)`

---

## Saving & Loading

PureML provides two levels of persistence:

- **Parameters only** — compact save/load of learnable weights
- **Full state** — parameters **+** buffers **+** top-level literals (versioned), using zarr with Blosc(zstd) compression inside a `.zip`

```python
# Save only trainable parameters
model.save("mnist_params")

# Save full state (params + buffers + literals) to .pureml.zip
model.save_state("mnist_full_state")

# Load later
model = MNIST_BEATER().eval().load_state("mnist_full_state.pureml.zip")
```

---

## MNIST dataset included

The repo ships a compressed zarr archive of MNIST (uint8, 28×28). The `MnistDataset`:
- Normalizes images to `[0,1]` float32
- Uses one-hot labels for training mode
- Supports slicing and context-manager cleanup

---

## Why PureML?

- **Read the source, learn the math.** Every gradient is explicit and local.
- **Great for teaching & research notes.** Small enough to copy into slides or notebooks.
- **Fast enough for classic datasets.** Vectorized NumPy code + light I/O.

If you need GPUs, distributed training, or huge model zoos, you should use PyTorch/JAX. PureML is intentionally small.

---

## Roadmap

- More optimizers (Adam, RMSProp), LR schedulers
- Convolutional layers and pooling
- RNN/CNN examples and docs
- Better metrics & visualization utilities
- Typed public API + docstrings/docs site

---

## Contributing

PRs, issues, and discussion are welcome! Please include:
- A small, focused change
- Clear rationale (what/why)
- Tests where appropriate

---

## License

MIT — see `LICENSE` in this repo.
