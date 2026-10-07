import csv
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.common import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "outputs/ppo")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/training.png")
    args = parser.parse_args()
    folder = args.input
    with (folder / "progress.csv").open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    pairs = [(float(r["time/total_timesteps"]), float(r["rollout/ep_rew_mean"]))
             for r in rows if r.get("rollout/ep_rew_mean")]
    figure, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(*zip(*pairs), color="#167d8d", label="Training (100-episode mean)")
    evaluations = np.load(folder / "eval/evaluations.npz")
    ax.plot(evaluations["timesteps"], evaluations["results"].mean(axis=1),
            "o-", color="#bf493c", label="Separate evaluation (5 episodes)")
    ax.axhline(200, color="#555555", linestyle="--", label="200 reward reference")
    ax.set(xlabel="Environment steps", ylabel="Episode reward", title="PPO on LunarLander-v3")
    ax.grid(alpha=0.2)
    ax.legend()
    figure.tight_layout()
    destination = args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
