from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from langchain.schema import BaseMessage, HumanMessage, AIMessage, _message_to_dict, messages_from_dict
from langchain.memory.chat_memory import ChatMessageHistory


import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoDBChatMessageHistory(ChatMessageHistory):
    """Chat message history that stores messages in DynamoDB. 
    DynamoDB has a limitation of max item size of 400kb. Ensure
    that conversation history does not exceed this size limit. 
    """

    session_id: str
    table_name: str
    table: Optional[Any] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        client = boto3.resource("dynamodb")
        self.table = client.Table(self.table_name)
    
    def _read(self) -> List[Dict]:
        try: 
            response = self.table.get_item(
                Key={'SessionId': self.session_id}
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warn("No record found with session id: %s", self.session_id)
            else:
                logger.error(error)
        else:
            if response and 'Item' in response:
                return response['Item']['History']
        
        return []

    def add_user_message(self, message: str) -> None:
        self._add_message(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
       self._add_message(AIMessage(content=message))

    def _add_message(self, message: BaseMessage) -> None:
        messages_ = self._read()
        messages_.append(_message_to_dict(message))
        self._write(self.session_id, messages_)

    def _write(self, session_id: str, messages: List[Dict]):
        try:
            self.table.put_item(
                Item={
                    'SessionId': session_id,
                    'History': messages
                }
            )
            self.messages = messages_from_dict(messages)
        except ClientError as err:
            logger.error(err)
    
    def clear(self):
        try:
            self.table.delete_item(
                Key={'SessionId': self.session_id}
            )
            self.messages = []
        except ClientError as err:
            logger.error(err)
