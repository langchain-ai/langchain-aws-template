from langchain import ConversationChain, OpenAI
from memory import ConversationBufferStoreMemory, DynamoDBStore

import config

def run(api_key: str, session_id: str, prompt: str) -> str:
    memory = ConversationBufferStoreMemory(
        buffer=DynamoDBStore(table_name=config.config.DYNAMODB_TABLE_NAME),
        session_id=session_id
    )   
    
    llm = OpenAI(temperature=0.9, openai_api_key=api_key)
    conversation = ConversationChain(
        llm=llm, 
        verbose=True, 
        memory=memory
    )
    response = conversation.predict(input=prompt)
    
    return response, memory.session_id