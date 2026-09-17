"""One function, two models: generate_sql(model_key, schema_ddl, question).

Keys are read from each teammate's own .env (see .env.example).
"""
import os
import re

from dotenv import load_dotenv

from .paths import ROOT

load_dotenv(ROOT / ".env")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MODELS = ("gemini", "llama")

PROMPT_TEMPLATE = """You are given a SQLite database with this schema:

{schema}

Write a single SQLite query that answers the question below.
Return ONLY the SQL query — no explanation, no markdown fences.

Question: {question}
"""


def build_prompt(schema_ddl: str, question: str) -> str:
    return PROMPT_TEMPLATE.format(schema=schema_ddl.strip(), question=question.strip())


def _require_key(name: str) -> str:
    key = os.getenv(name)
    if not key:
        raise RuntimeError(f"{name} is not set. Copy .env.example to .env and add your own key.")
    return key


def _call_gemini(prompt: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_require_key("GEMINI_API_KEY"))
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0),
    )
    return resp.text or ""


def _call_groq(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=_require_key("GROQ_API_KEY"))
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content or ""


def clean_sql(text: str) -> str:
    """Strip markdown fences if the model added them anyway. Keep everything else
    as-is so the security audit sees exactly what the model produced."""
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return (m.group(1) if m else text).strip()


def generate_sql(model_key: str, schema_ddl: str, question: str) -> dict:
    prompt = build_prompt(schema_ddl, question)
    call = {"gemini": _call_gemini, "llama": _call_groq}[model_key]
    raw = call(prompt)
    return {
        "model": GEMINI_MODEL if model_key == "gemini" else GROQ_MODEL,
        "raw_response": raw,
        "sql": clean_sql(raw),
    }
