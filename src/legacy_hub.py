import argparse
from pathlib import Path

import gym
import torch
from huggingface_hub import hf_hub_download
from shimmy import GymV26CompatibilityV0
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
import numpy as np

from src.common import ROOT, positive_int, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="Classroom-workshop/assignment2-omar")
    parser.add_argument("--filename", default="ppo-LunarLander-v2.zip")
    parser.add_argument("--episodes", type=positive_int, default=10)
    args = parser.parse_args()
    torch.set_num_threads(1)
    checkpoint = hf_hub_download(args.repo, args.filename,
                                 local_dir=str(ROOT / "outputs/legacy/download"))
    env = Monitor(GymV26CompatibilityV0(env=gym.make("LunarLander-v2")))
    try:
        # Gym changed declared Box bounds; inference still uses the same 8-vector.
        model = PPO.load(checkpoint, device="cpu", custom_objects={
            "learning_rate": 0.0, "lr_schedule": lambda _: 0.0,
            "clip_range": lambda _: 0.0})
        if model.observation_space.shape != env.observation_space.shape:
            raise ValueError("Legacy observation dimensions do not match")
        if model.action_space != env.action_space:
            raise ValueError("Legacy actions do not match")
        env.reset(seed=12345)
        rewards, lengths = evaluate_policy(model, env, n_eval_episodes=args.episodes,
                                          deterministic=True, return_episode_rewards=True)
        result = {"repo": args.repo, "filename": args.filename,
                  "env_id": "Gym LunarLander-v2 via Shimmy", "seed": 12345,
                  "episodes": args.episodes, "mean_reward": float(np.mean(rewards)),
                  "std_reward": float(np.std(rewards)),
                  "episode_rewards": rewards, "episode_lengths": lengths}
        save_json(ROOT / "outputs/legacy/evaluation.json", result)
        print(result)
    finally:
        env.close()


if __name__ == "__main__":
    main()
