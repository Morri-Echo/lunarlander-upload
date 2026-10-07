import argparse
import json
import shutil
from pathlib import Path

from src.common import ROOT


def prepare(model, evaluation, output, repo=None):
    output.mkdir(parents=True, exist_ok=True)
    result = json.loads((evaluation / "evaluation.json").read_text(encoding="utf-8"))
    recorded_model = Path(result["model"])
    if not recorded_model.is_absolute():
        recorded_model = ROOT / recorded_model
    if recorded_model.resolve() != model.resolve():
        raise ValueError("Evaluation must correspond to the uploaded model")
    shutil.copy2(model, output / "ppo-LunarLander-v3.zip")
    public_result = {**result, "model": "ppo-LunarLander-v3.zip"}
    (output / "results.json").write_text(
        json.dumps(public_result, indent=2), encoding="utf-8")
    shutil.copy2(evaluation / "replay-0.mp4", output / "replay.mp4")
    replay = (f'<video controls src="https://huggingface.co/{repo}/resolve/main/replay.mp4"></video>'
              if repo else '[Watch replay](./resolve/main/replay.mp4)')
    card = f'''---
license: apache-2.0
library_name: stable-baselines3
tags:
- reinforcement-learning
- PPO
- LunarLander-v3
model-index:
- name: PPO LunarLander-v3
  results:
  - task:
      type: reinforcement-learning
      name: Reinforcement Learning
    dataset:
      name: LunarLander-v3
      type: LunarLander-v3
    metrics:
    - type: mean_reward
      name: mean_reward
      value: {result["mean_reward"]:.2f} +/- {result["std_reward"]:.2f}
---
# PPO LunarLander-v3

Trained with Stable-Baselines3 on Gymnasium LunarLander-v3 using 16 environments.
Evaluation: {result["episodes"]} deterministic episodes, seed {result["seed"]}.

## Evaluation

| Metric | Result |
| --- | --- |
| Mean episode reward | **{result["mean_reward"]:.2f}** |
| Standard deviation | {result["std_reward"]:.2f} |
| Evaluation episodes | {result["episodes"]} |
| Environment | Gymnasium LunarLander-v3 |
| Evaluation seed | {result["seed"]} |

Full per-episode scores and lengths are available in [results.json](./resolve/main/results.json).

## Replay

{replay}

## Usage

```python
from huggingface_hub import hf_hub_download
from stable_baselines3 import PPO
checkpoint = hf_hub_download(
    repo_id="{repo or 'YOUR_USERNAME/ppo-LunarLander-v3'}",
    filename="ppo-LunarLander-v3.zip",
)
model = PPO.load(checkpoint, device="cpu")
```

## Training

The training run requested 1,000,000 environment steps. Stable-Baselines3 completed
full rollouts for 1,015,808 actual steps using 16 subprocess environments and seed 42.
Policy: MlpPolicy; n_steps=1024; batch_size=64; n_epochs=4; gamma=0.999;
gae_lambda=0.98; ent_coef=0.01; learning_rate=0.0003.
Tested with Python 3.9, Stable-Baselines3 2.6.0, Gymnasium 1.1.1, and PyTorch 2.8.0.
The score above is a deterministic 10-episode evaluation of the final model in a
separate environment; it is not a guarantee for every random seed.
'''
    (output / "README.md").write_text(card, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "outputs/ppo/ppo-LunarLander-v3.zip")
    parser.add_argument("--evaluation", type=Path, default=ROOT / "outputs/evaluation")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/hub-package")
    parser.add_argument("--repo", help="Hugging Face username/repository")
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()
    if args.upload and not args.repo:
        parser.error("--upload requires --repo")
    prepare(args.model, args.evaluation, args.output, args.repo)
    print(f"Prepared {args.output}")
    if args.upload:
        from huggingface_hub import HfApi
        api = HfApi()
        api.create_repo(args.repo, exist_ok=True)
        print(api.upload_folder(repo_id=args.repo, folder_path=args.output))


if __name__ == "__main__":
    main()
