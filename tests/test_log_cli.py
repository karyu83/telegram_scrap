from pathlib import Path
from uuid import uuid4

from src.log_cli import main


def test_log_cli_list_and_tail():
    base = Path("tests") / ".tmp" / f"log_cli_{uuid4().hex}"
    log_dir = base / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_a = log_dir / "collector_2026-03-08.log"
    log_a.write_text("line1\nline2\n", encoding="utf-8")
    log_b = log_dir / "collector_2026-03-09.log"
    log_b.write_text("a\nb\nc\n", encoding="utf-8")

    assert main(["--workspace", str(base), "list"]) == 0

    assert main(["--workspace", str(base), "tail", "--lines", "2"]) == 0
