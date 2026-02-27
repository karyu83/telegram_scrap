from pathlib import Path


def test_main_module_entry_delegates_to_run_main():
    main_path = Path("src/main.py")
    content = main_path.read_text(encoding="utf-8")

    assert "if __name__ == \"__main__\":" in content
    assert "from src.run import main as run_main" in content
    assert "raise SystemExit(run_main())" in content
