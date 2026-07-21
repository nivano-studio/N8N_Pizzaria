"""Redact accidental secrets from the portable Etapa 0 package."""

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"checksums.sha256"}
TEXT_EXTENSIONS = {".json", ".md", ".py", ".ts", ".txt", ".sql"}
PATTERNS = (
    (re.compile(r"sb_[A-Za-z0-9_-]{15,}"), "[REDACTED_SECRET]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._-]{15,}"), "Bearer [REDACTED_SECRET]"),
    (re.compile(r"sk-[A-Za-z0-9_-]{15,}"), "[REDACTED_SECRET]"),
    (re.compile(r"sk_live_[A-Za-z0-9_-]{15,}"), "[REDACTED_SECRET]"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}"), "[REDACTED_SECRET]"),
)


def redact_text(value: str) -> str:
    for pattern, replacement in PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def redact_json(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED_SECRET]"
            if key.lower() in {"elevenlabsapi-key", "openia_api_key", "openai_api_key", "vector_store_id"}
            and isinstance(item, str)
            and not item.startswith("[REDACTED")
            else redact_json(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_json(item) for item in value]
    return redact_text(value) if isinstance(value, str) else value


def main() -> None:
    changed: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in EXCLUDED or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() == ".json":
            try:
                replacement = json.dumps(redact_json(json.loads(original)), indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                replacement = redact_text(original)
        else:
            replacement = redact_text(original)
        if replacement != original:
            path.write_text(replacement, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"Secret sanitization complete. Files changed: {len(changed)}")


if __name__ == "__main__":
    main()
