import os
from importlib import reload
from pathlib import Path
from typing import Iterator

import pandas as pd
import pytest

import prepro.pipeline as pipeline_mod


@pytest.fixture(autouse=False)
def tmp_workdir(tmp_path: Path) -> Iterator[Path]:
    """Switch CWD to a temp directory for the test and restore afterwards."""
    prev = Path.cwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(prev)


def test_extract_writes_file_and_uses_params(
    tmp_workdir: Path, monkeypatch: pytest.MonkeyPatch
):
    # Arrange
    captured = {}

    class DummyResp:
        status_code = 200

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            yield b"col1,col2\n1,2\n"

    def fake_get(url, params=None, stream=None):
        captured["url"] = url
        captured["params"] = params
        captured["stream"] = stream
        return DummyResp()

    monkeypatch.setattr(pipeline_mod.requests, "get", fake_get)

    # Act
    pipeline_mod.extract("http://db", "/blob/dev/raw/2025/8/N_Test.csv")

    # Assert
    assert captured["url"].endswith("/extract_file")
    assert captured["params"] == {"path": "/blob/dev/raw/2025/8/N_Test.csv"}
    assert Path("extracted_N_Test.csv").exists()


def test_transform_maps_and_saves_csv(
    tmp_workdir: Path, monkeypatch: pytest.MonkeyPatch
):
    # Arrange - create an extracted csv with some columns
    Path("extracted_Sample.csv").write_text(
        "Started Date,Completed Date,Type,Product,Description,Amount,Fee,Currency,State,Balance,Extra\n"
        "2025-08-01,2025-08-02,CARD,Prod,Something,10.5,0,EUR,COMPLETED,100,zzz\n"
    )

    # Act
    pipeline_mod.transform("/anything/Sample.csv")

    # Assert
    out = Path("transformed_Sample.csv")
    assert out.exists()
    df = pd.read_csv(out)
    assert "Executor" in df.columns
    # Balance column should be removed
    assert "Balance" not in df.columns
    # State filtered and removed
    assert "State" not in df.columns
    assert len(df) == 1


def test_load_calls_loader_and_cleans_files(
    tmp_workdir: Path, monkeypatch: pytest.MonkeyPatch
):
    # Arrange - create files expected by load
    Path("extracted_A.csv").write_text("x\n1\n")
    df = pd.DataFrame(
        [
            {
                "Started Date": "2025-08-01",
                "Completed Date": "2025-08-02",
                "Type": "CARD",
                "Product": "Prod",
                "Description": "Something",
                "Amount": 10.5,
                "Fee": 0,
                "Currency": "EUR",
                "Executor": "A",
            }
        ]
    )
    df.to_csv("transformed_A.csv", index=False)

    called = {"args": None}

    def fake_load_to_postgres(path):
        called["args"] = path

    # Patch the function in pipeline module namespace (matches pipeline.load's import)
    monkeypatch.setattr(pipeline_mod, "load_to_postgres", fake_load_to_postgres)

    # Act
    pipeline_mod.load("/whatever/A.csv")

    # Assert - loader called with correct path and temp files removed
    assert called["args"] == "transformed_A.csv"
    assert not Path("extracted_A.csv").exists()
    assert not Path("transformed_A.csv").exists()


def test_load_missing_transformed_logs_and_returns(
    tmp_workdir: Path, capsys: pytest.CaptureFixture
):
    # Nothing created, should log error and return without raising
    pipeline_mod.load("/nope/NA.csv")
    # We don't assert logs here (logger configured elsewhere), just ensure no exception
    assert True
