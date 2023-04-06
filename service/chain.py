from typing import Tuple
from uuid import uuid4

from langchain import ConversationChain
from langchain.memory import ConversationBufferMemory, DynamoDBChatMessageHistory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
from langchain.schema import messages_to_dict

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
        The prediction from LLM
    """
    
    if not session_id:
        session_id = str(uuid4())
    
    chat_memory = DynamoDBChatMessageHistory(
        table_name=config.config.DYNAMODB_TABLE_NAME,
        session_id=session_id
    )
    messages = chat_memory.messages

    # Maintains immutable sessions
    # If previous session was present, create
    # a new session and copy messages, and 
    # generate a new session_id 
    if messages:
        session_id = str(uuid4())
        chat_memory = DynamoDBChatMessageHistory(
            table_name=config.config.DYNAMODB_TABLE_NAME,
            session_id=session_id
        )
        # This is a workaround at the moment. Ideally, this should
        # be added to the DynamoDBChatMessageHistory class
        try:
            messages = messages_to_dict(messages)
            chat_memory.table.put_item(
                Item={"SessionId": session_id, "History": messages}
            )
        except Exception as e:
            print(e)
    
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
    
    return response, session_id

