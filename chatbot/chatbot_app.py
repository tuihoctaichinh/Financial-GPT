import streamlit as st
import os
import openai
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma

# Initialize OpenAI embeddings
openai.api_key = os.environ.get('OPENAI_API_KEY')
embedding = OpenAIEmbeddings()

# Specify the directory for persistent storage
persist_directory = os.path.dirname(os.getcwd()) + '\\data\\chroma\\vietcap_reports'

# Initialize Chroma with embeddings and directory
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)

# Initialize ChatOpenAI with temperature set to 0
llm = ChatOpenAI(temperature=0)

# Set up RetrievalQA with the language model and retriever
qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectordb.as_retriever(search_kwargs={"k": 3}))  

# Streamlit app
st.title("Financial GPT")

# Input field for question
question = st.text_input("Enter your question:")

# Button to ask question
if st.button("Ask"):
    if question:
        result = qa_chain({"query": question})
        st.write("Answer:", result["result"])
    else:
        st.write("Please enter a question.")

# Note: No need for a close button or a main loop as Streamlit handles these automatically.

