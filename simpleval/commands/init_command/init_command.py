from typing import Tuple

from simpleval.commands.init_command.init_interactive import InitInteractive


def init_command(names: Tuple[str, ...] = ()) -> None:
    """
    Initializes a new evaluation folder structure with necessary files and directories.

    Args:
        names: Optional tuple of evaluation set names provided via CLI.
               If empty, the user will be prompted interactively for a single name.

    Raises:
        SystemExit: If the evaluation folder already exists or if an error occurs during the creation process.
    """

    init_interactive = InitInteractive(names=names, post_instructions_start_index=1)
    init_interactive.run_init_command()
