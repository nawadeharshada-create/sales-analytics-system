#---------------------------- Part 3:API Integration -----------------------------#

import os
import re
import requests


BASE_URL = "https://dummyjson.com/products"

#-------------------------- Task 3.1: Fetch Product Details ---------------------#

#-- a) Fetch All Products
def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Requirements:
    - Fetch all available products (use limit=100)
    - Handle connection errors with try-except
    - Return empty list if API fails
    - Print status message (success/failure)
    """
    url = f"{BASE_URL}?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get("products", [])

        print(f" Fetched {len(products)} products from API")
        return products

    except requests.exceptions.RequestException as e:
        print(f" API Error: Unable to fetch products ({e})")
        return []
    except ValueError:
        print(" API Error: Invalid JSON response")
        return []
    except Exception as e:
        print(f" Unexpected Error in fetch_all_products: {e}")
        return []


#--- b)Create Product Mapping
def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Expected Output Format:
    {
        1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
        ...
    }
    """
    mapping = {}

    try:
        for p in api_products:
            pid = p.get("id")

            if isinstance(pid, int):
                mapping[pid] = {
                    "title": p.get("title"),
                    "category": p.get("category"),
                    "brand": p.get("brand"),
                    "rating": p.get("rating"),
                }

        print(f" Created product mapping for {len(mapping)} products")
        return mapping

    except Exception as e:
        print(f" Error creating product mapping: {e}")
        return {}


def _extract_numeric_product_id(product_id_str):
    """
    Extract numeric ID from ProductID like:
    P101 -> 101
    P5   -> 5
    """
    if not product_id_str:
        return None

    match = re.search(r"\d+", str(product_id_str))
    if not match:
        return None

    try:
        return int(match.group())
    except ValueError:
        return None

#-------------------------- Task 3.1: Fetch Product Details ---------------------#

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information

    Adds:
    - API_Category
    - API_Brand
    - API_Rating
    - API_Match (True/False)

    Note: This returns enriched list. Saving is handled by save_enriched_data().
    """
    enriched = []

    try:
        for t in transactions:
        
            row = dict(t)

            numeric_id = _extract_numeric_product_id(row.get("ProductID"))
            api_info = product_mapping.get(numeric_id)

            if api_info:
                row["API_Category"] = api_info.get("category")
                row["API_Brand"] = api_info.get("brand")
                row["API_Rating"] = api_info.get("rating")
                row["API_Match"] = True
            else:
                row["API_Category"] = None
                row["API_Brand"] = None
                row["API_Rating"] = None
                row["API_Match"] = False

            enriched.append(row)

        print(f"Enriched {len(enriched)} transactions with API info")
        return enriched

    except Exception as e:
        print(f" Error enriching sales data: {e}")
       
        return enriched


def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file

    Requirements:
    - Create output file with all original + new fields
    - Use pipe delimiter
    - Handle None values appropriately
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        headers = [
            "TransactionID",
            "Date",
            "ProductID",
            "ProductName",
            "Quantity",
            "UnitPrice",
            "CustomerID",
            "Region",
            "API_Category",
            "API_Brand",
            "API_Rating",
            "API_Match",
        ]

        with open(filename, "w", encoding="utf-8") as f:
            f.write("|".join(headers) + "\n")

            for row in enriched_transactions:
                values = []
                for h in headers:
                    v = row.get(h)

                    # None handling -> write empty
                    if v is None:
                        values.append("")
                    else:
                        values.append(str(v))

                f.write("|".join(values) + "\n")

        print(f" Saved enriched data to: {filename}")

    except Exception as e:
        print(f" Error saving enriched data: {e}")
