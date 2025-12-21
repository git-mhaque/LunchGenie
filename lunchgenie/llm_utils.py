"""
LLM utility functions for LunchGenie.
Handles OpenAI/LangChain integration.
"""

from lunchgenie.config import Config, ConfigError
from langchain_openai import ChatOpenAI

def test_llm():
    """
    Sanity check for LangChain + OpenAI configuration.
    Runs a 'Hello, LunchGenie!' prompt via ChatOpenAI.
    """
    cfg = Config()
    llm = ChatOpenAI(
        openai_api_key=cfg.openai_api_key,
        model_name="gpt-3.5-turbo",
        temperature=0.2,
    )
    prompt = "Hello, LunchGenie! Reply with 'Hello, world!' if you are working."
    response = llm.invoke(prompt)
    return response.content
