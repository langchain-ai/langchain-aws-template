from langchain.memory import ConversationBufferMemory, DynamoDBChatMessageHistory
from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import RetrievalQA

from langchain.prompts import PromptTemplate
from langchain import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
import sys

import config

MAX_HISTORY_LENGTH = 5

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

    retriever = AmazonKendraRetriever(index_id="d30dd38b-d307-4eba-90d0-c274639daf79")
        
    # prompt_template = ChatPromptTemplate.from_messages([
    #     SystemMessagePromptTemplate.from_template("The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know."),
    #     MessagesPlaceholder(variable_name="history"),
    #     HumanMessagePromptTemplate.from_template("{input}")
    # ])

    prompt_template = """
    The following is a friendly conversation between a human and an AI. 
     The AI is talkative and provides lots of specific details from its context.
    If the AI does not know the answer to a question, it truthfully says it 
    does not know.
    {context}
    Instruction: Based on the above documents, provide a detailed answer for, {question} Answer "don't know" 
    if not present in the document. 
    Solution:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    condense_qa_template = """
    Given the following conversation and a follow up question, rephrase the follow up question 
    to be a standalone question.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)
    
    llm = ChatOpenAI(temperature=0, openai_api_key=api_key)
    conversation = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever,
        return_source_documents=True, 
        condense_question_prompt=standalone_question_prompt, 
        verbose=True, 
        # memory=memory,
        combine_docs_chain_kwargs={"prompt":PROMPT} 
    )

    print("success")
    return conversation

def run_chain(chain, prompt: str, history=[]):
  return chain({"question": prompt, "chat_history": history})



