"""One Gemini call on the Joe demo case, with the full error if it fails.

    python scripts/check_gemini.py
"""
import sys, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fasttrack.intake import LocalFolderConnector
from fasttrack.reader import GeminiReader

try:
    r = GeminiReader()
    print("backend:", r.backend, "| model:", r.model)
    res = r.read(LocalFolderConnector(str(ROOT / "data" / "simulated")).load_case("demo-001"))
    print(f"OK: {len(res.items)} checklist items, {res.input_tokens} in / {res.output_tokens} out tokens, {res.seconds:.1f}s")
    for i in res.items[:5]:
        print("  ", i.field, "=", i.value, "| p.", i.page, "|", i.quote[:70])
except Exception:
    traceback.print_exc()
