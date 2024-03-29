import streamlit as st
import os
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback
import json 

sysmessage = """
You are a company information extractor.
You will receive question from users, you will first separate the question into sub-questions
Give detailed answers for each sub-question (include data if available) based on the below context, 
and generate 3 related questions that users might be interested in.
Answer I don't know if the information is not in the context.
"""

# Specify the directory for persistent storage
persist_directory = os.path.dirname(os.getcwd()) + '\\data\\chroma\\vietcap_reports'
embedding = OpenAIEmbeddings()
# Initialize Chroma with embeddings and directory
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)

# Define your desired data structure.
class Answer(BaseModel):
    answer_: str = Field(description="answer of the user's query")
    related_q1: str = Field(description="related question no.1")
    related_q2: str = Field(description="related question no.2")
    related_q3: str = Field(description="related question no.3")
        
def qachatbot(question, include_prompt=False, structured_result=False):
    if not include_prompt and structured_result:
        raise Exception("include prompt if want to have structured answer")
    #---------------------------------------------------#
    # Initialize OpenAI embeddings
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    # Initialize ChatOpenAI with temperature set to 0
    llm = ChatOpenAI(temperature=0)
    
    #---------------------------------------------------#
    if include_prompt and structured_result:
        template = sysmessage + """
        Context: {context}
        Question: {question}
        {format_instructions}
        """
        # Set up a parser + inject instructions into the prompt template.
        parser = JsonOutputParser(pydantic_object=Answer)
        
        # Instantiation using initializer
        prompt = PromptTemplate(input_variables=["query","context"],
                                partial_variables={"format_instructions": parser.get_format_instructions()},
                                template=template)

        # Set up RetrievalQA with the language model and retriever
        qa_chain = RetrievalQA.from_chain_type(llm, 
                                            retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
                                            chain_type_kwargs= {"prompt": prompt}
                                            )   
    #---------------------------------------------------#
    if include_prompt and not structured_result:
        template = sysmessage + """
        Context: {context}
        Question: {question}
        """
        
        # Instantiation using initializer
        prompt = PromptTemplate(input_variables=["query","context"],
                                template=template)

        # Set up RetrievalQA with the language model and retriever
        qa_chain = RetrievalQA.from_chain_type(llm, 
                                            retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
                                            chain_type_kwargs= {"prompt": prompt}
                                            )  
    #---------------------------------------------------#
    if not include_prompt and not structured_result:
        # Set up RetrievalQA with the language model and retriever
        qa_chain = RetrievalQA.from_chain_type(llm, 
                                            retriever=vectordb.as_retriever(search_kwargs={"k": 3}))
        
    #---------------------------------------------------#
         
    # Call the _call method
    with get_openai_callback() as cb:
        result = qa_chain({"query": question})        
    
    return result, cb    


# Streamlit app
st.title("Financial GPT")

# Input field for question
question = st.text_input("Enter your question:")
askbutton = st.button("Ask")

def answer_question(question):
    result, cb = qachatbot(question=question,include_prompt=True, structured_result=True)
    result_json_string = result["result"]
    parsed_result = json.loads(result_json_string)
    st.write(parsed_result["answer_"])
    st.write("Related Question 1: " + parsed_result["related_q1"])
    st.write("Related Question 2: " + parsed_result["related_q2"])
    st.write("Related Question 3: " + parsed_result["related_q3"])
    st.write(cb)
    
if askbutton:
    answer_question(question)

