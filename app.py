import streamlit as st
import os
from dotenv import load_dotenv
from binance.client import Client
from binance.enums import *
import logging

# Load environment variables from .env file
load_dotenv()

# Logging setup
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret)
        if testnet:
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'

    def place_order(self, symbol, side, order_type, quantity, price=None):
        try:
            if order_type == 'MARKET':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity
                )
            elif order_type == 'LIMIT':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == 'BUY' else SIDE_SELL,
                    type=ORDER_TYPE_LIMIT,
                    quantity=quantity,
                    price=price,
                    timeInForce=TIME_IN_FORCE_GTC
                )
            else:
                raise ValueError("Unsupported order type")

            logging.info(f"Order placed: {order}")
            return order

        except Exception as e:
            logging.error(f"Order placement failed: {e}")
            return str(e)

# Streamlit App
st.set_page_config(page_title="Binance Futures Testnet Trading Bot", layout="centered")
st.title("📈 Binance Futures Testnet Trading Bot")

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

if not API_KEY or not API_SECRET:
    st.error("❗ Please set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file.")
else:
    bot = BasicBot(API_KEY, API_SECRET)

    st.header("📊 Place an Order")
    symbol = st.text_input("Trading Pair (e.g., BTCUSDT)").upper()
    side = st.selectbox("Order Side", ["BUY", "SELL"])
    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
    quantity = st.number_input("Quantity", min_value=0.001, step=0.001, format="%.3f")

    price = None
    if order_type == "LIMIT":
        price = st.number_input("Price", min_value=0.001, step=0.001, format="%.3f")

    if st.button("📥 Place Order"):
        with st.spinner("Placing order..."):
            result = bot.place_order(symbol, side, order_type, quantity, price)
            if isinstance(result, dict):
                st.success("✅ Order placed successfully!")
                st.json(result)
            else:
                st.error(f"❌ Order failed: {result}")

st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit")
