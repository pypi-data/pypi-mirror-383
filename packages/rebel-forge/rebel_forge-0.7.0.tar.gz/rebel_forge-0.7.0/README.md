# rebel-forge

`rebel-forge` is a config-driven QLoRA/LoRA fine-tuning toolkit that runs smoothly on the Nebius GPU stack. It wraps the Hugging Face Transformers + PEFT workflow so teams can fine-tune hosted or user-provided models with a single command.

## Installation

`rebel-forge` targets Python 3.9 and newer. The base install ships just the configuration and dataset tooling so you can bring the exact PyTorch build you need.

### Minimal install

```bash
pip install rebel-forge
```

This installs the config/CLI plumbing plus `transformers`, `peft`, and `datasets`. Choose a runtime extra (or your own PyTorch wheel) when you know whether you need CPU-only or CUDA acceleration.

### Optional extras

```bash
# CPU-only wheels from PyPI
pip install rebel-forge[cpu]

# CUDA wheels (use the official PyTorch index if desired)
pip install rebel-forge[cuda] --extra-index-url https://download.pytorch.org/whl/cu121
```

### From source

```bash
git clone <repo-url>
cd rebel-forge
pip install -e .
```

### Export installed sources

`pip install rebel-forge` automatically drops a read-only copy to `~/rebel-forge`. Use the helper below to duplicate it elsewhere or refresh the snapshot.

```bash
rebel-forge source --dest ./rebel-forge-src
```

This copies the installed Python package into `./rebel-forge-src` so you can inspect or version-control the exact training scripts. Pass `--force` to overwrite an existing export.


## First run onboarding

Running `rebel-forge` launches a guided onboarding banner, exports the workspace into `~/rebel-forge`, and opens the Clerk portal at `http://localhost:3000/cli?token=…` (configurable via `.env.local`). Zero-argument runs render a compact “Welcome to Rebel” card with a single `Sign in with Rebel` button; press Enter and the CLI opens the portal with a fresh token and keeps the terminal watcher running until Clerk confirms the link. The CLI auto-starts `npm run dev` when it cannot detect the frontend, unlocks automatically after Clerk sign-in, and writes `~/.rebel-forge/onboarding.done` so future runs skip the blocking wizard. Automation helpers: set `REBEL_FORGE_SKIP_ONBOARDING=1` to bypass entirely or `REBEL_FORGE_AUTO_UNLOCK=1` (optionally `REBEL_FORGE_HANDSHAKE_USER`) to create the handshake file non-interactively.

## Usage

Prepare an INI/`.conf` file that names your base model, datasets, and training preferences. Then launch training with:

```bash
rebel-forge --config path/to/run.conf
```

The CLI infers sensible defaults (epochs, LoRA hyperparameters, dataset splits, etc.) and stores summaries plus adapter checkpoints inside the configured `output_dir`.

## Example configuration

```ini
[model]
base_model = meta-llama/Llama-3.1-8B
output_dir = /mnt/checkpoints/llama-3.1-chat
quant_type = nf4

[data]
format = plain
train_data = /mnt/datasets/fta/train.jsonl
eval_data = /mnt/datasets/fta/val.jsonl
text_column = text

[training]
batch_size = 2
epochs = 3
learning_rate = 2e-4
warmup_ratio = 0.05
save_steps = 250

[lora]
lora_r = 64
lora_alpha = 16
lora_dropout = 0.05
```

## Key features

- Optional 4-bit QLoRA via bitsandbytes (install `rebel-forge[cuda]` or add `bitsandbytes` manually)
- Dataset auto-loading for JSON/JSONL/CSV/TSV/local directories and Hugging Face Hub references
- Configurable LoRA target modules, quantization type, and training hyperparameters
- One-line Nebius provisioning (`forge.device(...)`) that spins up a fresh GPU VM on demand
- Summary JSON + adapter checkpoints emitted for downstream pipelines (Convex sync, artifact uploads, etc.)

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Nebius Remote Execution

Run `python -m rebel_forge.sample` after installation to push a Torch demo onto Nebius GPUs.


### Quick GPU smoke test

