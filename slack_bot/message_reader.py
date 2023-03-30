import json
import os

from typing import Dict, Union

import boto3

from langchain.memory import DynamoDBChatMessageHistory
from models import SlackMessage


import config
import requests


import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def handler(event, context):
    """Lambda handler that reads the messages from slack and
    distributes them to an sqs queue or DynamoDB store based on 
    whether message was directly addressed to the bot (a message
    that starts with `@bot-name`) or a conversation between two
    or more slack users. Note that the conversation history is only
    stored after the first direct message to the bot is received.
    """

    body = json.loads(event['body'])
    
    logging.debug(body)
    
    # For initial validation call from slack
    if "challenge" in body:
        challenge = body["challenge"]
        return build_response({"challenge": challenge})

    sqs = boto3.client('sqs')
    queue_url = sqs.get_queue_url(
        QueueName=config.config.MESSAGE_QUEUE_NAME,
    )
    
    slack_message = SlackMessage(body)
    chat_memory = DynamoDBChatMessageHistory(
        table_name=config.config.DYNAMODB_TABLE_NAME,
        session_id=slack_message.thread
    )
    messages = chat_memory.messages
    
    logging.debug(f"Thread id is {slack_message.thread}")

    try:
        if not slack_message.is_bot_reply():
            if slack_message.is_direct_message():
                logging.debug("Sending message to queue")
                
                # send to queue
                sqs.send_message(
                    QueueUrl=queue_url["QueueUrl"],
                    MessageBody=(event['body']),
                    MessageGroupId=str(slack_message.thread),
                    MessageDeduplicationId=slack_message.event_id
                )
            elif messages:
                logging.debug("Saving message to history")

                # add to memory for context
                chat_memory.add_user_message(slack_message.sanitized_text())

        logging.info(f"Done processing message with event id: {slack_message.event_id}")
    except Exception as e:
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


def get_api_key():
    """Fetches the api keys saved in Secrets Manager"""

    headers = {
        "X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')
    }
    secrets_extension_endpoint = "http://localhost:2773" + \
    "/secretsmanager/get?secretId=" + \
    config.config.API_KEYS_SECRET_NAME
  
    r = requests.get(secrets_extension_endpoint, headers=headers)
    secret = json.loads(json.loads(r.text)["SecretString"])

    return secret["openai-api-key"]