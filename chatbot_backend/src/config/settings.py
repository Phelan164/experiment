import logging
from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

logging.basicConfig(format="%(levelname)s %(name)s  %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    project_dir: Path = Path(__file__).resolve().parents[2]
    # host
    host: str = "https://api.aailabbot.com"
    order_host: str = "https://api.order.aailabbot.com"

    # openai config
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_size: int = 1536  # size of model "text-embedding-3-small"

    # pinecone config
    pinecone_api_key: str = ""  # api key for pinecone

    all_cors_origins: list[str] = []

    model_config = ConfigDict(
        case_sensitive=False,
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="allow",
    )
