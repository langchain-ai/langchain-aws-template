import json
import os

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

import boto3
from botocore.exceptions import ClientError

from langchain.chains.base import Memory
from langchain.chains.conversation.memory import _get_prompt_input_key, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import ConversationChain

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import langchain

import config
import requests


class BufferDDBStore:
    def __init__(self, table_name):
        self.table_name = table_name
        self.ddb = boto3.client("dynamodb")

    def read(self, session_id: str) -> str:
        try: 
            response = self.ddb.get_item(TableName=self.table_name, Key={'SessionId': {'S': session_id}})
        except ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warn("No record found with session id: %s", session_id)
            else:
                logger.error(error)
        
        if response and 'Item' in response:
            return response['Item']['History']['S']
        
        return ''

    def write(self, session_id: str, history: str):
        try:
            self.ddb.put_item(
                TableName=self.table_name,
                Item={
                    'SessionId': {
                        'S': session_id
                    },
                    'History': {
                        'S': history
                    }
                }
            )
        except ClientError as err:
            logger.error(err)


class ConversationBufferStoreMemory(Memory, BaseModel):
    """Buffer for storing conversation memory."""

    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    """Prefix to use for AI generated responses."""
    buffer: BufferDDBStore
    output_key: Optional[str] = None
    input_key: Optional[str] = None
    memory_key: str = "history"  #: :meta private:
    session_id: str

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Return history buffer."""
        return {self.memory_key: self.buffer.read(self.session_id)}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        if self.input_key is None:
            prompt_input_key = _get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) != 1:
                raise ValueError(f"One output key expected, got {outputs.keys()}")
            output_key = list(outputs.keys())[0]
        else:
            output_key = self.output_key
        human = f"{self.human_prefix}: " + inputs[prompt_input_key]
        ai = f"{self.ai_prefix}: " + outputs[output_key]
        self.buffer.write(
            session_id=self.session_id,
            history=self.buffer.read(self.session_id) + "\n" + "\n".join([human, ai])
        ) 

    def clear(self) -> None:
        """Clear memory contents."""
        self.buffer = ""


def get_secret():
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}
    secrets_extension_endpoint = "http://localhost:2773" + \
    "/secretsmanager/get?secretId=" + \
    config.config.API_KEYS_SECRET_NAME
  
    r = requests.get(secrets_extension_endpoint, headers=headers)
    secret = json.loads(json.loads(r.text)["SecretString"])

    return secret["openai-api-key"]

def handler(event, context): 
    body = json.loads(event["body"])
    
    if "prompt" not in body:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "error",
                "message": "prompt missing in payload"
            })
            
        }
    
    if "session_id" not in body:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "error",
                "message": "session_id missing in payload"
            })
            
        }
    
    prompt = body['prompt']
    session_id = body["session_id"]
    if session_id:
        memory = ConversationBufferStoreMemory(
            buffer=BufferDDBStore(table_name="conversation-store"),
            session_id=session_id
        )
    else:
        memory = ConversationBufferMemory()
    
    llm = langchain.OpenAI(temperature=0.9, openai_api_key=get_secret())
    conversation = ConversationChain(
        llm=llm, 
        verbose=True, 
        memory=memory
    )
    response = conversation.predict(input=prompt)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "response": response
        })
    }
