# 仿真环境实践

对应 PPT 第 13 至 19 页。核心强化学习环境使用 `.venv`，Genesis 使用 `.venv-genesis`，Isaac 使用 `.venv-isaac`。不同环境有互相冲突的版本要求。

## MuJoCo

项目依赖固定 MuJoCo 3.3.7。先按 README 在新电脑重建环境，再运行：

```powershell
.\.venv\Scripts\python.exe -m src.smoke_test
```

脚本创建球体和地面，计算 500 步自由落体及碰撞，检查最终高度，再生成 `outputs/smoke/mujoco.png`。这同时验证物理引擎和离屏渲染。

## Genesis

采用与 PPT 的 Python 3.9 方案兼容的 Genesis 0.2.1；该版本固定 NumPy 1.26.4、MuJoCo 3.2.5、Taichi 1.7.3，因此使用独立环境。`libigl==2.5.1` 解决新版本返回值 API 不兼容问题，CPU 仿真已在本机通过。

```powershell
.\.venv\Scripts\python.exe -m venv .venv-genesis
.\.venv-genesis\Scripts\python.exe -m pip install -r requirements-genesis.txt
.\.venv-genesis\Scripts\python.exe -m src.genesis_check
```

新电脑推荐使用 README 中的 `scripts/setup.ps1 -Genesis` 安装入口，它会同时应用 `requirements-genesis-lock.txt` 完整版本约束。清理后的项目不携带旧电脑的虚拟环境。

基本验证创建地面和盒子，执行 100 步重力与碰撞，并检查最终位置。使用 CPU 和 `show_viewer=False`，符合 PPT 标注的 Windows CPU 仿真能力；不依赖 Windows 暂不支持的交互查看器或光线追踪。首次编译 Taichi 内核可能较慢。

## Isaac Sim / Isaac Lab

本机：Windows 11、RTX 3060 12GB、约 16GB 内存。PPT 的 Isaac Sim 5.x 需要 Python 3.11，4.x 需要 Python 3.10；当前主实验是 Python 3.9。当前官方要求页（检查日期 2026-10-07）最低为 32GB 系统内存及 16GB 显存，本机不满足，因此当前机器没有执行完整安装或启动验收。该官方页面目前对应 Isaac Sim 6.0；旧 5.0 参考地址已无法打开，安装 5.0 前应进一步核实归档版本要求，不能将最新页面的显卡要求直接当作 5.0 的要求。

准备了独立安装脚本及最小仿真验收代码，采用 Isaac Sim 5.0.0 / Isaac Lab v2.2.0 配对。升级内存并准备 Python 3.11 后：

```powershell
.\scripts\setup_isaac.ps1 -Python311 'C:\path\to\python311\python.exe'
.\.venv-isaac\Scripts\python.exe -m src.isaac_check
```

需要安装 Git，并阅读 NVIDIA 的许可条款。首次启动按终端提示接受 EULA 后才会启动；脚本不会代替用户接受。Pip 安装使用 NVIDIA 索引，扩展首次加载可能需要十分钟以上。使用拟安装版本的最低要求检查硬件。该脚本在本机仅做语法检查，未宣称已运行成功。

- [Isaac Sim 当前官方要求](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html)
- [Isaac Lab 官方文档](https://isaac-sim.github.io/IsaacLab/)
- [PPT 中文参考](https://docs.robotsfan.com/isaaclab/source/setup/installation/pip_installation.html)
- [Genesis 安装文档](https://genesis-world.readthedocs.io/zh-cn/latest/user_guide/overview/installation.html)

## 可选工具

PPT 第 19 页将 OMPL、splashsurf 标为可选。本实验没有运动规划或流体表面重建任务，不需要它们完成 LunarLander 或基本刚体仿真。

- OMPL：从 [官方预发布 wheel](https://github.com/ompl/ompl/releases/tag/prerelease) 选取匹配操作系统、Python、架构的 wheel，再在相应环境中执行 `python -m pip install path/to/ompl.whl`。不能混用 Linux 和 Windows wheel。
- splashsurf：安装 Rust 工具链后执行 `cargo install splashsurf`，通过 `splashsurf --help` 检查。Linux 的 `apt` 命令不能直接在 Windows PowerShell 里使用。
