"""Build reproducible manifests for both audited stages, excluding manifests and cache."""

from pathlib import Path
import hashlib


ROOT = Path(__file__).resolve().parents[1]


def build(stage: str) -> None:
    base = ROOT / stage
    manifest = base / "audit_baseline_20260721" / "checksums.sha256" if stage == "0-etapa" else base / "checksums.sha256"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        path for path in base.rglob("*")
        if path.is_file()
        and path != manifest
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    )
    manifest.write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(base).as_posix()}\n" for path in files),
        encoding="utf-8",
    )
    invalid = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = base / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            invalid.append(relative)
    if invalid:
        raise SystemExit(f"{stage} manifest failed: {invalid}")
    print(f"{stage}: {len(files)} files, manifest verified")


if __name__ == "__main__":
    build("0-etapa")
    build("1-etapa")
