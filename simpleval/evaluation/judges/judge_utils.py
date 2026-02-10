import os
from pathlib import Path

import boto3

from simpleval.evaluation.consts import MODELS_DIR
from simpleval.evaluation.metrics.consts import METRICS_DIR

BEDROCK_API_KEY_ENV_VAR = 'AWS_BEARER_TOKEN_BEDROCK'


def get_metrics_models_root() -> Path:
    metrics_dir = (Path(__file__).resolve().parent.parent / METRICS_DIR / MODELS_DIR).resolve()
    if not metrics_dir.exists():
        raise FileNotFoundError(f'Metrics dir `{metrics_dir}` not found')
    return metrics_dir


def get_metrics_dir(metric_model: str) -> str:
    metrics_dir = get_metrics_models_root() / metric_model
    if not metrics_dir.exists():
        raise FileNotFoundError(f'Metrics folder `{metrics_dir}` not found')
    return str(metrics_dir)


def verify_env_var(env_var: str):
    """
    Verify if the environment variable is set.
    """
    if not os.getenv(env_var):
        raise ValueError(f'{env_var} environment variable is required.')


def _validate_bedrock_api_key():
    """
    Validate Bedrock API key by calling list_foundation_models.
    boto3 automatically recognizes AWS_BEARER_TOKEN_BEDROCK env var for bearer token authentication.
    """
    try:
        boto3.client('bedrock').list_foundation_models()
    except Exception as e:
        raise RuntimeError('Failed to validate Bedrock API key.') from e


def _validate_sts_credentials():
    """
    Validate STS credentials by calling get_caller_identity.
    """
    try:
        boto3.client('sts').get_caller_identity()
    except Exception as e:
        raise RuntimeError('Failed to validate sts credentials.') from e


def _validate_aws_region():
    """
    Validate that AWS region is configured.
    """
    try:
        session = boto3.session.Session()
        region = session.region_name
        if not region:
            raise ValueError('AWS region is not configured.')
    except Exception as e:
        raise RuntimeError('Failed to retrieve AWS region.') from e


def bedrock_preliminary_checks():
    """
    Run any preliminary checks before the evaluation starts.
    First checks for Bedrock API key, then falls back to STS credentials.
    """
    api_key = os.getenv(BEDROCK_API_KEY_ENV_VAR)

    if api_key:
        # Validate API key using list_foundation_models
        # boto3 automatically uses AWS_BEARER_TOKEN_BEDROCK env var
        _validate_bedrock_api_key()
    else:
        # Fall back to STS credential validation
        _validate_sts_credentials()

    # Region check remains for both paths
    _validate_aws_region()
