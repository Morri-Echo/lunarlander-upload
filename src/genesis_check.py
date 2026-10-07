import os

from src.common import ROOT, save_json

# Taichi's cache must stay inside the project.
os.environ.setdefault("TI_OFFLINE_CACHE_FILE_PATH", str(ROOT / ".cache/taichi"))


def main():
    import genesis as gs
    import numpy as np

    # Genesis 0.2.1 has no cache setting; redirect only its cache helper.
    gs.utils.misc.get_cache_dir = lambda: str(ROOT / ".cache/genesis")
    gs.init(backend=gs.cpu, logging_level="warning")
    scene = gs.Scene(sim_options=gs.options.SimOptions(dt=0.01), show_viewer=False)
    scene.add_entity(gs.morphs.Plane())
    box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 1), size=(0.2, 0.2, 0.2)))
    scene.build()
    initial = box.get_pos().detach().cpu().numpy().tolist()
    for _ in range(100):
        scene.step()
    final = box.get_pos().detach().cpu().numpy().tolist()
    assert np.all(np.isfinite(final)) and final[2] < initial[2]
    assert 0.05 < final[2] < 0.15
    result = {"backend": "cpu", "viewer": False, "steps": 100,
              "initial_position": initial, "final_position": final,
              "check": "gravity_and_ground_collision_passed"}
    save_json(ROOT / "outputs/genesis/results.json", result)
    print(result)


if __name__ == "__main__":
    main()
