import importlib
import inspect
from pathlib import Path
from typing import Dict, List

from simpleval.evaluation.consts import MODELS_DIR
from simpleval.evaluation.judges.base_judge import BaseJudge
from simpleval.evaluation.judges.consts import JUDGE_MODULE_FILE, JUDGE_PACKAGE


class JudgeProvider:
    INTERNAL_JUDGES = ['dummy_judge']

    @staticmethod
    def list_judges(filter_internal=False) -> List[str]:
        """
        Returns a dictionary of available judges.
        """
        judges_dir = Path(JudgeProvider.judges_dir())
        judge_names = [path.name for path in judges_dir.iterdir() if path.is_dir() and (path / JUDGE_MODULE_FILE).is_file()]
        if filter_internal:
            judge_names = [name for name in judge_names if name not in JudgeProvider.INTERNAL_JUDGES]

        return sorted(judge_names)

    @staticmethod
    def get_all_judges() -> Dict[str, BaseJudge]:
        """
        Get all judges available in the judges directory.
        :return: A dictionary of judge name to judge object.
        """
        judge_names = JudgeProvider.list_judges()
        judges = {judge_name: JudgeProvider().get_judge(judge_name) for judge_name in judge_names}

        return judges

    @staticmethod
    def get_judge(judge_name: str, model_id: str = None) -> BaseJudge:
        """
        Get a judge object by its name.
        """
        package_name = JUDGE_PACKAGE.format(judge_name=judge_name)

        try:
            module = importlib.import_module(package_name)
        except ModuleNotFoundError as e:
            raise ValueError(f'Judge `{judge_name}` module not found') from e

        return JudgeProvider._get_judge_object(module=module, model_id=model_id)

    @staticmethod
    def _get_judge_object(module: str, model_id: str) -> BaseJudge:
        # Find all classes that inherit from BaseJudge (directly or indirectly)
        judge_classes = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if inspect.isclass(attr) and issubclass(attr, BaseJudge) and attr is not BaseJudge:
                judge_classes.append(attr)

        if not judge_classes:
            raise ValueError('Module must implement a class that inherits from `BaseJudge`')

        # Find the leaf class (the one that doesn't appear as a base class in any other judge class)
        leaf_classes = []
        for cls in judge_classes:
            if not any(cls in other.__bases__ for other in judge_classes):
                leaf_classes.append(cls)

        if not leaf_classes:
            # This should only happen in case of circular inheritance or other unusual class structures
            raise ValueError('Could not determine leaf class in inheritance hierarchy. Check for circular inheritance.')

        # Return the first leaf class
        return leaf_classes[0](model_id=model_id)

    @staticmethod
    def judges_dir() -> str:
        judges_dir = (Path(__file__).resolve().parent / MODELS_DIR).resolve()
        if not judges_dir.exists():
            raise FileNotFoundError(f'Judges dir `{judges_dir}` not found')

        return str(judges_dir)
