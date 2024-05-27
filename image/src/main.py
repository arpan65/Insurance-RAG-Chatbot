## We will be suing Titan Embeddings Model To generate Embedding
from langchain_community.embeddings import BedrockEmbeddings
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader,PyPDFLoader
# Vector Embedding And Vector Store
from langchain.vectorstores import FAISS
import boto3
from pathlib import Path

BUCKET_NAME='rag-bot-source'

# Configure AWS credentials
bedrock=boto3.client(service_name="bedrock-runtime")
bedrock_embeddings=BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",client=bedrock)
s3 = boto3.client("s3")

def handler(event, context):
    # read the key of uploaded file
    key=event['Records'][0]['s3']['object']['key']
    key=key.replace('+',' ')
    # extract policy number
    policy_number=key.split('_')[-1]
    policy_number=policy_number.split('.')[0]
    print('key:',key,'policy:',policy_number)
    # download the file in temporary storage
    file_name_full = key.split("/")[-1]
    s3.download_file(BUCKET_NAME, key, f"/tmp/{file_name_full}")
    # load the files
    loader = PyPDFLoader(f"/tmp/{file_name_full}")
    docs=loader.load()
    print('loaded')
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,
                                                 chunk_overlap=100)
    # split the documents
    docs=text_splitter.split_documents(docs)
    vectorstore_faiss=FAISS.from_documents(
        docs,
        bedrock_embeddings
    )
    # save the vectors in local
    file_path = f"/tmp/"
    Path(file_path).mkdir(parents=True, exist_ok=True)
    file_name = "faiss_index.bin"
    vectorstore_faiss.save_local(index_name=file_name, folder_path=file_path)
    s3_vector_faiss_key='vectors/policydoc/'+policy_number+'/'+'policydoc_faiss.faiss'
    s3_vector_pkl_key='vectors/policydoc/'+policy_number+'/'+'policydoc_pkl.pkl'
    # upload the vectors to s3 bucket
    s3.upload_file(Filename=file_path + "/" + file_name + ".faiss", Bucket=BUCKET_NAME, Key=s3_vector_faiss_key)
    s3.upload_file(Filename=file_path + "/" + file_name + ".pkl", Bucket=BUCKET_NAME, Key=s3_vector_pkl_key)
    print('upload key:',s3_vector_pkl_key)
    print('files uploaded sucessfuly')
    # return the response
    return {
        "statusCode": 200,
        "body": {"message": "Vector Index Saved Sucessfuly", "path": s3_vector_faiss_key},
    }