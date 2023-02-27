
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # openai key is expected to be saved in SecretsManager under openai-key name
    API_KEYS_SECRET_NAME = "api-keys"

    # Needed for reading secrets from SecretManager
    # See https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html#ps-integration-lambda-extensions-add
    # for extension arn in other regions
    SECRETS_EXTENSION_ARN = "arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4"


config = Config()