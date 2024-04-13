import requests
import json
from openai import AzureOpenAI

from langchain_community.callbacks import get_openai_callback
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

def send_completion_request( prompt, tables_with_columns = {}):
    """
    Sends a completion job to the OpenAI API and prints the response.

    Returns:
    str: The original prompt concatenated with the generated response.
    """
    print('Sending a test completion job')

    print(prompt)
    print('TABLES')
    print(dict_to_string(tables_with_columns))

    context_structure = 'Please associate each query you generate with provided database structure ' + dict_to_string(tables_with_columns) +'\n RETURN ONLY PROPER SQL SYNTAX AND NO ADDITIONAL WORDS'

    prompt = context_str + prompt + context_structure 

    message = HumanMessage(
        model='testChatIntegration',
        content=prompt
    )

    with get_openai_callback() as cb:
        full_response = client([message])
        full_response.total_cost = format(cb.total_cost, '.6f')
        print(
        f"Total Cost (USD): ${format(cb.total_cost, '.6f')}"
    )  

    return {
        "content": full_response.content,  # or whatever the attribute for the response text is
        "total_cost": full_response.total_cost
    }
    # return full_response

def dict_to_string(data):
    output = []
    for table, columns in data.items():
        columns_str = ", ".join(columns)  # Join all column names with a comma and a space
        table_info = f"Table: {table}\nColumns: {columns_str}\n"
        output.append(table_info)
    return "\n".join(output)  # Join all table information with a newline


# Example usage
nl_query = "Show me all records from employees where age is greater than 30 AND city is equal to Warsaw"
test_query='What is the color of the sky? Please tell me'

result = send_completion_request(nl_query)
print(result)
