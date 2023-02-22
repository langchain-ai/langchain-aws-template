
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    API_KEYS_SECRET_NAME = "api-keys"
    SECRETS_EXTENSION_ARN = "arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4"

config = Config()