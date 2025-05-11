import csv
import os
from src.models.product import Product

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

products = read_products_from_csv(os.path.join(os.path.dirname(__file__), "Product_Information_Dataset.csv"))