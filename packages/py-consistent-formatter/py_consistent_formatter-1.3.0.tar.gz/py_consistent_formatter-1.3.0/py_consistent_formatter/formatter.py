import io
import sys
from pathlib import Path

import docformatter
import isort
import yapf

from .sort_all import sort_public_exports


def format_text(file_text: str, pyproject_toml: Path) -> str:
    """Formats python source.

    Aggregates several formatters in a deterministic way so that they don't try to fight each other.

    This function performs the following steps:

    - sort strings in __all__ in alphabetical order.
    - apply yapf formatting;
    - apply docformatter;
    - sort imports using isort;

    Args:
        file_text: Python source to format.
        pyproject_toml: Path to the configuration file.

    Returns:
        Formatted source.
    """
    sorted_all = sort_public_exports(file_text)

    (reformatted, _) = yapf.yapf_api.FormatCode(sorted_all, style_config=str(pyproject_toml))

    buffer_in = io.StringIO(reformatted)
    buffer_out = io.StringIO()
    buffer_err = io.StringIO()
    config = docformatter.Configurater(args=['--config', str(pyproject_toml)])
    config.do_parse_arguments()
    config.args.files = ['-']  # Read from stdin
    formatter = docformatter.format.Formatter(
        args=config.args,
        stderror=buffer_err,
        stdout=buffer_out,
        stdin=buffer_in,
    )
    formatter.do_format_standard_in(config.parser)

    buffer_out.seek(0)
    isort_config = isort.Config(
        str(pyproject_toml),
        quiet=True,
        virtual_env=sys.prefix,
    )
    buffer = io.StringIO()
    isort.stream(buffer_out, buffer, config=isort_config)

    formatted_file_text = buffer.getvalue()
    formatted_file_text = formatted_file_text.strip()
    if formatted_file_text != '':
        formatted_file_text += '\n'

    return formatted_file_text
