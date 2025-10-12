import sys
import io
import os
import tempfile
import pytest
import importlib.util
import pathlib

# Dynamically load llm_evaluation_framework/cli.py as a module to access main()
cli_path = pathlib.Path(__file__).parent.parent / "cli.py"
spec = importlib.util.spec_from_file_location("cli_module", cli_path)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def run_cli_command(args):
    """Helper to run CLI command and capture output."""
    sys.argv = ["cli.py"] + args
    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        cli.main()
    except SystemExit:
        # Handle SystemExit to capture output before exit
        pass
    finally:
        sys.stdout = sys.__stdout__
    return captured_output.getvalue()


def test_score_accuracy(monkeypatch):
    predictions = ["a", "b", "c"]
    references = ["a", "x", "c"]
    output = run_cli_command(
        ["score", "--predictions"] + predictions + ["--references"] + references + ["--metric", "accuracy"]
    )
    assert "Accuracy score:" in output


def test_score_f1(monkeypatch):
    predictions = ["a", "b", "c"]
    references = ["a", "x", "c"]
    output = run_cli_command(
        ["score", "--predictions"] + predictions + ["--references"] + references + ["--metric", "f1"]
    )
    assert "F1 score:" in output


def test_save_and_load(tmp_path):
    file_path = tmp_path / "test.json"
    data_pairs = ["key1=value1", "key2=value2"]

    # Save
    save_output = run_cli_command(["save", str(file_path), "--data"] + data_pairs)
    assert f"Data saved to {file_path}" in save_output
    assert file_path.exists()

    # Load
    load_output = run_cli_command(["load", str(file_path)])
    assert "Loaded data:" in load_output
    assert "key1" in load_output and "value1" in load_output


def test_load_no_data(tmp_path):
    file_path = tmp_path / "nonexistent.json"
    output = run_cli_command(["load", str(file_path)])
    assert "No data found." in output


def test_no_command_shows_help():
    output = run_cli_command([])
    assert "usage:" in output
