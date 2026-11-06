"""Find which Gemini model names this Google Cloud key can use.

    python scripts/find_gemini_model.py

Sends a tiny "say OK" request (a few tokens each) to each candidate name and prints
which ones answer. Then: export GEMINI_MODEL=<a name marked OK>
"""
import os, sys
from google import genai

key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not key:
    sys.exit("set GOOGLE_API_KEY in this terminal first")
backend = os.environ.get("GEMINI_BACKEND") or ("aistudio" if key.startswith("AIza") else "vertex")
client = genai.Client(api_key=key, vertexai=(backend == "vertex"))
print("backend:", backend)

try:
    names = [m.name for m in client.models.list()]
    gem = sorted({n.split("/")[-1] for n in names if "gemini" in n})
    print("models listed by the API:", ", ".join(gem) or "(none)")
except Exception as e:
    gem = []
    print("could not list models:", str(e)[:150])

CANDIDATES = ["gemini-flash-latest", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash",
              "gemini-3-flash", "gemini-3-flash-preview", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite-preview",
              "gemini-2.5-flash-lite", "gemini-pro-latest", "gemini-3.1-pro-preview", "gemini-3-pro-preview",
              "gemini-2.5-pro"]
ok = []
for m in list(dict.fromkeys([g for g in gem if "image" not in g and "tts" not in g and "live" not in g][:15] + CANDIDATES)):
    try:
        r = client.models.generate_content(model=m, contents="Reply with the single word OK.")
        print(f"  OK       {m:32} -> {(r.text or '').strip()[:20]}")
        ok.append(m)
    except Exception as e:
        print(f"  no       {m:32} ({str(e)[:70]})")
print("\nUsable:", ", ".join(ok) or "none")
if ok:
    pick = next((m for m in ok if "flash" in m and "lite" not in m), ok[0])
    print(f"Suggested:  export GEMINI_MODEL={pick}")
