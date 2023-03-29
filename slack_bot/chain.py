from typing import Tuple
from uuid import uuid4
from langchain.memory import ConversationBufferMemory
from langchain import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
from memory import DynamoDBChatMessageHistory

import config

def run(api_key: str, session_id: str, prompt: str) -> str:
    """This is the main function that executes the prediction chain.
    Updating this code will change the predictions of the service.

    Args:
        api_key: api key for the LLM service, OpenAI used here
        session_id: session id key to store the history
        prompt: prompt question entered by the user

    Returns:
        The prediction from LLM
    """
    
    chat_memory = DynamoDBChatMessageHistory(
        table_name=config.config.DYNAMODB_TABLE_NAME,
        session_id=session_id
    )
    
    memory = ConversationBufferMemory(chat_memory=chat_memory, return_messages=True)   
        
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know."),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    llm = ChatOpenAI(temperature=0, openai_api_key=api_key)
    conversation = ConversationChain(
        llm=llm, 
        prompt=prompt_template,
        verbose=True, 
        memory=memory
    )
        
    response = conversation.predict(input=prompt)
    
    return response
