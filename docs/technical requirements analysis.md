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
Pinecone

### 2.2. Data Embedding
#### 2.2.1 PDF parser

#### 2.2.2 Metadata
To increase the accuracy of document search, report metadata should be captured. The metadata should consist of information utilized to differentiate similar content (e.g: industry updates, financial statements), which may vary in context (e.g., 2022 versus 2023). 
The list of metadata includes:
- report type: Types of report (Annual report, Stock analysis report)
- report year: Financial year that the report is talking about?


## 3. Chatbot 
### 3.1. Self-query retriever
Chatbot turns user query into structured query to look for documents inside vector store.

Langchain's sample project: https://github.com/langchain-ai/langchain/blob/master/cookbook/self_query_hotel_search.ipynb

Figure 1. Example process of self-querying
![alt text](https://python.langchain.com/assets/images/self_querying-26ac0fc8692e85bc3cd9b8640509404f.jpg)

Refer to sample_self_querying.ipynb

Example of input: 
How did SWE perform in 2023 compared to the previous year?

Example of output:
- PROMPT QUERY:  SWE profit
- PROMPT FILTER:  comparator=<Comparator.EQ: 'eq'> attribute='reportyear' value=2020
- PROMPT FILTER:  None

### 3.2 Related questions
Prompt to generate related questions:
_"Generate 3 related questions that users might be interested in, based on the context."_

Ideally, the related questions should be presented as clickable buttons. Upon clicking these buttons, the answer box should dynamically update to display the answer corresponding to the selected question.

Figure 2. Buttons for related questions

<img width="377" alt="image" src="https://github.com/tuihoctaichinh/Financial-GPT/assets/159899982/0ef0b272-9994-41ad-a186-baef087fac7a">

## 4. User Interface
