import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

from app.modules.lesson_knowledge.application.agent.tools import TOOL_DECLARATIONS

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-3.6-flash"]
MAX_RETRIES = 3
REQUEST_TIMEOUT_MS = 30000

def _is_retryable(error):
    if isinstance(error, errors.ClientError):
        return error.code in (429, 500, 502, 503, 504)
    msg = str(error).lower()
    if any(k in msg for k in ("timed out", "timeout", "deadline", "headers timed out", "temporarily unavailable")):
        return True
    return False

def _retry_delay(error):
    try:
        for detail in error.details:
            if str(detail.get("@type", "")).endswith("RetryInfo"):
                d = str(detail.get("retryDelay", ""))
                if d.endswith("s"):
                    return float(d[:-1])
    except: pass
    return None

def _try_generate(client, model, contents, config):
    last = None
    try:
        config.http_options = types.HttpOptions(timeout=REQUEST_TIMEOUT_MS)
    except Exception:
        pass
    for attempt in range(MAX_RETRIES):
        try:
            return client.models.generate_content(model=model, contents=contents, config=config)
        except Exception as e:
            last = e
            if not _is_retryable(e) or attempt == MAX_RETRIES-1:
                raise
            wait = _retry_delay(e) or (2**attempt)
            print(f"(429/timeout — إعادة خلال {wait:.0f}ث)")
            time.sleep(wait)
    raise last

def call_with_tools(client, contents, system):
    tools = [types.Tool(function_declarations=[
        types.FunctionDeclaration(name=t["name"], description=t["description"], parameters=t["parameters"]) for t in TOOL_DECLARATIONS
    ])]
    config = types.GenerateContentConfig(
        system_instruction=system,
        tools=tools,
        tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode="AUTO")),
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
    )
    models = [MODEL_NAME] + [m for m in FALLBACK_MODELS if m != MODEL_NAME]
    last = None
    for i, model in enumerate(models):
        try:
            return _try_generate(client, model, contents, config)
        except Exception as e:
            last = e
            if isinstance(e, errors.ClientError) and getattr(e, "code", None) in (404, 429):
                if i < len(models)-1:
                    print(f"({model} فشل → {models[i+1]})")
                    continue
            raise
    raise last

def call_simple(client, user: str, system: str) -> str:
    models = [MODEL_NAME] + [m for m in FALLBACK_MODELS if m != MODEL_NAME]
    for i, model in enumerate(models):
        try:
            last = None
            for attempt in range(MAX_RETRIES):
                try:
                    r = client.models.generate_content(model=model, contents=user, config=types.GenerateContentConfig(system_instruction=system, http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS)))
                    return r.text
                except Exception as e:
                    last = e
                    if not _is_retryable(e) or attempt == MAX_RETRIES-1:
                        raise
                    time.sleep(_retry_delay(e) or 2**attempt)
            raise last
        except Exception as e:
            if isinstance(e, errors.ClientError) and getattr(e, "code", None) in (404,429) and i < len(models)-1:
                continue
            raise
    raise last
