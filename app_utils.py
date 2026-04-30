import requests
import json
import time
import os
import pandas as pd

TOKEN_FILE = "token_cache.json"

def get_kroger_token(client_id, client_secret):
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            try:
                cache = json.load(f)
                if time.time() < (cache.get("expires_at", 0) - 60):
                    return cache.get("access_token")
            except json.JSONDecodeError:
                pass

    url = "https://api.kroger.com/v1/connect/oauth2/token"
    
    payload = {
        "grant_type": "client_credentials",
        "scope": "product.compact"
    }
    
    response = requests.post(url, data=payload, auth=(client_id, client_secret))
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 1800) 
        expiration_timestamp = time.time() + expires_in
        
        cache_data = {
            "access_token": access_token,
            "expires_at": expiration_timestamp
        }
        
        with open(TOKEN_FILE, "w") as f:
            json.dump(cache_data, f)
            
        return access_token
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
    
def get_nearby_stores(access_token, zip_code):
    url = f"https://api.kroger.com/v1/locations?filter.zipCode.near={zip_code}"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        stores = response.json().get("data", [])
        # Terminal print spam removed here
        return stores
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def find_product_price(access_token, location_id, term):
    url = f"https://api.kroger.com/v1/products?filter.locationId={location_id}&filter.term={term}"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
        }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        products = response.json().get("data", [])
        # Terminal print spam removed here
        
        lowest_price = float('inf')
        best_product = None
        
        for product in products:
            items = product.get("items", [])
            
            if not items:
                continue
                
            item_data = items[0] 
            price_data = item_data.get("price", {})
            price = price_data.get("promo") or price_data.get("regular")
            
            if price is None:
                continue

            if price <= lowest_price:
                lowest_price = price
                best_product = product
                best_item_data = item_data 
            
        if best_product is None:
            return None
            
        key_product_info = {
            "product_name": best_product.get("description"),
            "product_price": lowest_price,
            "inventory_level": best_item_data.get("inventory", {}).get("stockLevel", "UNKNOWN")
        }
        
        return key_product_info

    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Strategy 1: Find absolute lowest prices regardless of store
def find_lowest_price(access_token, stores, term):
    lowest_price = float('inf')
    best_product = None

    for store in stores:
        location_id = store.get("locationId")
        product = find_product_price(access_token, location_id, term)

        if product is None:
            continue

        if product["product_price"] <= lowest_price:
            lowest_price = product["product_price"]
            best_product = product
            best_product["location_id"] = location_id
            best_product["store_name"] = store.get("name")
            best_product["store_address"] = store.get("address", {}).get("addressLine1", "Unknown Address")
            
        time.sleep(0.5) 
        
    if best_product is None:
        return {
            "product_name": f"{term} (Not Found)",
            "product_price": 0.0,
            "inventory_level": "OUT OF STOCK",
            "location_id": "N/A",
            "store_name": "No nearby stores",
            "store_address": "N/A"
        }

    return best_product

def create_smart_grocer_list(access_token, stores, grocery_list):
    found_items = []
    for item in grocery_list:
        found_items.append(find_lowest_price(access_token, stores, item))

    return pd.DataFrame(found_items)

# Strategy 2: NEW FEATURE - Find the cheapest overall cart at a single store
def optimize_single_cart(access_token, stores, grocery_list):
    best_store_receipt = []
    lowest_cart_total = float('inf')

    for store in stores:
        location_id = store.get("locationId")
        current_store_receipt = []
        current_cart_total = 0.0

        for term in grocery_list:
            product = find_product_price(access_token, location_id, term)
            time.sleep(0.5) # API Throttle to prevent 503 errors

            if product:
                # Add the specific store details to the dictionary
                product["location_id"] = location_id
                product["store_name"] = store.get("name")
                product["store_address"] = store.get("address", {}).get("addressLine1", "Unknown Address")
                
                current_store_receipt.append(product)
                current_cart_total += product["product_price"]
            else:
                # Handle out of stock items gracefully
                current_store_receipt.append({
                    "product_name": f"{term} (Not Found)",
                    "product_price": 0.0,
                    "inventory_level": "OUT OF STOCK",
                    "location_id": location_id,
                    "store_name": store.get("name"),
                    "store_address": store.get("address", {}).get("addressLine1", "Unknown Address")
                })
        
        # After checking every item at this specific store, see if it is the cheapest cart so far
        if current_cart_total < lowest_cart_total:
            lowest_cart_total = current_cart_total
            best_store_receipt = current_store_receipt

    return pd.DataFrame(best_store_receipt)
