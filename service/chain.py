from typing import Tuple
from uuid import uuid4
from langchain import ConversationChain, OpenAI
from langchain.memory import ConversationBufferMemory
from memory import DynamoDBChatMessageHistory

import config

def run(api_key: str, session_id: str, prompt: str) -> Tuple[str, str]:
    """This is the main function that executes the prediction chain.
    Updating this code will change the predictions of the service.
    Current implementation creates a new session id for each run, client
    should pass the returned session id in the next execution run, so the
    conversation chain can load message context from previous execution.

    Args:
        api_key: api key for the LLM service, OpenAI used here
        session_id: session id from the previous execution run, pass blank for first execution
        prompt: prompt question entered by the user

    Returns:
        The prediction from LLM and the session id
    """

    if not session_id:
        session_id = str(uuid4())
    
    chat_memory = DynamoDBChatMessageHistory(
        table_name=config.config.DYNAMODB_TABLE_NAME,
        session_id=session_id
    )
    
    # Maintains immutable sessions
    # If previous session was present, create
    # a new session and copy messages, and 
    # generate a new session_id 
    messages = chat_memory._read()
    if messages:
        session_id = str(uuid4())
        chat_memory = DynamoDBChatMessageHistory(
            table_name=config.config.DYNAMODB_TABLE_NAME,
            session_id=session_id
        )
        chat_memory._write(session_id, messages)
    
    memory = ConversationBufferMemory(chat_memory=chat_memory)   
    
    llm = OpenAI(temperature=0.9, model_name="gpt-3.5-turbo", openai_api_key=api_key)
    conversation = ConversationChain(
        llm=llm, 
        verbose=True, 
        memory=memory
    )
    response = conversation.predict(input=prompt)
    
    return response, session_id
