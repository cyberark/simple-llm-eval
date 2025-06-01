import json
import uuid
from unittest import mock

from simpleval.commands.init_command import init_command, init_from_template_command


def verify_eval_config_file(eval_dir, expected):
    config_path = eval_dir / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    assert config["name"] == eval_dir.name, config
    assert config["max_concurrent_judge_tasks"] == expected["max_concurrent_judge_tasks"], config
    assert config["max_concurrent_llm_tasks"] == expected["max_concurrent_llm_tasks"], config
    assert config["llm_as_a_judge_name"] == expected["llm_as_a_judge_name"], config
    assert config["eval_metrics"] == expected["eval_metrics"], config


def test_init_command_creates_eval_set(tmp_path):
    eval_dir = tmp_path / f"temp_{uuid.uuid4()}"
    testcase = "testcase"

    input_values = [str(eval_dir), testcase]
    def input_side_effect(prompt):
        return input_values.pop(0)

    metrics_from_user = ['correctness', 'accuracy', 'relevancy']
    
    with mock.patch("builtins.input", side_effect=input_side_effect), \
         mock.patch("simpleval.commands.init_command.user_functions.pick_judge", return_value="dummy_judge"), \
         mock.patch("simpleval.commands.init_command.user_functions.get_model_id_from_user", return_value="dummy_model_id"), \
         mock.patch("simpleval.commands.init_command.user_functions.get_metrics_from_user", return_value=metrics_from_user), \
         mock.patch("simpleval.commands.init_command.user_functions.get_concurrency_values", return_value=(10, 10)):
        init_command.init_command()

    verify_eval_config_file(
        eval_dir,
        {
            "max_concurrent_judge_tasks": 10,
            "max_concurrent_llm_tasks": 10,
            "llm_as_a_judge_name": "dummy_judge",
            "eval_metrics": metrics_from_user,
        }
    )    


def test_init_from_template_command_runs(tmp_path):
    eval_dir = tmp_path / f"temp_{uuid.uuid4()}"
    testcase = "testcase"
    init_from_template_command.init_from_template_command(str(eval_dir), testcase)

    verify_eval_config_file(
        eval_dir,
        {
            "max_concurrent_judge_tasks": 10,
            "max_concurrent_llm_tasks": 10,
            "llm_as_a_judge_name": "open_ai",
            "eval_metrics": [],
        }
    )    
