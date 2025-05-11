from typing import List
from openai import AsyncOpenAI
from retry import retry

from src.config import s
from src.models.product import Product

# Create async OpenAI client
openai_client = AsyncOpenAI(api_key=s.openai_api_key)


@retry(tries=3, delay=1)
async def embed_text(text: str) -> List[float]:
    """
    Get the OpenAI embedding for the given text asynchronously.
    """
    response = await openai_client.embeddings.create(
        model=s.openai_embedding_model, input=text
    )
    return response.data[0].embedding


@retry(tries=3, delay=1)
async def embed_product(product: Product) -> List[float]:
    """
    Get the OpenAI embedding for the product asynchronously.
    """
    # Combine product information into a single string
    product_text = Product.get_product_info(product)
    # Get embedding for the combined text
    return await embed_text(product_text)
