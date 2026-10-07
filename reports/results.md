# 实验结果

运行日期：2026-10-07。

## PPO LunarLander-v3

- 环境：Gymnasium `LunarLander-v3`
- 并行环境：16 个 `SubprocVecEnv`
- 算法：Stable-Baselines3 PPO，`MlpPolicy`
- 请求步数：1,000,000
- SB3 实际步数：1,015,808（完整 rollout 批次）
- 训练耗时：约 338.73 秒
- 独立评估：10 局，seed 12345，确定性策略
- 平均回报：**229.74 ± 16.79**
- 成功判定：平均回报达到 200，10 局回报均达到 200
- 视频：`outputs/evaluation/replay-0.mp4`，395 帧，400x600，首尾帧像素有变化

训练过程中 SB3 的 5 局独立评估在 800,000 步为 `224.65 ± 24.21`，在 1,000,000 步为 `251.44 ± 15.09`。最终的 10 局评估使用了不同的评估种子，因此数值不同是预期行为。

## Shimmy 旧模型

PPT 指定仓库 `Classroom-workshop/assignment2-omar` 实际提供 `ppo-LunarLander-v2.zip`。通过 `GymV26CompatibilityV0` 加载到 Gym `LunarLander-v2`，10 局确定性评估为 **302.04 ± 18.39**。PPT 中写的 v3 文件名与仓库内容不一致，项目按仓库实际文件执行并记录。

## MuJoCo

主 `.venv` 中 MuJoCo 3.3.7 验证通过：创建球体和地面，执行 500 步物理更新，检查自由落体后的高度，并完成离屏渲染。结果写入 `outputs/smoke/results.json`，截图为 `outputs/smoke/mujoco.png`。

## Genesis

Genesis 0.2.1 已安装到独立 `.venv-genesis`，CPU 物理验收通过：盒子从 `[0, 0, 1]` 下落，100 步后最终高度为 `0.099892` 米，符合半高为 0.1 米的盒子落地结果。该版本与 `libigl 2.6.3` 的 `signed_distance` 返回值不兼容，已固定 `libigl==2.5.1`。Taichi 和 Genesis 缓存都放在项目 `.cache/`。Windows 下 Genesis 的无窗口渲染会给出官方警告；验收使用 CPU 和无 viewer 物理场景，没有调用该渲染功能。结果写入 `outputs/genesis/results.json`。

## Isaac Sim / Isaac Lab

本机检测到 NVIDIA GeForce RTX 3060 12GB，但系统内存约 16GB。PPT 指定的 Isaac Sim 5.x / Python 3.11 版本配对已写入 `scripts/setup_isaac.ps1` 和 `src/isaac_check.py`。本机内存低于 Isaac Sim 官方常见最低要求，未执行完整下载和启动验收，避免产生无法运行的大型安装；升级到满足要求的机器后可按 `docs/simulators.md` 继续。

## Hugging Face 发布

已于 2026-10-07 发布到公开仓库 [ZZW-Echo/ppo-LunarLander-v3](https://huggingface.co/ZZW-Echo/ppo-LunarLander-v3)。模型卡中显示平均回报 **229.74 ± 16.79** 及视频回放。模型权重、模型卡、评分 JSON 和 MP4 四个文件均从远端读回，并通过 SHA-256 与本地文件的一致性检查。验证的提交为 `7a877388a09ea9fc8f7820ae6127e13390d4c200`。
