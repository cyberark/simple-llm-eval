from simpleval.commands.init_command.init_interactive import InitInteractive


def init_command() -> None:
    """
    Initializes a new evaluation folder structure with necessary files and directories.

    Raises:
        SystemExit: If the evaluation folder already exists or if an error occurs during the creation process.
    """

    init_interactive = InitInteractive(post_instructions_start_index=1)
    init_interactive.run_init_command()
