"""Run only in the separate Isaac Sim 5.0 / Python 3.11 environment."""
from src.common import ROOT, save_json


def main():
    from isaacsim import SimulationApp
    app = SimulationApp({"headless": True})
    try:
        from isaaclab.sim import SimulationCfg, SimulationContext
        sim = SimulationContext(SimulationCfg(dt=1.0 / 60.0, device="cuda:0"))
        sim.reset()
        for _ in range(120):
            sim.step()
        save_json(ROOT / "outputs/isaac/results.json",
                  {"steps": 120, "device": "cuda:0", "check": "isaaclab_simulation_passed"})
    finally:
        app.close()


if __name__ == "__main__":
    main()
