import streamlit as st
import os
from dotenv import load_dotenv
import app_utils
import pandas as pd

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# 1. Page Configuration
st.set_page_config(page_title="Smart Grocer", page_icon="🛒", layout="centered")

# 2. Header Section
st.title("🛒 Smart Grocer")
st.markdown("Find the lowest prices for your grocery list at nearby Kroger-family stores.")
st.divider()

# 3. Input Form
with st.form("grocery_form"):
    zip_code = st.text_input("📍 Zip Code", placeholder="e.g. 57104", max_chars=5)
    
    st.markdown("**📝 Your Grocery List**")
    st.caption("Enter one item per line. Be as specific as possible for better results.")
    
    grocery_input = st.text_area(
        "Items", 
        placeholder="Glazed Donuts\nDiet Coke 12 pack\nFrozen Pizza", 
        height=150, 
        label_visibility="collapsed"
    )
    
    # NEW FEATURE: The Strategy Toggle
    st.markdown("**🎯 Shopping Strategy**")
    optimization_type = st.radio(
        "Optimization",
        ["Cheapest Overall Cart (One Store)", "Absolute Lowest Prices (Multiple Stores)"],
        label_visibility="collapsed"
    )
    
    submit_button = st.form_submit_button("Optimize My Trip", type="primary")

# 4. Processing and API Calls
if submit_button:
    if not zip_code or not grocery_input:
        st.warning("Please enter both a zip code and at least one grocery item.")
    else:
        grocery_list = [item.strip() for item in grocery_input.split('\n') if item.strip()]
        
        with st.spinner("Authenticating..."):
            access_token = app_utils.get_kroger_token(CLIENT_ID, CLIENT_SECRET)
        
        if not access_token:
            st.error("Authentication failed. Check your API credentials.")
        else:
            with st.spinner(f"Finding stores near {zip_code}..."):
                stores = app_utils.get_nearby_stores(access_token, zip_code)
                
            if not stores:
                st.error("No stores found in that zip code.")
            else:
                st.success(f"Found {len(stores)} stores! Comparing prices...")
                
                with st.spinner("Scouring aisles for the best deals... this might take a few seconds."):
                    # Route to the correct logic based on user selection
                    if optimization_type == "Cheapest Overall Cart (One Store)":
                        df = app_utils.optimize_single_cart(access_token, stores, grocery_list)
                    else:
                        df = app_utils.create_smart_grocer_list(access_token, stores, grocery_list)
                
                # 5. The Results Dashboard
                st.divider()
                st.subheader("🧾 Your Optimized Receipt")
                
                total_cost = df['product_price'].sum()
                
                col1, col2 = st.columns(2)
                col1.metric("Items Found", len(df))
                col2.metric("Estimated Total", f"${total_cost:.2f}")
                
                display_df = df[['product_name', 'product_price', 'inventory_level', 'store_name', 'store_address']].copy()
                display_df.columns = ['Product', 'Price ($)', 'Stock', 'Store', 'Address']
                
                # FIXED: Swapped use_container_width for width='stretch' to clear the warning
                st.dataframe(display_df, width='stretch', hide_index=True)
