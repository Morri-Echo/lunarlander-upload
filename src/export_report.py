"""Export compact, reproducible evidence suitable for a GitHub commit."""
import json
import argparse
from pathlib import Path

from src.common import ROOT, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/latest-metrics.json")
    args = parser.parse_args()
    evidence = {}
    for name, relative in {
        "training": "ppo/training.json",
        "evaluation": "evaluation/evaluation.json",
        "legacy": "legacy/evaluation.json",
        "smoke": "smoke/results.json",
        "genesis": "genesis/results.json",
        "isaac": "isaac/results.json",
    }.items():
        path = ROOT / "outputs" / relative
        evidence[name] = (json.loads(path.read_text(encoding="utf-8"))
                          if path.exists() else {"status": "not_run"})
    upload_record = ROOT / "reports/hub-upload.json"
    evidence["hub_upload"] = (
        json.loads(upload_record.read_text(encoding="utf-8")) if upload_record.exists()
        else {"status": "prepared_locally", "requires": "User account and write token"})
    save_json(args.output, evidence)
    print(f"Exported {args.output}")


if __name__ == "__main__":
    main()
