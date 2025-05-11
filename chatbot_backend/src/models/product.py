from pydantic import BaseModel
from typing import List, Optional
import ast

class Product(BaseModel):
    main_category: str
    title: str
    average_rating: Optional[float]
    rating_number: Optional[int]
    features: Optional[List[str]]
    description: str
    price: float
    store: str
    categories: Optional[List[str]]
    details: Optional[dict]
    parent_asin: str


    @classmethod
    def from_csv_row(cls, row: List[str], headers: List[str]) -> 'Product':
        """
        Create a Product instance from a CSV row
        
        Args:
            row: List of values from CSV row
            headers: List of column headers from CSV
        
        Returns:
            Product instance
        """
        # Create a dictionary mapping headers to values
        data = dict(zip(headers, row))
        
        def safe_float(value: str) -> Optional[float]:
            if not value or value.lower() == 'none':
                return None
            try:
                return float(value)
            except ValueError:
                return None

        def safe_int(value: str) -> Optional[int]:
            if not value or value.lower() == 'none':
                return None
            try:
                return int(value)
            except ValueError:
                return None

        def safe_eval_list(value: str) -> Optional[List[str]]:
            if not value or value.lower() == 'none':
                return None
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return None

        def safe_eval_dict(value: str) -> Optional[dict]:
            if not value or value.lower() == 'none':
                return {}
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return {}

        product_data = {
            'main_category': data.get('main_category', ''),
            'title': data.get('title', ''),
            'average_rating': safe_float(data.get('average_rating')),
            'rating_number': safe_int(data.get('rating_number')),
            'features': safe_eval_list(data.get('features')),
            'description': data.get('description', ''),
            'price': safe_float(data.get('price')) or 0.0,  # Default to 0.0 if None
            'store': data.get('store', ''),
            'categories': safe_eval_list(data.get('categories')),
            'details': safe_eval_dict(data.get('details')),
            'parent_asin': data.get('parent_asin', '')
        }
        
        return cls(**product_data)
    

    def get_product_info(self) -> str:
        return f"Title: {self.title}\nDescription: {self.description}\nPrice: {self.price}\nStore: {self.store}\nCategories: {self.categories}\nDetails: {self.details}\nParent ASIN: {self.parent_asin}"