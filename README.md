# 🛒 Smart Grocer

**Smart Grocer** is a Streamlit application designed to help you find the lowest prices for your grocery list at nearby Kroger-family stores. Simply enter your zip code and grocery list, and the app will optimize your shopping trip based on your preferred strategy!

<img width="1732" height="1491" alt="smart_grocer_prototypeP1" src="https://github.com/user-attachments/assets/dc75aff1-1f18-40ba-bbfe-e6fe34f269fc" />
<img width="1454" height="680" alt="smart_grocer_prototypeP2" src="https://github.com/user-attachments/assets/ad1f1170-a846-405e-ac5d-932e36f73a40" />

## Features

- **Location-Based Search:** Find stores near your zip code.
- **Two Shopping Strategies:**
  - **Cheapest Overall Cart (One Store):** Finds the single store where your total grocery bill will be the lowest.
  - **Absolute Lowest Prices (Multiple Stores):** Scours multiple nearby stores to find the absolute lowest price for each item, allowing you to split your trip for maximum savings.
- **Optimized Receipt:** View a detailed breakdown of your optimized receipt, including the total estimated cost, items found, store names, and inventory levels.

## Prerequisites

To run this application, you will need a **Kroger Developer API Key**.
1. Visit the [Kroger Developer Portal](https://developer.kroger.com/).
2. Create an account and register a new application.
3. Obtain your `CLIENT_ID` and `CLIENT_SECRET`.

## Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install dependencies:**
   Make sure you have Python installed. You can install the required packages using pip:
   ```bash
   pip install streamlit python-dotenv pandas requests
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory of the project and add your Kroger API credentials:
   ```env
   CLIENT_ID=your_client_id_here
   CLIENT_SECRET=your_client_secret_here
   ```

## How to Run

Start the Streamlit application by running the following command in your terminal:

```bash
streamlit run app.py
```

The application will open in your default web browser (usually at `http://localhost:8501`).

## How to Use

1. Enter your **Zip Code**.
2. Add your **Grocery List** (one item per line, be as specific as possible).
3. Select your preferred **Shopping Strategy**.
4. Click **Optimize My Trip** and wait for the results!
