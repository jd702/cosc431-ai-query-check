"""Smoke-test both API keys before spending quota on the real run.

    python scripts/check_keys.py

Sends one trivial prompt to each model and reports whether the key works and
whether the model id in .env is still valid. Costs 2 requests out of your daily
quota. Never prints your keys.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.llm import GEMINI_MODEL, GROQ_MODEL  # noqa: E402  (loads .env)

PROMPT = "Reply with exactly: OK"


def looks_like_bad_model(err: Exception) -> bool:
    text = str(err).lower()
    return any(s in text for s in ("not_found", "not found", "404", "does not exist", "decommission"))


def mask(key: str) -> str:
    return f"{key[:4]}…{key[-4:]} ({len(key)} chars)" if key else "MISSING"


def check_gemini() -> bool:
    print(f"\nGemini  model={GEMINI_MODEL}  key={mask(os.getenv('GEMINI_API_KEY', ''))}")
    try:
        from google import genai
    except ImportError:
        print("  ✗ google-genai not installed — run: pip install -r requirements.txt")
        return False
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=PROMPT)
        print(f"  ✓ replied: {(resp.text or '').strip()[:60]}")
        return True
    except KeyError:
        print("  ✗ GEMINI_API_KEY is not set in .env")
    except Exception as e:  # noqa: BLE001 - surface the provider's own message
        print(f"  ✗ {type(e).__name__}: {e}")
        if looks_like_bad_model(e):
            print("    That id is wrong or unavailable to you. Pick one from the model list at")
            print("    https://aistudio.google.com and update GEMINI_MODEL in .env.")
    return False


def check_groq() -> bool:
    print(f"\nGroq    model={GROQ_MODEL}  key={mask(os.getenv('GROQ_API_KEY', ''))}")
    try:
        from groq import Groq
    except ImportError:
        print("  ✗ groq not installed — run: pip install -r requirements.txt")
        return False
    try:
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        resp = client.chat.completions.create(
            model=GROQ_MODEL, messages=[{"role": "user", "content": PROMPT}]
        )
        print(f"  ✓ replied: {(resp.choices[0].message.content or '').strip()[:60]}")
        return True
    except KeyError:
        print("  ✗ GROQ_API_KEY is not set in .env")
    except Exception as e:  # noqa: BLE001
        print(f"  ✗ {type(e).__name__}: {e}")
        if looks_like_bad_model(e):
            print("    That id is retired or unavailable for your account. List what you can call:")
            print("      curl -s https://api.groq.com/openai/v1/models \\")
            print("        -H \"Authorization: Bearer $GROQ_API_KEY\" | grep -o '\"id\":\"[^\"]*\"'")
    return False


def main() -> None:
    if not (ROOT / ".env").exists():
        print("No .env file. Run:  cp .env.example .env   then paste your keys in.")
        sys.exit(1)
    ok = [check_gemini(), check_groq()]
    print()
    if all(ok):
        print("Both models reachable. Record these exact ids and today's date in the report,")
        print("then run notebooks/02_run_grade_audit_benchmark.ipynb.")
    else:
        print("Fix the failures above before running the notebook — a bad model id partway")
        print("through the run wastes quota.")
        sys.exit(1)


if __name__ == "__main__":
    main()
