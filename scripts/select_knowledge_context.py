#!/usr/bin/env python3
"""Compatibility wrapper for the knowledge-base inventory builder.

Knowledge selection is now owned by prd-analyze. This wrapper only builds the
inventory files used by the AI sub-agent; it does not write the final
00-knowledge-context.json decision artifact.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_knowledge_inventory import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
