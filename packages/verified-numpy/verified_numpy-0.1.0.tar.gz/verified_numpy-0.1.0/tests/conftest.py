import pytest
from pathlib import Path

@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    p = tmp_path / "hello.txt"
    p.write_text("hi", encoding="utf-8")
    return p
