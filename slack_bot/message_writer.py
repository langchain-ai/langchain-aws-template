import json
import os

from typing import Dict, Union

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


from models import SlackMessage
import chain

import config
import requests


import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def handler(event, context):
    """Lambda handler that pulls the messages from the
    sqs queue, and calls the LLM chain to process the
    user's message. This lambda writes the response from
    the LLM chain to the slack thread.
    """

    logging.debug(event)
    
    record = event['Records'][0]
    body = json.loads(record['body'])
    slack_message = SlackMessage(body=body)
    
    try:
        response_text = chain.run(
            api_key=get_api_key("openai-api-key"), 
            session_id=slack_message.thread, 
            prompt=slack_message.sanitized_text()
        )
        
        slack_token = get_api_key("slack-bot-token")
        client = WebClient(token=slack_token)
        
        client.chat_postMessage(
            channel=slack_message.channel,
            thread_ts=slack_message.thread,
            text=response_text
        )
    except SlackApiError as e:
        assert e.response["error"]
        logging.error(e)
    
    return build_response("Processed message successfully!")


def build_response(body: Union[Dict, str]):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def get_api_key(key: str ):
    """Fetches the api keys saved in Secrets Manager"""

    headers = {
        "X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')
    }
    secrets_extension_endpoint = "http://localhost:2773" + \
    "/secretsmanager/get?secretId=" + \
    config.config.API_KEYS_SECRET_NAME
  
    r = requests.get(secrets_extension_endpoint, headers=headers)
    secret = json.loads(json.loads(r.text)["SecretString"])

    return secret[key]