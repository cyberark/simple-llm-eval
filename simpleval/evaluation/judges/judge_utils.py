import os
from pathlib import Path

import boto3

from simpleval.evaluation.consts import MODELS_DIR
from simpleval.evaluation.metrics.consts import METRICS_DIR


def get_metrics_models_root():
    metrics_dir = (Path(__file__).resolve().parent.parent / METRICS_DIR / MODELS_DIR).resolve()
    if not metrics_dir.exists():
        raise FileNotFoundError(f'Metrics dir `{metrics_dir}` not found')
    return str(metrics_dir)


def get_metrics_dir(metric_model: str) -> str:
    metrics_dir = os.path.join(get_metrics_models_root(), metric_model)
    if not os.path.exists(metrics_dir):
        raise FileNotFoundError(f'Metrics folder `{metrics_dir}` not found')
    return metrics_dir


def verify_env_var(env_var: str):
    """
    Verify if the environment variable is set.
    """
    if not os.getenv(env_var):
        raise ValueError(f'{env_var} environment variable is required.')


def bedrock_preliminary_checks():
    """
    Run any preliminary checks before the evaluation starts.
    """
    try:
        boto3.client('sts').get_caller_identity()
    except Exception as e:
        raise RuntimeError('Failed to validate sts credentials.') from e

    try:
        session = boto3.session.Session()
        region = session.region_name
        if not region:
            raise ValueError('AWS region is not configured.')
    except Exception as e:
        raise RuntimeError('Failed to retrieve AWS region.') from e
