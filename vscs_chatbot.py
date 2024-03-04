import tkinter as tk
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os

def ask_question():
    question = question_entry.get()
    result = qa_chain({"query": question})
    result_label.config(text="Answer: " + result["result"])

def close_window():
    root.destroy()

# Initialize OpenAI embeddings
openai.api_key  = os.environ['OPENAI_API_KEY']
embedding = OpenAIEmbeddings()

# Specify the directory for persistent storage
persist_directory = 'docs/chroma/financialgpt'

# Initialize Chroma with embeddings and directory
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)

# Initialize ChatOpenAI with temperature set to 0
llm = ChatOpenAI(temperature=0)

# Set up RetrievalQA with the language model and retriever
qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectordb.as_retriever(search_kwargs={"k": 3}))

# Create the main window
root = tk.Tk()
root.title("Question Answering System")

# Create a label and entry for inputting questions
question_label = tk.Label(root, text="Enter your question:")
question_label.pack()
question_entry = tk.Entry(root, width=50)
question_entry.pack()

# Create a button to ask the question
ask_button = tk.Button(root, text="Ask", command=ask_question)
ask_button.pack()

# Create a label to display the result with a larger text box
result_label = tk.Label(root, text="", wraplength=700, justify="left", height=15)
result_label.pack()

# Create a button to close the window
close_button = tk.Button(root, text="Close", command=close_window)
close_button.pack()

root.mainloop()
