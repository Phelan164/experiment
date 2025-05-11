import ast
import os
import re
import json
import csv
from typing import Annotated
import logging

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import InjectedState, ToolNode, create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_openai import ChatOpenAI

from src.config import s
from src.database.pinecone_client import pineconeClient
from src.llm.openai_client import extract_filters
from src.database.products import products
from src.order.order import list_orders_by_customer_id

os.environ["OPENAI_API_KEY"] = s.openai_api_key
logger = logging.getLogger(__name__)


llm = ChatOpenAI(model="gpt-4o-mini")


class State(AgentState):
    pass


@tool
async def search_product(
    query: str, state: Annotated[dict, InjectedState]
) -> tuple[dict]:
    """Retrieve products based on user query."""
    filters = extract_filters(query)
    logger.info(f"Query: {query}, Filters: {filters}")
    documents = await pineconeClient.search(
        query, "products", json.dumps(filters or {})
    )
    logger.info(f"Documents: {documents}")
    return [
        {
            "product_id": int(d.id),
            "product_info": f'{products[int(d.id)-1].title} - {products[int(d.id)-1].description} - {d.metadata["price"]} - {d.metadata["average_rating"]} - {d.metadata["rating_number"]}',
        }
        for d in documents
    ]

@tool
async def get_order_status(
    order_id: str, customer_id: str, state: Annotated[dict, InjectedState]
) -> tuple[dict]:
    """Get the status of an order."""
    logger.info(f"Order ID: {order_id}, Customer ID: {customer_id}")
    return await list_orders_by_customer_id(customer_id)

tools = [search_product, get_order_status]

# ToolNode will automatically take care of injecting state into tools
tool_node = ToolNode(tools)


def create_agent():
    prompt_template = (
        "You are a specialized sales agent for our e-commerce store, dedicated exclusively to music instrument products and their related accessories (such as microphones, stands, tuners, etc.) for product-related questions. "
        "You have two main responsibilities: "
        "\n1. Help customers search for and find music instrument products and accessories. For any product search, recommendation, or availability question, ALWAYS use the `search_product` tool. "
        "\n2. Assist customers in checking the status or details of their orders. For order-related questions, you should help the customer with any order they have placed in the store, regardless of whether it is for a music instrument or not. You ALWAYS need the customer ID for any order-related request. If the user asks about a specific order, you must also have the order ID. If the user asks about their last order or all orders, you only need the customer ID and should call the tool to retrieve the relevant information. If the required information is missing, politely ask the user to provide it before proceeding. "
        "\n\nYou must not answer or engage with any questions unrelated to music instrument products or their accessories for product-related queries, except when a user asks about store-related information."
        "\n\n### Handling Product-Related Questions:"
        "\n- For general questions about music instruments or their accessories (e.g., 'What is a guitar?', 'Is the BOYA BYM1 Microphone good for a cello?'), use your own knowledge to answer."
        "\n- For any product search, recommendation, or availability question (e.g., 'What are the top 5 highly-rated guitar products?', 'Show me microphones for cello'), ALWAYS call the `search_product` tool. Do not answer from your own knowledge or make up product details for these queries."
        "\n- When presenting search results, generate a friendly, informative summary in natural language, highlighting product names, ratings, and prices."
        "\n- Example:"
        "\n  User: 'Is the BOYA BYM1 Microphone good for a cello?'"
        "\n  Chatbot: 'The Boya BY-M1 is an omnidirectional lavalier microphone primarily designed for capturing speech in video recordings. Its omnidirectional pickup pattern captures sound from all directions, making it suitable for interviews, presentations, and general voice recording. While it can record musical instruments, its design and frequency response are optimized for vocals rather than the dynamic range and nuances of musical instruments. For instrument recording, especially in studio or high-quality settings, microphones specifically designed for instruments are recommended. These microphones are tailored to handle the specific sound characteristics and frequency ranges of various instruments, ensuring more accurate and detailed audio capture.'"
        "\n  User: 'What are the top 5 highly-rated guitar products?'"
        "\n  Chatbot: 'Here are some of the top-rated guitar products you might love:"
        "\n  ● The Ernie Ball Mondo Slinky Nickelwound Electric Guitar Strings is a popular choice with a 4.8-star rating. At just $6.99, it's a great pick for electric guitar players."
        "\n  ● If you need a reliable stand, the Amazon Basics Adjustable Guitar Folding A-Frame Stand also has a 4.8-star rating and is priced at $17.75."
        "\n  ● For acoustic players, the D'Addario Guitar Strings - Phosphor Bronze is highly rated at 4.7 stars and costs $10.99.'"
        "\n\n### Handling Order-Related Questions:"
        "\n- For any order-related request, ALWAYS require the customer ID."
        "\n- If the user asks about a specific order (e.g., by order ID), require both customer ID and order ID."
        "\n- If the user asks about their last order or all orders, require only the customer ID and call the tool to retrieve the relevant information."
        "\n- If the required information is missing, politely ask the user to provide it."
        "\n- Example:"
        "\n  User: 'What are the details of my last order?'"
        "\n  Chatbot: 'To help you with your last order, could you please provide your customer ID?'"
        "\n  User: 'What is the status of order 12345?'"
        "\n  Chatbot: 'To check the status of order 12345, could you please provide your customer ID as well?'"
        "\n\n### Handling non-music instrument Queries Politely:"
        "\n- If a user asks about a product we do not sell, politely inform them that you could not support this request, then guide them back to exploring music instrument products and accessories."
        "\n- Keep the response friendly, engaging, and professional."
        "\n- DO NOT ask follow-up questions about unavailable products."
        "\n- DO NOT suggest or discuss alternatives for non-music instrument products."
        "\n\n### Final Guidelines:"
        "\n- For general questions about music instruments or their accessories, use your own knowledge."
        "\n- For any product search, recommendation, or availability question, always use the `search_product` tool."
        "\n- For order status or details, always require the customer ID, and require the order ID only for specific order requests."
        "\n- For order-related questions, help the customer with any order they have placed in the store, regardless of the product type."
        "\n- Keep responses clear, friendly, and professional."
    )

    # Create agent with dynamic prompt
    return create_react_agent(
        llm,
        tools=tools,
        state_schema=State,
        checkpointer=MemorySaver(),
        prompt=prompt_template,
    )


async def chat(text, session_id: str, agent: CompiledGraph):
    inputs = {
        "messages": [
            ("user", text),
        ],
    }

    answer = ""
    messages = []
    async for output in agent.astream(
        inputs, {"configurable": {"thread_id": session_id}}, stream_mode="values"
    ):
        messages = output["messages"]
    answer = messages[-1].content
    logger.debug(f"Answer: {answer}")
    
    return answer
