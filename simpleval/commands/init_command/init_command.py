from simpleval.commands.init_command.init_interactive import InitInteractive
from simpleval.commands.init_command.user_functions import get_eval_config_from_user, get_testcase_name_from_user


def init_command(names: tuple = ()) -> None:
    """
    Initializes a new evaluation folder structure with necessary files and directories.

    Args:
        names: Optional tuple of evaluation set names. If provided, creates multiple eval sets
               with shared testcase and config. If empty, prompts interactively for a single name.

    Raises:
        SystemExit: If the evaluation folder already exists or if an error occurs during the creation process.
    """

    if not names:
        # Original behavior - single interactive creation
        init_interactive = InitInteractive(post_instructions_start_index=1)
        init_interactive.run_init_command()
    else:
        # Create multiple eval sets with provided names
        # Collect testcase and config once, then reuse for all eval sets
        testcase = get_testcase_name_from_user()
        config = get_eval_config_from_user()

        for name in names:
            init_interactive = InitInteractive(
                post_instructions_start_index=1,
                eval_dir=name,
                testcase=testcase,
                config=config
            )
            init_interactive.run_init_command()
