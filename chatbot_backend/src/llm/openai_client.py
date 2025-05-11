import json
import logging
import re

from openai import OpenAI

from src.config import s

logger = logging.getLogger(__name__)


model = OpenAI(api_key=s.openai_api_key)


def clean_json_response(response_text: str) -> str:
    """
    Cleans JSON response by removing triple backticks and unnecessary whitespace.

    Args:
        response_text (str): The raw response from Gemini.

    Returns:
        str: The cleaned JSON string.
    """
    return re.sub(r"^```(json)?|```$", "", response_text.strip()).strip()


def lowercase_dict(d):
    """Helper function to convert string values in a dictionary to lowercase."""
    return {k: v.lower() if isinstance(v, str) else v for k, v in d.items()}


extract_price_rating_prompt = (
    "You are an intelligent assistant that extracts structured filters from a user query for a product search system. "
    "All queries are about music instrument products. "
    "The available filters are: {'price': float, 'rating_number': int, 'average_rating': float}. "
    "Extract only the relevant filters explicitly or implicitly mentioned in the query. "
    "Do not include generic or default values unless explicitly specified or qualified in the query. "
    "Always ensure the output is in a JSON object format, where the keys are the filter names and the values are the extracted data. "
    "For price filters, always use floats and support min, max, or range (e.g., 'under $100' -> {'price': {'max': 100.0}}, 'between $50 and $200' -> {'price': {'min': 50.0, 'max': 200.0}}). "
    "For rating_number filters, always use integers and support min, max, or range (e.g., 'at least 100 reviews' -> {'rating_number': {'min': 100}}, 'less than 50 ratings' -> {'rating_number': {'max': 50}}). "
    "For average_rating filters, always use floats and support min, max, or range (e.g., 'at least 4.5 stars' -> {'average_rating': {'min': 4.5}}, 'less than 3.5 stars' -> {'average_rating': {'max': 3.5}}). "
    "If the query mentions 'highly-rated', map this to average_rating >= 4.5. "
    "If multiple filters are present, include all in the output. "
    "Examples: "
    "- 'Show me guitars under $300 with at least 200 reviews' -> {'price': {'max': 300.0}, 'rating_number': {'min': 200}} "
    "- 'I want something above $50 and below $150 with more than 50 ratings' -> {'price': {'min': 50.0, 'max': 150.0}, 'rating_number': {'min': 51}} "
    "- 'Highly-rated music instrument products under $100' -> {'average_rating': {'min': 4.5}, 'price': {'max': 100.0}} "
    "- 'Products with at least 4.7 stars and under $200' -> {'average_rating': {'min': 4.7}, 'price': {'max': 200.0}} "
    "Output only the JSON object."
)

def extract_filters(query: str) -> dict:
    """
    Extract filters from a user's query based on the given schema using openai.

    Args:
        query (str): The user's input query.
        schema (dict): A dictionary defining the filter schema, where keys are filter names and values are expected data types.

    Returns:
        dict: Extracted filters matching the schema.
    """
    try:
        user_message = f"""
            User Query: "{query}"

            Extract and return only the relevant filters as a JSON object.
            """

        completion = model.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": extract_price_rating_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
        )
        # Call the Gemini model
        cleaned_json = clean_json_response(completion.choices[0].message.content)
        filters = json.loads(cleaned_json)

        return lowercase_dict(filters)

    except Exception as e:
        print(f"Error parsing the response: {e}")
        return {}

if __name__ == "__main__":
    print(extract_filters("I want a highly-rated music instrument under 100 dollars"))
