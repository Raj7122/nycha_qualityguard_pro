"""
Test script to verify smolagents and CodeAgent import and initialization.
"""

from smolagents import CodeAgent

if __name__ == "__main__":
    try:
        agent = CodeAgent(model="gemini-pro", api_key="dummy", tools=[], temperature=0.7)
        print("smolagents and CodeAgent imported and initialized successfully.")
    except Exception as e:
        print(f"Error initializing CodeAgent: {e}") 