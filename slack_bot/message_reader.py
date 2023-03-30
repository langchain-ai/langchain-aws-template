import json

import boto3

from langchain.memory import DynamoDBChatMessageHistory
from models import SlackMessage


import config
import utils


import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        return utils.build_response({"challenge": challenge})

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
                logging.info(f"Sending message with event_id: {slack_message.event_id} to queue")
                
                # send to queue
                sqs.send_message(
                    QueueUrl=queue_url["QueueUrl"],
                    MessageBody=(event['body']),
                    MessageGroupId=str(slack_message.thread),
                    MessageDeduplicationId=slack_message.event_id
                )
            elif messages:
                logging.debug(f"Saving message with event_id: {slack_message.event_id} to history")

                # add to memory for context
                chat_memory.add_user_message(slack_message.sanitized_text())

        logging.info(f"Done processing message with event id: {slack_message.event_id}")
    except Exception as e:
        logging.error(e)
    
    return utils.build_response("Processed message successfully!")

