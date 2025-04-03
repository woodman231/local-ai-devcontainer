from typing import List
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages.tool import ToolMessage

@tool
def validate_user(user_id: int, addresses: List[str]) -> bool:
    """Validate user using historical addresses.

    Args:
        user_id (int): the user ID.
        addresses (List[str]): Previous addresses as a list of strings.
    """

    return True


llm_without_tools = ChatOllama(
    model="llama3.1",
    temperature=0,
    base_url="http://ollama:11434",
)

llm_with_tools = ChatOllama(
    model="llama3.1",
    temperature=0,
    base_url="http://ollama:11434",
).bind_tools([validate_user])

system_message_text = """
You are a helpful assistant. You will either be asked to validate users by id and addresses, or to answer general knowledge questions.
You will be provided with a list of tools to help you answer the questions.
"""

system_message = SystemMessage(content=system_message_text)

messages = [system_message]

query = """
Could you validate user 123? They previously lived at 
123 Fake St in Boston MA and 234 Pretend Boulevard in 
Houston TX.
"""

messages.append(HumanMessage(content=query))

response: AIMessage = llm_with_tools.invoke(
    messages
)

messages.append(response)

# Iterate over the response metadata
for tool_call in response.tool_calls:
    selected_tool = {"validate_user": validate_user}.get(tool_call["name"].lower())
    if selected_tool:
        tool_output = selected_tool.invoke(tool_call["args"])
        messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))

general_knowledge_query = """
Why is the sky blue?
"""

messages.append(HumanMessage(content=general_knowledge_query))
general_knowledge_response: AIMessage = llm_without_tools.invoke(
    messages
)

messages.append(general_knowledge_response)

# Print the final response
for message in messages:
    message.pretty_print()

