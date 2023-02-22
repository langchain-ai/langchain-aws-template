import json
import os

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import langchain

import config
import requests


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

    llm = langchain.OpenAI(temperature=0.9, openai_api_key=get_secret())
    response = llm(body['prompt'])

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "response": response
        })
    }