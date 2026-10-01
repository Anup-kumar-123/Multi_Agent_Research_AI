import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import scrape_url, web_query

load_dotenv()

# Initialize LLM
LLM = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# Building the Search Agent
def build_search_agent():
    return create_agent(
        model=LLM,
        tools=[web_query]
    )

# Building the Reader Agent
def build_reader_agent():
    return create_agent(
        model=LLM,
        tools=[scrape_url]
    )

# Writer Chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer, write clearly, structured and insightful responses for the user"),
    ("human", """Write a detailed research report on the topic below.

Topic : {topic}

Research Gathered: 
{research}

Structure the report as :
-Introduction.
-Key findings (minimum 3 well explained points)
-Conclusion
-Sources (List all the URLs found on the research)
    
Be detailed factual and professional""")
])

writer_chain = writer_prompt | LLM | StrOutputParser()

# Critic Chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly
    
Report: 
{report}

Respond in this exact format:

Score : X/10

Strengths:
- . . .
- . . . 

Area of improvements:
- . . .
- . . .

One line verdict 
...""")
])

critic_chain = critic_prompt | LLM | StrOutputParser()
