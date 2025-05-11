import csv
import os
from src.models.product import Product
from src.llm.embedding import embed_product
from tqdm import tqdm
from src.database.pipecone_client import pineconeClient


def read_products_from_csv(file_path: str) -> list[Product]:
    products = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Get the header row
        for row in reader:
            try:
                product = Product.from_csv_row(row, headers)
                products.append(product)
            except Exception as e:
                print(f"Error processing row: {row}")
                print(f"Error: {str(e)}")
                continue
    return products

# TODO: multiple process
async def embed_products(products: list[Product]):
    embedded_products = []
    for idx, product in tqdm(enumerate(products)):
        embedding = await embed_product(product)
        embedded_products.append({
            "id": idx+1,
            "embedded_vector": embedding,
            "metadata": {
                "price": product.price,
                "average_rating": product.average_rating,
                "rating_number": product.rating_number,
            }
        })

    return embedded_products


async def main():
    products = read_products_from_csv(os.path.join(os.path.dirname(__file__), "Product_Information_Dataset.csv"))
    products = await embed_products(products)
    pineconeClient.upsert_products(products, "products")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
