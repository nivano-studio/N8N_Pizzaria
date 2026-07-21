"""Local, non-destructive finalizer for the Etapa 0 evidence package.

Live checks (n8n and Supabase) must be collected through their MCP connectors;
this script only validates packaged evidence and rebuilds the checksum manifest.
"""

from pathlib import Path
import hashlib
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
AUDIT = ROOT / "audit_baseline_20260721"
MANIFEST = AUDIT / "checksums.sha256"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    subprocess.run([sys.executable, str(SCRIPTS / "step1_sanitize_secrets_v2.py")], check=True)
    subprocess.run([sys.executable, str(SCRIPTS / "step2_generate_supabase_ddl_and_rpc.py")], check=True)

    files = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path != MANIFEST
        and ".git" not in path.parts
        and "node_modules" not in path.parts
        and ".gemini" not in path.parts
    )
    MANIFEST.write_text(
        "".join(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in files),
        encoding="utf-8",
    )

    invalid = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            invalid.append(relative)
    if invalid:
        raise SystemExit("Checksum verification failed: " + ", ".join(invalid))

    print(f"Etapa 0 package finalized: {len(files)} checksums verified.")


if __name__ == "__main__":
    main()
