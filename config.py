from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI

_ = load_dotenv(find_dotenv())
llm = ChatOpenAI(
    model="Qwen/Qwen2-72B-Instruct-AWQ"
)