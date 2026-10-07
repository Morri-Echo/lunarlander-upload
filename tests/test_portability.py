import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import common, hub


class PortabilityTests(unittest.TestCase):
    def test_project_paths_are_relative(self):
        self.assertEqual(common.portable_path(common.ROOT / "outputs/model.zip"),
                         "outputs/model.zip")

    def test_model_package_survives_directory_change(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            model = root / "outputs/ppo/model.zip"
            model.parent.mkdir(parents=True)
            model.write_bytes(b"model")
            evaluation = root / "outputs/evaluation"
            evaluation.mkdir()
            (evaluation / "evaluation.json").write_text(json.dumps({
                "model": "outputs/ppo/model.zip", "mean_reward": 229.74,
                "std_reward": 16.79, "episodes": 10, "seed": 12345,
            }), encoding="utf-8")
            (evaluation / "replay-0.mp4").write_bytes(b"replay")
            destination = root / "package"
            with patch.object(hub, "ROOT", root):
                hub.prepare(model, evaluation, destination, "ZZW-Echo/ppo-LunarLander-v3")
            self.assertEqual((destination / "ppo-LunarLander-v3.zip").read_bytes(), b"model")
            result = json.loads((destination / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(result["model"], "ppo-LunarLander-v3.zip")
            self.assertNotIn(str(root), (destination / "README.md").read_text(encoding="utf-8"))
            with patch.object(hub, "ROOT", root):
                with self.assertRaises(ValueError):
                    hub.prepare(root / "different-model.zip", evaluation, root / "invalid")


if __name__ == "__main__":
    unittest.main()
