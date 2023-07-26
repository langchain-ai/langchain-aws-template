import json

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from models import SlackMessage
import chain

import utils
import config

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        SECRETS = utils.get_secrets()
        API_KEY = SECRETS["openai-api-key"]
        SLACK_TOKEN = SECRETS["slack-bot-token"]
        INDEX_ID = config.config.KENDRA_INDEX_ID

        logging.info(f"Sending message with event_id: {slack_message.event_id} to LLM chain")
        
        response_text = chain.run(
            api_key=API_KEY, 
            session_id=slack_message.thread,
            kendra_index_id = INDEX_ID, 
            prompt=slack_message.sanitized_text()
        )
        
        client = WebClient(token=SLACK_TOKEN)
        
        logging.info(f"Writing response for message with event_id: {slack_message.event_id} to slack")

        client.chat_postMessage(
            channel=slack_message.channel,
            thread_ts=slack_message.thread,
            text=response_text
        )
    except SlackApiError as e:
        assert e.response["error"]
        logging.error(e)
    
    return utils.build_response("Processed message successfully!")


