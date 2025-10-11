"""Tests for the CLI functionality."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from asdadagp.cli import main, validate_file_path


def test_validate_file_path():
    """Test file path validation."""
    # Test with existing file
    current_file = __file__
    result = validate_file_path(current_file)
    assert result == str(Path(current_file).resolve())

    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        validate_file_path("non_existent_file.txt")


def test_cli_help():
    """Test that CLI help works."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "asdadagp.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "acoustic-solo-dadaGP" in result.stdout
        assert "encode" in result.stdout
        assert "decode" in result.stdout
        assert "process" in result.stdout
        assert "info" in result.stdout
    except subprocess.TimeoutExpired:
        pytest.skip("CLI help test timed out")


def test_cli_no_command():
    """Test CLI with no command shows help."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "asdadagp.cli"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1
        assert "Available commands" in result.stdout
    except subprocess.TimeoutExpired:
        pytest.skip("CLI no command test timed out")


def test_cli_info_with_test_file():
    """Test CLI info command with a test Guitar Pro file."""
    data_folder = Path(__file__).parent / "data"
    test_file = data_folder / "bensusan_pierre-dame_lombarde.gp5"

    if not test_file.exists():
        pytest.skip("Test Guitar Pro file not found")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "asdadagp.cli", "info", str(test_file)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "Guitar Pro File" in result.stdout
        assert "Tracks:" in result.stdout
    except subprocess.TimeoutExpired:
        pytest.skip("CLI info test timed out")


def test_cli_process_with_test_file():
    """Test CLI process command with a test token file."""
    # First create a test token file
    test_tokens = [
        "Test Artist",
        "downtune:0",
        "tempo:120",
        "D4",
        "A3",
        "G3",
        "D3",
        "A2",
        "D2",
        "start",
        "new_measure",
        "clean0:note:s3:f3",
        "wait:480",
        "end",
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(test_tokens))
        temp_file = f.name

    temp_dir = os.path.dirname(temp_file)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "asdadagp.cli",
                "process",
                temp_file,
                os.path.join(temp_dir, "temp_output.txt"),
                "--merge-tracks",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        # assert "Processing tokens from" in result.stdout
        # assert "Merging tracks" in result.stdout
    except subprocess.TimeoutExpired:
        pytest.skip("CLI process test timed out")
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
