
from dataclasses import dataclass
import boto3


@dataclass(frozen=True)
class Config:
    # openai key is expected to be saved in SecretsManager under openai-api-key name
    API_KEYS_SECRET_NAME = "api-keys"

    session = boto3.Session()
    account_id = session.client('sts').get_caller_identity().get('Account')
    region = session.region_name

    
    # Needed for reading secrets from SecretManager
    # See https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html#ps-integration-lambda-extensions-add
    # for extension arn in other regions
    SECRETS_EXTENSION_ARN = f'arn:aws:lambda:{region}:{account_id}:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4'

    # Dynamo db table that stores the conversation history
    DYNAMODB_TABLE_NAME = "conversation-history-store"


config = Config()