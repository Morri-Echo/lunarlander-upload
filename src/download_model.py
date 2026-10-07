"""Restore the published model on a new computer without logging in."""
import argparse
import hashlib
from pathlib import Path

from huggingface_hub import hf_hub_download

from src.common import ROOT, save_json

REPO = "ZZW-Echo/ppo-LunarLander-v3"
REVISION = "7a877388a09ea9fc8f7820ae6127e13390d4c200"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default=REVISION)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/ppo")
    parser.add_argument("--with-replay", action="store_true")
    args = parser.parse_args()
    model = Path(hf_hub_download(REPO, "ppo-LunarLander-v3.zip", revision=args.revision,
                                local_dir=str(args.output), token=False))
    reference = ROOT / "outputs/published-reference"
    names = ["README.md", "results.json"]
    if args.with_replay:
        names.append("replay.mp4")
    for name in names:
        hf_hub_download(REPO, name, revision=args.revision,
                        local_dir=str(reference), token=False)
    save_json(args.output / "download.json", {
        "repo": REPO, "revision": args.revision, "filename": model.name,
        "sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
    })
    print(f"Downloaded model: {model}")
    print("Evaluate with: python -m src.evaluate")


if __name__ == "__main__":
    main()
