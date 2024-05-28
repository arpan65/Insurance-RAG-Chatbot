# Import necessary libraries
import time
import re
from langchain_core.prompts import PromptTemplate
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_community.vectorstores import FAISS
import boto3
from langchain_aws import BedrockLLM as Bedrock
from langchain_community.embeddings import BedrockEmbeddings
from pathlib import Path
from styles import STYLES,BANNER,TYPING

st.set_page_config(page_title="IVA Bot", page_icon="🤖")
st.markdown(STYLES, unsafe_allow_html=True)

# Top banner with bot logo and status
st.markdown(BANNER, unsafe_allow_html=True)


# Prompt
template = """Use the following pieces of context to answer the question at the end. Please follow the following rules:
1. If you don't know the answer, don't try to make up an answer.
2. If you find the answer, write the answer in a detailed way without references.
{context}
Question: {input}
Helpful Answer:"""

BUCKET_NAME = "rag-bot-source"
file_path = f"/tmp"

# Initialize AWS connectors
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client(service_name="s3")

prompt = PromptTemplate(
    input_variables=["context", "input"],
    template=template,
)

# Method to use the foundational LLM model via bedrock
def get_llama2_llm():
    llm = Bedrock(model_id="meta.llama2-13b-chat-v1", client=bedrock,
                  model_kwargs={'max_gen_len': 512})
    return llm

llm = get_llama2_llm()

bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock)

# Method to download vectors of the policy document from S3
def download_vectors(policy_number):
    s3_vector_faiss_key = 'vectors/policydoc/' + policy_number + '/' + 'policydoc_faiss.faiss'
    s3_vector_pkl_key = 'vectors/policydoc/' + policy_number + '/' + 'policydoc_pkl.pkl'
    Path(file_path).mkdir(parents=True, exist_ok=True)
    s3.download_file(Bucket=BUCKET_NAME, Key=s3_vector_faiss_key, Filename=f"{file_path}/my_faiss.faiss")
    s3.download_file(Bucket=BUCKET_NAME, Key=s3_vector_pkl_key, Filename=f"{file_path}/my_faiss.pkl")
   
# Method to load the vector indexes
def load_faiss_index():
    faiss_index = FAISS.load_local(index_name="my_faiss", folder_path=file_path, embeddings=bedrock_embeddings, allow_dangerous_deserialization=True)
    retriever = faiss_index.as_retriever()
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    chain = create_retrieval_chain(retriever_chain, document_chain)
    return chain

# Methods to retreive chat responses as stream
def get_response(query, chain):
    return chain.stream({"input": query})

def get_streamed_response(prompt, chain):
    chunks = []
    for chunk in get_response(prompt, chain):
        if "answer" in chunk:
            chunks.append(chunk["answer"])
    return ''.join(chunks)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! I'm IVA, your virtual assistant"),
    ]
    time.sleep(2)
    st.session_state.chat_history.append(AIMessage(content="Please enter your policy number to get started"))
    st.session_state.policy_id_validated = False

# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    avatar_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS4h4UlldDaq69Pd6QHlzSVB8yAYH73Gpn5Qkn5R2fYS10XfhpKlr86Ci8-HjyX0ft9Ivw&usqp=CAU" if isinstance(message, HumanMessage) else "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQG1JzTwTj8b1jzq2zKlBbLEf3i-rOLwnmZqQ&usqp=CAU"
    bubble_class = "user-bubble" if isinstance(message, HumanMessage) else "assistant-bubble"
    st.markdown(f"""
        <div class="chat-bubble {bubble_class}">
            <img src="{avatar_url}" class="chat-avatar">
            {message.content}
        </div>
    """, unsafe_allow_html=True)

# Method to validate the policy
def validate_policy_id(policy_id):
    return bool(re.match(r'^AU\d{4}$', policy_id))

# Handle user input
if "awaiting_response" not in st.session_state:
    st.session_state.awaiting_response = False

# Handle user input based on policy validation
if not st.session_state.policy_id_validated:
    prompt_ = st.chat_input("Enter your policy number(e.g., AU1234789):")
else:
    prompt_ = st.chat_input("Type your message here")

if prompt_:
    # Display user message in chat message container
    st.session_state.chat_history.append(HumanMessage(content=prompt_))
    st.session_state.awaiting_response = True
    st.experimental_rerun()

# Handle the response after user input
if st.session_state.awaiting_response:
    typing_indicator = st.empty()
    with typing_indicator:
        st.markdown(TYPING, unsafe_allow_html=True)

    # Check if policy ID is validated or not
    user_input = st.session_state.chat_history[-1].content
    if not st.session_state.policy_id_validated:
        if validate_policy_id(user_input):
            download_vectors(user_input)
            # Load FAISS index and setup chain after vectors are downloaded
            st.session_state.chain = load_faiss_index()
            response = "Policy number validated successfully. How can I help about your policy today?"
            st.session_state.policy_id_validated = True
        else:
            response = "Incorrect policy number. Please enter a valid policy"
    else:
        # Get response from chain
        response = get_streamed_response(user_input, st.session_state.chain)

    # Add the response to chat history
    st.session_state.chat_history.append(AIMessage(content=response))
    st.session_state.awaiting_response = False
    typing_indicator.empty()
    st.experimental_rerun()
