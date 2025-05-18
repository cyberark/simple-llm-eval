from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EvalTaskOverrides(BaseModel):
    max_concurrent_judge_tasks: int = Field(None, ge=1)
    max_concurrent_llm_tasks: int = Field(None, ge=1)


class EvalTaskConfig(BaseModel):
    """
    Evaluation config.

    name: Name of the evaluation task.
    max_concurrent_judge_tasks: Maximum number of concurrent judge tasks.
    max_concurrent_llm_tasks: Maximum number of concurrent LLM tasks.
    eval_metrics: List of evaluation metrics
    llm_as_a_judge_name: LLM model to be used as a judge model.
    llm_as_a_judge_model_id: LLM model ID to be used as a judge model (if different from llm_as_a_judge_name default model id).
    override: Dictionary of testcase-specific overrides.

    Run `simpleval metrics-explorer` to learn about the available judge models and metrics
    See documentation for more details.
    """

    name: str
    max_concurrent_judge_tasks: int = Field(..., ge=1)
    max_concurrent_llm_tasks: int = Field(..., ge=1)
    eval_metrics: List[str]
    llm_as_a_judge_name: str
    llm_as_a_judge_model_id: Optional[str] = None

    override: Dict[str, EvalTaskOverrides] = {}

    def effective_max_concurrent_judge_tasks(self, testcase: str = None):
        # Get the override value if override exists and if value is not None, otherwise use the default value
        return self.override.get(testcase, self).max_concurrent_judge_tasks or self.max_concurrent_judge_tasks

    def effective_max_concurrent_llm_tasks(self, testcase: str = None):
        # Get the override value if override exists and if value is not None, otherwise use the default value
        return self.override.get(testcase, self).max_concurrent_llm_tasks or self.max_concurrent_llm_tasks
