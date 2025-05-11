import logging
import re
import time
import json
from async_lru import alru_cache
from funcy import log_durations
from langchain_core.documents import Document
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone
from retry import retry

from src.config import s
from src.llm.embedding import embed_text


logging.basicConfig(format="%(levelname)s %(name)s  %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def build_filter(filters: dict) -> dict:
    """
    Convert the filters dictionary into a Pinecone-compatible query filter.
    Supports price, rating_number, and average_rating with min/max or equality.
    """
    pinecone_filter = {}

    for key, value in filters.items():
        if key in {"price", "rating_number", "average_rating"} and isinstance(value, dict):
            # Handle min/max for numeric fields using the original key
            range_ops = {}
            if "min" in value and value["min"] is not None:
                range_ops["$gte"] = value["min"]
            if "max" in value and value["max"] is not None:
                range_ops["$lte"] = value["max"]
            if range_ops:
                pinecone_filter[key] = range_ops
        elif isinstance(value, dict):
            # Handle other dict-based filters (e.g., $ne, $in, $nin)
            if "$ne" in value and value["$ne"] is not None:
                pinecone_filter[key] = {"$ne": value["$ne"]}
            if "$in" in value and isinstance(value["$in"], list) and value["$in"]:
                pinecone_filter[key] = {"$in": value["$in"]}
            if "$nin" in value and isinstance(value["$nin"], list) and value["$nin"]:
                pinecone_filter[key] = {"$nin": value["$nin"]}
        elif isinstance(value, str):
            if value.lower().startswith("not "):
                excluded_value = value[4:].strip()
                pinecone_filter[key] = {"$ne": excluded_value}
            else:
                pinecone_filter[key] = {"$eq": value}
        elif isinstance(value, list) and value:
            pinecone_filter[key] = {"$in": value}
        elif value is not None:
            pinecone_filter[key] = {"$eq": value}

    return pinecone_filter


class PineconeClient:
    def __init__(self, api_key: str):
        self.pinecone = Pinecone(api_key=api_key)
        self.index = self.pinecone.Index("music-instruments")


    def create_index(self, index_name: str):
        """Create index if it doesn't exist."""
        if not self.pinecone.has_index(index_name):
            self.pinecone.create_index(
                name=index_name,
                dimension=s.openai_embedding_size,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            # Wait for index to be ready
            while not self.pinecone.describe_index(index_name).status["ready"]:
                time.sleep(1)

    def upsert_products(self, products: list[dict], namespace: str):
        batch_size = 128  # TODO: experiment with different batch size

        records = []
        for product in products:
            embdded_vector = product["embedded_vector"]
            records.append(
                {
                    "id": str(product["id"]),
                    "values": embdded_vector,
                    "metadata": product["metadata"],
                }
            )
            if len(records) == batch_size:
                self.index.upsert(vectors=records, namespace=namespace)
                records = []
        if records:
            self.index.upsert(vectors=records, namespace=namespace)
            
    @retry(tries=3, delay=1)
    async def _pinecone_query(self, query: str, filters: dict, namespace: str):
        embedded_vector = await embed_text(query)

        pinecone_filter = build_filter(filters)
        logger.info(f"Pinecone build_filter {filters} to {pinecone_filter}")
        try:
            results = self.index.query(
                namespace=namespace,
                vector=embedded_vector,
                filter=pinecone_filter,
                top_k=10,
                include_values=False,
                include_metadata=True,
            )
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")

        if not results or not results["matches"]:  # query without filters
            logger.debug(f"_pinecone_query Pinecone query without filters")
            results = self.index.query(
                namespace=namespace,
                vector=embedded_vector,
                filter={},
                top_k=10,
                include_values=False,
                include_metadata=True,
            )
        return results

    @log_durations(logging.info)
    @alru_cache(maxsize=1000)
    async def search(self, query: str, namespace: str, filters: str):
        if not query:
            return []

        if not filters:
            filters = {}
        else:
            filters = json.loads(filters)

        logger.info(f"Pinecone search {query} {filters} {namespace}")
        results = await self._pinecone_query(query, filters, namespace)
        docs = []
        for match in results["matches"]:
            docs.append(
                Document(
                    id=match["id"],
                    metadata=match["metadata"],
                    page_content="",
                )
            )
        return docs


# Create the client instance
pineconeClient = PineconeClient(api_key=s.pinecone_api_key)
