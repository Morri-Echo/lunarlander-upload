import argparse
import time
from pathlib import Path

import gymnasium as gym
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.logger import configure
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

from src.common import ROOT, portable_path, positive_int, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=positive_int, default=1_000_000)
    parser.add_argument("--envs", type=positive_int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--backend", choices=["dummy", "subproc"], default="subproc")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "ppo")
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    settings = dict(n_steps=1024, batch_size=64, n_epochs=4, gamma=0.999,
                    gae_lambda=0.98, ent_coef=0.01)
    save_json(output / "config.json", {**vars(args), "output": portable_path(output),
              "resume": portable_path(args.resume) if args.resume else None,
              "ppo": settings, "env_id": "LunarLander-v3", "device": "cpu"})
    env = make_vec_env("LunarLander-v3", n_envs=args.envs, seed=args.seed,
                       monitor_dir=str(output / "monitor"),
                       vec_env_cls=SubprocVecEnv if args.backend == "subproc" else DummyVecEnv)
    eval_env = Monitor(gym.make("LunarLander-v3"))
    eval_env.reset(seed=args.seed + 10_000)
    callbacks = [
        EvalCallback(eval_env, best_model_save_path=str(output / "best"),
                     log_path=str(output / "eval"), n_eval_episodes=5,
                     eval_freq=max(100_000 // args.envs, 1), deterministic=True),
        CheckpointCallback(save_freq=max(250_000 // args.envs, 1),
                           save_path=str(output / "checkpoints"), name_prefix="ppo"),
    ]
    try:
        model = (PPO.load(args.resume, env=env, device="cpu") if args.resume else
                 PPO("MlpPolicy", env, seed=args.seed, device="cpu", verbose=1, **settings))
        model.set_logger(configure(str(output), ["stdout", "csv"]))
        started = time.perf_counter()
        model.learn(total_timesteps=args.steps, callback=callbacks,
                    reset_num_timesteps=args.resume is None)
        model.save(output / "ppo-LunarLander-v3")
        save_json(output / "training.json", {"requested_steps": args.steps,
                  "actual_steps": model.num_timesteps, "seconds": time.perf_counter() - started})
    finally:
        env.close()
        eval_env.close()


if __name__ == "__main__":
    main()
