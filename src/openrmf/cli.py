"""Command-line interface."""

import argparse
import json
import sys
from pathlib import Path

import yaml

from .categorization import categorize
from .generator import generate_poam, generate_ssp
from .poam import validate_poam
from .validator import validate_system


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="openrmf", description="OpenRMF Forge compliance-as-code toolkit"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("categorize", "validate", "build"):
        command = sub.add_parser(name)
        command.add_argument("system")
        if name in {"validate", "build"}:
            command.add_argument("--poam")
        if name == "build":
            command.add_argument("--output", default="build")
    args = parser.parse_args()
    system = load_yaml(args.system)
    if args.command == "categorize":
        print(json.dumps(categorize(**system["categorization"]), indent=2))
        return
    findings = validate_system(system)
    poam = load_yaml(args.poam) if args.poam else {"items": []}
    findings.extend(validate_poam(poam))
    if args.command == "validate":
        print(json.dumps(findings, indent=2))
    else:
        root = Path(__file__).resolve().parents[2]
        output = Path(args.output)
        output.mkdir(parents=True, exist_ok=True)
        (output / "system-security-plan.md").write_text(
            generate_ssp(system, root / "templates"), encoding="utf-8"
        )
        (output / "poam-report.md").write_text(
            generate_poam(poam, root / "templates"), encoding="utf-8"
        )
        (output / "validation-results.json").write_text(
            json.dumps(findings, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Generated artifacts in {output}")
    if any(f["severity"] == "error" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
