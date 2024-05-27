#1 import the OS, Bedrock, ConversationChain, ConversationBufferMemory Langchain Modules
import os
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain,ConversationalRetrievalChain
from langchain_aws import BedrockLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains import create_history_aware_retriever
# create chain for documents
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import BedrockEmbeddings
from langchain_aws import BedrockLLM as Bedrock
## Data Ingestion
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader,PyPDFLoader
# Vector Embedding And Vector Store
from langchain.vectorstores import FAISS
import boto3
from langchain.chains import create_retrieval_chain
prompt_template = """

Human: Use the following pieces of context to provide a 
concise answer to the question at the end but usse atleast summarize with 
250 words with detailed explaantions. If you don't know the answer, 
just say that you don't know, don't try to make up an answer.
<context>
{context}
</context

Question: {question}

Assistant:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

#2a Write a function for invoking model- client connection with Bedrock with profile, model_id & Inference params- model_kwargs
def demo_chatbot():
    demo_llm = BedrockLLM(
       credentials_profile_name='default',
       model_id='meta.llama2-70b-chat-v1',
       model_kwargs= {
        "temperature": 0.9,
        "top_p": 0.5,
        "max_gen_len": 512})
    return demo_llm
    
#3 Create a Function for ConversationBufferMemory (llm and max token limit)
def demo_memory():
    llm_data=demo_chatbot()
    memory = ConversationBufferMemory(llm=llm_data, max_token_limit= 512)
    return memory

#4 Create a Function for Conversation Chain - Input text + Memory
def demo_conversation(input_text,memory):
    llm_chain_data = demo_chatbot()
    llm_conversation= ConversationChain(llm=llm_chain_data,memory= memory,verbose=False)
    llm_conversation.prompt.template = """System: The following is a friendly conversation between a knowledgeable helpful assistant and a customer. The assistant is talkative and provides lots of specific details from it's context.\n\nCurrent conversation:\n{history}\nUser: {input}\nBot:"""
    chat_reply = llm_conversation.predict(input=input_text)
    return chat_reply
    

def chat_response(llm,retriever,chat_history,query):
    prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ] )
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions based on the below context:\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
    ])
    document_chain = create_stuff_documents_chain(llm, prompt)
    conversational_retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)
    response = conversational_retrieval_chain.invoke({
            'chat_history': chat_history,
            "input":query
            })
    return response['answer']


## Data ingestion
def data_ingestion():
    loader = PyPDFLoader("http://www.axainsurance.com/home/policy-wording/policywording_153.pdf")
    documents=loader.load()
    # - in our testing Character split works better with this PDF data set
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,
                                                 chunk_overlap=100)
    docs=text_splitter.split_documents(documents)
    return docs



## Vector Embedding and vector store
def get_vector_store(docs,bedrock_embeddings):
    vectorstore_faiss=FAISS.from_documents(
        docs,
        bedrock_embeddings
    )
    vectorstore_faiss.save_local("faiss_index")