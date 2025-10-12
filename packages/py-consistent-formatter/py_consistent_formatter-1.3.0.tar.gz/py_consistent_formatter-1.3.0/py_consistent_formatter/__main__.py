"""Script for formatting multiple Python files.

The formatting is done in-place. If formatting doesn't change the
contents of the file, the file will not be overwritten.
"""
import argparse
import sys
from pathlib import Path
from typing import List

import yapf

from .formatter import format_text


def find_pyproject_toml() -> Path:
    """Finds nearest pyproject.toml file by looking in parent directories.
    
    Returns:
        Path to the nearest pyproject.toml file.
    """
    current_directory = Path.cwd()
    while current_directory != current_directory.parent:
        pyproject_toml = current_directory / 'pyproject.toml'
        if pyproject_toml.exists():
            return pyproject_toml
        current_directory = current_directory.parent

    raise FileNotFoundError('pyproject.toml not found')


def format_file(file_path: Path, pyproject_toml: Path) -> None:
    """In-place formats python source file.

    If the formatting does not change the contents of the file, the file will not be overwritten.

    Args:
        file_path: Path to the file to format.
        pyproject_toml: Path to the configuration file.
    """
    try:
        with open(file_path, 'r') as fd:
            file_text = fd.read()

        formatted_file_text = format_text(file_text, pyproject_toml)

        if formatted_file_text != file_text:
            with open(file_path, 'w') as fd:
                fd.write(formatted_file_text)
    except Exception as error:
        print(f'Cannot format {file_path}: {error}')


def format_files(file_paths: List[Path]) -> None:
    """In-place formats multiple files.

    Args:
        file_paths: Paths to files to format.
    """
    pyproject_toml = find_pyproject_toml()

    for file_path in file_paths:
        format_file(file_path, pyproject_toml)


def main() -> int:
    """Script entry point.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__, prog='py-consistent-formatter')
    parser.add_argument(
        'python_files',
        metavar='python-file',
        nargs='+',
        type=Path,
        help='Path to file to format',
    )
    args = parser.parse_args()

    exclude_patterns_from_ignore_file = yapf.file_resources.GetExcludePatternsForDir(str(Path.cwd()))
    files = [Path(file) for file in yapf.file_resources.GetCommandLineFiles([str(file) for file in args.python_files], False, exclude_patterns_from_ignore_file)]

    format_files(files)

    return 0


if __name__ == '__main__':
    sys.exit(main())
