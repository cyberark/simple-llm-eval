from simpleval.commands.init_command.init_from_template import InitFromTemplate


def init_from_template_command(eval_dir: str, testcase: str) -> None:
    """
    Initializes a new evaluation folder structure with necessary files and directories.

    Args:
        eval_dir (str): The full path of the new evaluation folder (folder must not exist).
        testcase (str): The name of the testcase to be used. e.g. "nova-micro" or "new-prompts2"

    Raises:
        SystemExit: If the evaluation folder already exists or if an error occurs during the creation process.
    """

    init_from_template = InitFromTemplate(eval_dir=eval_dir, testcase=testcase, post_instructions_start_index=2)
    init_from_template.run_init_command()
