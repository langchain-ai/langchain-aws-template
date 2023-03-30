import json
import os
from typing import Dict, Union

import requests

import config


def build_response(body: Union[Dict, str]):
    """Builds response for lambda"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def get_secrets() -> Dict[str, str]:
    """Fetches the api keys saved in Secrets Manager"""

    headers = {
        "X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')
    }
    secrets_extension_endpoint = "http://localhost:2773" + \
    "/secretsmanager/get?secretId=" + \
    config.config.API_KEYS_SECRET_NAME
  
    r = requests.get(secrets_extension_endpoint, headers=headers)
    secrets = json.loads(json.loads(r.text)["SecretString"])

    return secrets