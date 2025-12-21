"""
Command-line interface for LunchGenie.
"""

from lunchgenie.agent import recommend_lunch_places
from lunchgenie.llm_utils import test_llm
from lunchgenie.config import ConfigError
from lunchgenie.result_formatter import print_recommendations

def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "recommend":
        recommendations = recommend_lunch_places()
        print_recommendations(recommendations)
    else:
        try:
            print("Testing LangChain + OpenAI integration...")
            result = test_llm()
            print(f"LLM Response: {result}")
        except ConfigError as ce:
            print(f"Configuration error: {ce}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
