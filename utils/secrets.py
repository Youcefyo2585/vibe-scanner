"""Secret resolution for VibeScan.

Reads from environment variables first (with .env loaded via python-dotenv).
If `SSM_PREFIX` is set, falls back to AWS SSM Parameter Store under that
prefix — useful for ECS/Fargate deploys, opt-in for everyone else. boto3 is
imported lazily so users without AWS credentials don't need it installed.
"""

import os

from dotenv import load_dotenv


load_dotenv()


def _coerce(value):
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def get_secret(name, default=None):
    if name in os.environ:
        return _coerce(os.environ[name])

    ssm_prefix = os.environ.get("SSM_PREFIX")
    if not ssm_prefix:
        return default

    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        return default

    try:
        client = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        resp = client.get_parameter(Name=f"{ssm_prefix}{name}", WithDecryption=True)
        return _coerce(resp["Parameter"]["Value"])
    except ClientError:
        return default
