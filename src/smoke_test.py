import argparse
import importlib.metadata
import platform
import sys

import gymnasium as gym
import imageio.v2 as imageio
import numpy as np
import torch
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.monitor import Monitor

from src.common import ROOT, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-mujoco-render", action="store_true",
                        help="Skip OpenGL rendering on CI runners without a graphics driver")
    args = parser.parse_args()
    output = ROOT / "outputs/smoke"
    output.mkdir(parents=True, exist_ok=True)
    result = {"python": sys.version, "platform": platform.platform(),
              "cuda_available": torch.cuda.is_available(), "checks": {}}
    env = gym.make("LunarLander-v3", render_mode="rgb_array")
    try:
        obs, info = env.reset(seed=42)
        assert obs.shape == (8,) and isinstance(info, dict)
        env.action_space.seed(42)
        for _ in range(50):
            obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
            if terminated or truncated:
                env.reset()
        frame = env.render()
        assert frame.shape == (400, 600, 3) and np.ptp(frame) > 0
        imageio.imwrite(output / "lunarlander.png", frame)
        result["checks"]["gymnasium_reset_step_render"] = "passed"
    finally:
        env.close()
    vec = make_vec_env("LunarLander-v3", n_envs=16, seed=42)
    try:
        assert vec.reset().shape == (16, 8)
        assert vec.step(np.zeros(16, dtype=int))[0].shape == (16, 8)
        result["checks"]["16_vectorized_environments"] = "passed"
    finally:
        vec.close()
    import gym as old_gym
    from shimmy import GymV26CompatibilityV0
    legacy = Monitor(GymV26CompatibilityV0(env=old_gym.make("LunarLander-v2")))
    try:
        legacy.reset(seed=42)
        assert len(legacy.step(0)) == 5
        result["checks"]["shimmy_gym_v26"] = "passed"
    finally:
        legacy.close()
    import mujoco
    model = mujoco.MjModel.from_xml_string('''<mujoco><worldbody>
      <light pos="0 0 3"/><geom type="plane" size="2 2 .1"/>
      <body pos="0 0 1"><freejoint/><geom type="sphere" size=".1" mass="1"/>
      </body></worldbody></mujoco>''')
    data = mujoco.MjData(model)
    for _ in range(500):
        mujoco.mj_step(model, data)
    assert 0.08 < data.qpos[2] < 0.12
    if args.skip_mujoco_render:
        result["checks"]["mujoco_physics"] = "passed"
        result["checks"]["mujoco_render"] = "skipped: explicit --skip-mujoco-render"
    else:
        with mujoco.Renderer(model, height=240, width=320) as renderer:
            renderer.update_scene(data)
            imageio.imwrite(output / "mujoco.png", renderer.render())
        result["checks"]["mujoco_physics_and_render"] = "passed"
    result["versions"] = {name: importlib.metadata.version(name) for name in
                           ["gymnasium", "stable-baselines3", "torch", "Box2D", "gym", "shimmy", "mujoco", "numpy"]}
    save_json(output / "results.json", result)
    print(result)


if __name__ == "__main__":
    main()
