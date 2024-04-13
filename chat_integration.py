import requests
import json
from openai import AzureOpenAI

from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI

# Constants
API_KEY = "73e54f660d6d4c2aa5b9def3c32cac0c"  # Your API key
AZURE_ENDPOINT = "https://chatintegration.openai.azure.com/"  # Azure endpoint
max_tokens = 10
client = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=API_KEY,
    api_version="2024-02-01",
    deployment_name='testChatIntegration'
)

context_str = 'You are a SQL query developer. Please create a proper SQL query for the description as given below:\n'

def send_completion_request( prompt):
    """
    Sends a completion job to the OpenAI API and prints the response.

    Returns:
    str: The original prompt concatenated with the generated response.
    """
    print('Sending a test completion job')

    print(prompt)

    prompt = context_str + prompt

    # response = client.completions.create(model='testChatIntegration',  prompt=prompt, temperature=0.1, top_p=1)
    # full_response = prompt + response.choices[0].text
    # print(full_response)
    message = HumanMessage(
        model='testChatIntegration',
        content=prompt
    )
    full_response = client([message])
    return full_response


def sql_to_json(sql_query):
    # Assuming SQL query is "SELECT * FROM table WHERE condition"
    # Simplistic parser for demonstration purposes
    parts = sql_query.split()
    json_query = {
        "action": parts[0],
        "columns": parts[1],
        "table": parts[3],
        "condition": " ".join(parts[5:])
    }
    print(json_query)
    return json_query

def get_sql_query_in_json(nl_query):
    sql_query = azure_openai_request(nl_query)
    json_query = sql_to_json(sql_query)
    return json_query

# Example usage
nl_query = "Show me all records from employees where age is greater than 30"
test_query='What is the color of the sky? Please tell me'

result = send_completion_request(nl_query)
print(result)