After `pip install rebel-forge`, run the packaged sampler:

```bash
python -m rebel_forge.sample
```

The helper syncs your project (using `forge.ensure_remote()`), relaunches on Nebius, and trains a tiny Torch model on CUDA.

`rebel-forge` ships a remote orchestrator so any Python project can offload execution to the Nebius GPU VM with a single helper call.

```python
import rebel_forge as forge

forge.ensure_remote()  # syncs and re-runs the script remotely on Nebius

# your existing training code stays untouched below this line
```

Configuration relies on the `FORGE_REMOTE_*` variables (falling back to the existing `NEBIUS_*` keys):

- `FORGE_REMOTE_HOST` / `NEBIUS_HOST`
- `FORGE_REMOTE_USER` / `NEBIUS_USERNAME`
- `FORGE_REMOTE_PORT` / `NEBIUS_PORT`
- `FORGE_REMOTE_KEY_PATH` or a `.nebius_key` file for the SSH identity
- `FORGE_REMOTE_VENV` (defaults to `~/venvs/rebel-forge`)
- `FORGE_REMOTE_ROOT` (defaults to `~/forge_runs`)

`forge.ensure_remote()` rsyncs the project tree (excluding caches, build artefacts, and virtualenvs), copies optional `.env` secrets, and relaunches the entrypoint on Nebius while streaming logs back to STDOUT. Once on the VM the helper is a no-op because the flag `FORGE_REMOTE_ACTIVE=1` is auto-set.

Need bespoke orchestration? Build a config and invoke commands directly:

```python
import rebel_forge as forge

cfg = forge.RemoteConfig.from_env()
forge.run_remote_command(cfg, ["python", "-m", "torch.utils.collect_env"])
```

## On-demand Nebius provisioning

Swap your manual `torch.device` selection for a call into Rebel Forge and the
library will stand up a Nebius VM, inject your SSH credentials, and re-run the
script remotely:

```python
import rebel_forge as forge

device = forge.device("h200", storage_gib=512)

# from here on you can use ``device`` exactly like ``torch.device("cuda")``
model.to(device)
```

Behind the scenes the helper performs the following steps when invoked from
your local environment:

1. Configures the Nebius CLI using the service-account credentials provided
   via environment variables.
2. Creates a boot disk from your preferred image (defaults to
   `ubuntu24.04-cuda12.0.2`) sized according to `storage_gib`.
3. Launches a VM on the requested GPU platform/preset inside your Nebius
   project and waits for SSH to become available.
4. Updates the `NEBIUS_*` environment variables and calls
   `forge.ensure_remote()` so the remainder of the script executes on the new
   instance.

When the code re-executes on the VM, `forge.device(...)` simply returns
`torch.device("cuda")` so the rest of your training script behaves exactly as
before.

### Required environment

The helper relies on several environment variables – populate them in your
`.env.local` (or equivalent) before invoking `forge.device`:

- `project_id`: Nebius project to charge the resources against.
- `service_account_id`: The service account that owns the authorized key.
- `Authorized_key`: Authorized (public) key ID for the service account.
- `AUTHORIZED_KEY_PRIVATE`: The corresponding private key PEM.
- `ssh_key_public` and `ssh_key_private`: The SSH key pair that should be
  installed on the VM for you to log in.
- Optional overrides:
  - `NEBIUS_SUBNET_ID`: The VPC subnet to attach (auto-detected if omitted).
  - `NEBIUS_IMAGE_ID`: Compute image to use for the boot disk.

You also need the Nebius CLI (`nebius`) on your PATH. The first call to
`forge.device` will initialise a profile in `~/.nebius/config.yaml` using the
service-account credentials above.

### Cleaning up

Provisioning currently leaves the instance running after your training script
completes. You can tear it down with the Nebius CLI:

```bash
# delete the VM
nebius compute instance delete "$FORGE_ACTIVE_INSTANCE_ID" --async=false

# delete the boot disk if you no longer need it
nebius compute disk delete <boot-disk-id> --async=false
```

Future releases will add a convenience helper for reclaiming the VM
automatically.
