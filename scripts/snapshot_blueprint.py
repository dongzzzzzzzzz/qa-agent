#!/usr/bin/env python3
"""④ Save / compare blueprint snapshots under workspace/artifacts/snapshots/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from qa_coverage_checks import SNAPSHOTS_DIR, snapshot_compare, snapshot_save  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Blueprint snapshot for regression diff")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List snapshot directories")
    save_p = sub.add_parser("save", help="Save current 00-test-blueprint.json")
    save_p.add_argument("--label", default=None, help="Optional label suffix")
    cmp_p = sub.add_parser("compare", help="Compare two snapshots or latest vs named")
    cmp_p.add_argument("a", help="Snapshot dir name (under snapshots/)")
    cmp_p.add_argument("b", nargs="?", default=None, help="Second snapshot; omit = latest")
    args = parser.parse_args()

    if args.cmd == "list":
        if not SNAPSHOTS_DIR.exists():
            print("(no snapshots)")
            return 0
        for d in sorted(SNAPSHOTS_DIR.iterdir()):
            if d.is_dir():
                print(d.name)
        return 0
    if args.cmd == "save":
        dest = snapshot_save(args.label)
        print(dest)
        return 0
    if args.cmd == "compare":
        print(snapshot_compare(args.a, args.b))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
