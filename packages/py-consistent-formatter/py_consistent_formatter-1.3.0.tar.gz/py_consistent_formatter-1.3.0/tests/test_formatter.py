import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Iterator, NamedTuple

import pytest


class Assets(NamedTuple):
    unformatted_file_path: Path
    ignored_file_path: Path
    formatted_file_path: Path


@pytest.fixture()
def script_dir() -> Path:
    return Path(__file__).parent


@pytest.fixture()
def assets(script_dir: Path) -> Iterator[Assets]:
    with tempfile.TemporaryDirectory() as temp_dir:
        assets_path = Path(temp_dir)
        (assets_path / 'subfolder').mkdir(parents=True, exist_ok=True)

        unformatted_file_path = assets_path / 'unformatted_file.py'
        ignored_file_path = assets_path / 'subfolder' / 'ignored.py'
        formatted_file_path = assets_path / 'formatted_file.py'

        original_assets_path = script_dir / 'assets'

        shutil.copyfile(original_assets_path / 'unformatted_file.py.bin', unformatted_file_path)
        shutil.copyfile(original_assets_path / 'unformatted_file.py.bin', ignored_file_path)
        shutil.copyfile(original_assets_path / 'formatted_file.py.bin', formatted_file_path)

        yield Assets(
            unformatted_file_path=unformatted_file_path,
            ignored_file_path=ignored_file_path,
            formatted_file_path=formatted_file_path,
        )


def test_format_file(assets: Assets, script_dir: Path) -> None:
    subprocess.run(
        [sys.executable, '-m', 'py_consistent_formatter', assets.unformatted_file_path],
        cwd=script_dir,
        shell=False,
    )

    with open(assets.unformatted_file_path, 'r') as formatted_file:
        print('File after formatting:')
        print()
        for line in formatted_file.readlines():
            sys.stdout.write(line)

    with open(assets.unformatted_file_path, 'r') as unformatted_file:
        with open(assets.formatted_file_path, 'r') as formatted_file:
            assert list(unformatted_file) == list(formatted_file)


def test_ignored_file(assets: Assets, script_dir: Path) -> None:
    subprocess.run(
        [sys.executable, '-m', 'py_consistent_formatter', assets.ignored_file_path],
        cwd=script_dir,
        shell=False,
    )

    with open(assets.unformatted_file_path, 'r') as formatted_file:
        print('File after formatting:')
        print()
        for line in formatted_file.readlines():
            sys.stdout.write(line)

    with open(assets.ignored_file_path, 'r') as ignored_file:
        with open(assets.unformatted_file_path, 'r') as unformatted_file:
            assert list(ignored_file) == list(unformatted_file)
