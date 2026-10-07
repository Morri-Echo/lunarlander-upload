import argparse
from pathlib import Path

import gymnasium as gym
import imageio.v2 as imageio
import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor

from src.common import ROOT, portable_path, positive_int, save_json


def evaluate(model_path, output, episodes=10, seed=12345, video_episodes=1):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    model = PPO.load(model_path, device="cpu")
    env = Monitor(gym.make("LunarLander-v3"))
    try:
        env.reset(seed=seed)
        rewards, lengths = evaluate_policy(model, env, n_eval_episodes=episodes,
                                          deterministic=True, return_episode_rewards=True)
    finally:
        env.close()
    result = {"model": portable_path(model_path), "env_id": "LunarLander-v3", "seed": seed,
              "episodes": episodes, "deterministic": True,
              "mean_reward": float(np.mean(rewards)), "std_reward": float(np.std(rewards)),
              "episode_rewards": rewards, "episode_lengths": lengths,
              "mean_reward_at_least_200": bool(np.mean(rewards) >= 200)}
    save_json(output / "evaluation.json", result)
    if video_episodes:
        env = gym.make("LunarLander-v3", render_mode="rgb_array")
        try:
            for episode in range(video_episodes):
                observation, _ = env.reset(seed=seed + episode)
                with imageio.get_writer(output / f"replay-{episode}.mp4", fps=50,
                                        macro_block_size=2) as writer:
                    writer.append_data(env.render())
                    done = False
                    while not done:
                        action, _ = model.predict(observation, deterministic=True)
                        observation, _, terminated, truncated, _ = env.step(action)
                        writer.append_data(env.render())
                        done = terminated or truncated
                imageio.imwrite(output / f"replay-{episode}.png", env.render())
        finally:
            env.close()
    print(f"Mean reward: {result['mean_reward']:.2f} +/- {result['std_reward']:.2f}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "outputs/ppo/ppo-LunarLander-v3.zip")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/evaluation")
    parser.add_argument("--episodes", type=positive_int, default=10)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--video-episodes", type=int, default=1)
    args = parser.parse_args()
    if args.video_episodes < 0:
        parser.error("--video-episodes must be nonnegative")
    evaluate(args.model, args.output, args.episodes, args.seed, args.video_episodes)


if __name__ == "__main__":
    main()
