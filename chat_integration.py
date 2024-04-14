import requests
import json
from openai import AzureOpenAI

from langchain.prompts import ChatPromptTemplate
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI

from azure_connection.utils import AzureCredential

credential = AzureCredential()

# Constants
API_KEY = credential.get_secret_value('openai-api-key')
AZURE_ENDPOINT = credential.get_secret_value('openai-endpoint')
max_tokens = 10
client = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=API_KEY,
    api_version="2024-02-01",
    deployment_name='testChatIntegration'
)

def dict_to_string(data):
    output = []
    for table, columns in data.items():
        columns_str = ", ".join(columns)
        table_info = f"Table: {table}, Columns: {columns_str}"
        output.append(table_info)
    return " | ".join(output)  # Using '|' to separate tables for clarity with a newline


def send_completion_request(user_input, tables_with_columns={}):
    chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", f"You are a SQL query developer. Please associate each query you generate with the provided database structure: {dict_to_string(tables_with_columns)}. Check if the field you use is actually in the table. All dates are in ISO8601 format. The answer MUST only contain SQL QUERY. DO NOT SHOW TABLE OR DATABASE NAME IN THE ANSWER OUTSIDE THE SQL QUERY"),

        ("human", user_input),
    ]
)
    print(chat_template)

    with get_openai_callback() as cb:
        full_response = client(chat_template.format_prompt( text=user_input).to_messages())

        print(f"Total Cost (USD): ${format(cb.total_cost, '.6f')}")

    return {
        "content": full_response.content,  # Adjust this based on actual attribute
        "total_cost": format(cb.total_cost, '.6f')
    }

# Example usage
# user_input = "Find all employees who were hired after 2020."
# tables_with_columns = {
#     "employees": ["id", "name", "hire_date"],
#     "departments": ["id", "department_name"]
# }
# response = send_completion_request(user_input, tables_with_columns)
# print(response["content"])





