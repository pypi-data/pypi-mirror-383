# mlbnb

Machine learning bread and butter - a collection of tools for PyTorch-based machine learning experiments.

This library provides utilities to streamline common tasks such as experiment management, checkpointing, and data handling.

To jumpstart your ML experiment codebase, check out the associated [scaffolding-v3 repo](https://github.com/jonas-scholz123/scaffolding-v3), which uses mlbnb.

## Core Components

### `ExperimentPath`

The `ExperimentPath` class helps manage the directory structure for your experiments. It can generate unique run names and save your experiment configuration.

**Example:**

```python
from pathlib import Path
from omegaconf import OmegaConf
from mlbnb.paths import ExperimentPath

# Define your experiment configuration
cfg = OmegaConf.create({
    "learning_rate": 1e-3,
    "model": {
        "name": "resnet18",
        "pretrained": True
    },
    "dataset": "cifar10"
})

# Create a new experiment path
# This will create a directory like: /tmp/experiments/2025-06-26_11-02_witty_zebra
exp_path = ExperimentPath.from_config(cfg, root=Path("/tmp/experiments"))

print(f"Experiment directory: {exp_path}")

# The configuration is saved automatically
saved_cfg = exp_path.get_config()
assert saved_cfg == cfg

# You can also create paths for files within the experiment directory
model_dir = exp_path / "models"
model_dir.mkdir()
print(f"Model directory: {model_dir}")
```

### `CheckpointManager`

The `CheckpointManager` simplifies saving and loading the state of your training loop, including the model, optimizer, and random number generators. It integrates with `ExperimentPath` to store checkpoints within your experiment's directory.

**Example:**

```python
import torch
from torch import nn, optim
from mlbnb.checkpoint import CheckpointManager
from mlbnb.paths import ExperimentPath

# Assume exp_path is an existing ExperimentPath instance
exp_path = ExperimentPath(root="/tmp/experiments", name="my-first-experiment")

# Initialize components
model = nn.Linear(10, 2)
optimizer = optim.Adam(model.parameters())
generator = torch.Generator()

# Create a CheckpointManager
checkpoint_manager = CheckpointManager(exp_path)

# Save a checkpoint
checkpoint_manager.save_checkpoint(
    name="epoch_1",
    model=model,
    optimiser=optimizer,
    generator=generator
)
print(f"Saved checkpoints: {checkpoint_manager.list_checkpoints()}")

# Later, you can restore the state
new_model = nn.Linear(10, 2)
new_optimizer = optim.Adam(new_model.parameters())
new_generator = torch.Generator()

checkpoint_manager.reproduce(
    name="epoch_1",
    model=new_model,
    optimiser=new_optimizer,
    generator=new_generator
)

print("Restored state from checkpoint.")
```

## Other Utilities

`mlbnb` also includes several other helpful modules:

- **`WandbLogger` & `WandbProfiler`**: For logging metrics and profiling code with Weights & Biases.
- **`StepIterator`**: An iterator that runs for a fixed number of steps, to turn training from "num epochs" to "num steps" cleanly.
- **`LabelledArray`**: A NumPy array wrapper that allows indexing by named coordinates, similar to xarray, supporting memmaps.
- **`checksum`**: A utility to compute a checksum for objects containing tensors to verify reproducibility.
- **`EarlyStopper`**: Stop training when a metric stops improving.
- **`CachedDataset`**: A PyTorch `Dataset` wrapper that caches items in memory.
