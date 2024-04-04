# Technical Requirements 

## Product Building blocks:  

1. Raw Data (financial statements + company profile + securities reports) 
2. Database (RDBMS + vector database) 
3. Visualization (code) 
4. Chatbot (initial prompt + related questions)  
5. User interface (host + domain) 
6. Evaluation framework for chatbot

## 1. Raw Data

## 2. Database 
### 2.1. Choice of vector database

### 2.2. Data Embedding
To increase the accuracy of document search, report metadata should be captured. The list of metadata includes:
- report type: Types of report (Annual report, Stock analysis report)
- report year: Financial year that the report is talking about?

## 3. Chatbot 
### 3.1. Self-query retriever
Chatbot turns user query into structured query to look for documents inside vector store.

Figure 1. Example process of self-querying
![alt text](https://python.langchain.com/assets/images/self_querying-26ac0fc8692e85bc3cd9b8640509404f.jpg)

Refer to sample_self_querying.ipynb

Example of input: 
How did SWE perform in 2023 compared to the previous year?

Example of output:
PROMPT QUERY:  SWE profit
PROMPT FILTER:  comparator=<Comparator.EQ: 'eq'> attribute='reportyear' value=2020
PROMPT FILTER:  None

## 3. Chatbot 
