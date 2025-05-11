import httpx
from src.config import s

async def list_orders_by_customer_id(customer_id: str):
    """
    List all orders for a given customer ID by calling the order service REST API.
    """
    url = f"{s.order_host}/data/customer/{customer_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def get_all_data():
    url = f"{s.order_host}/data"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def get_customer_data(customer_id: int):
    url = f"{s.order_host}/data/customer/{customer_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def get_product_category_data(category: str):
    url = f"{s.order_host}/data/product-category/{category}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def get_orders_by_priority(priority: str):
    url = f"{s.order_host}/data/order-priority/{priority}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def total_sales_by_category():
    url = f"{s.order_host}/data/total-sales-by-category"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def high_profit_products(min_profit: float = 100.0):
    url = f"{s.order_host}/data/high-profit-products?min_profit={min_profit}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def shipping_cost_summary():
    url = f"{s.order_host}/data/shipping-cost-summary"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def profit_by_gender():
    url = f"{s.order_host}/data/profit-by-gender"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
