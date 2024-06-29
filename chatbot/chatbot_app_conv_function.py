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
from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationEntityMemory
from langchain import OpenAI
from langchain.chains import ConversationChain
import json 

# Specify the directory for persistent storage
persist_directory = os.path.dirname(os.getcwd()) + '\\data\\chroma\\vietcap_reports'
embedding = OpenAIEmbeddings()
# Initialize Chroma with embeddings and directory
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)


# Initialize OpenAI embeddings
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize ChatOpenAI with temperature set to 0
llm = ChatOpenAI(temperature=0,
                    model = 'gpt-3.5-turbo'
                    #streaming=True
                    )

class Answer(BaseModel):
    answer_: str = Field(description="answer of the user's query")
    related_q1: str = Field(description="related question no.1")
    related_q2: str = Field(description="related question no.2")
    related_q3: str = Field(description="related question no.3")

parser = JsonOutputParser(pydantic_object=Answer)

TEMPLATE= """
You are a company information extractor and also an expert in Financial investment.
You will receive question from users, there are steps that you will follow to answer the questions:
Important instruction 1: Answer I don't know if the information is not in the context.
Important instruction 2: Answer the question in a structured format with numbers for evidence.
First step (think, don't write): you separate the question into 2 or 3 sub-questions 
Second step (think, don't write): Give detailed answers with numbers for evidence for each sub-question in a 2-level structure, level 1 has 3 headings in numbered list, each heading in level 1 then is explained in 3 bullet points. 
Third step (now write): you show level 1 headings, then you show level 1 headings + their bullet points.
Finally generate 3 related questions that users might be interested in.
If the question is not in the context, look for the context in vector database
.\n\nContext:\n{entities}\n\nCurrent conversation:\n{history}\nLast line:\nHuman: {input}\nYou:
"""
# Set up a parser + inject instructions into the prompt template.
#parser = JsonOutputParser(pydantic_object=Answer)
format_instructions= parser.get_format_instructions()
PROMPT = PromptTemplate(
            input_variables=['entities', 'history', 'input'],
            partial_variables={'format_instructions': parser.get_format_instructions()},
                               template=TEMPLATE)

#memory2 = ConversationEntityMemory(retriever=vectordb.as_retriever(search_kwargs={"k": 3}))

conversation_entitymemory = ConversationChain( 
    llm=llm,  
    verbose=True,
    prompt=PROMPT,
    memory=ConversationEntityMemory(llm=llm))

conversation_entitymemory = ConversationChain( 
    llm=llm,  
    verbose=True,
    prompt=PROMPT,
    memory=ConversationBufferMemory(llm=llm))

def chatbot_conv_entitymemory(question):
    response = conversation_entitymemory({"input": question})
    # If you want to treat the 'response' string as JSON, you need to convert it to a valid JSON format
    response_str = response['response']

    # Extract the related questions using regex or splitting the text
    related_questions_start = response_str.find("Related questions:")
    related_questions_text = response_str[related_questions_start:].strip()

    # Splitting the related questions section to extract each question
    related_questions_list = related_questions_text.split('\n')[1:]  # Skip the "Related questions:" line
    related_questions = {f"related_q{i+1}": question.strip() for i, question in enumerate(related_questions_list)}
    # Extract the main content without the "Related questions" part
    if related_questions_start != -1:
        answer = response_str[:related_questions_start].strip()
    else:
        answer = response_str.strip()

    related_q1 = related_questions.get("related_q1")
    related_q2 = related_questions.get("related_q2")
    related_q3 = related_questions.get("related_q3")

    return answer, related_q1, related_q2, related_q3

