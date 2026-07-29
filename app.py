import os
import psycopg2
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(os.environ["NEON_DATABASE_URL"])


def run_query(query, params=None):
    with get_connection() as conn:
        return pd.read_sql(query, conn, params=params)


def run_write(query, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()


st.set_page_config(page_title="AgriConnect", layout="wide")
st.title("AgriConnect — Farmer-Buyer Marketplace")

page = st.sidebar.radio(
    "Go to",
    ["Add Farmer", "Add Buyer", "Add Listing", "Place Order", "Active Listings", "Reports"],
)

if page == "Add Farmer":
    st.header("Register a Farmer")
    with st.form("farmer_form"):
        name = st.text_input("Name")
        village = st.text_input("Village")
        contact = st.text_input("Contact")
        crop = st.text_input("Primary crop")
        if st.form_submit_button("Add Farmer"):
            run_write(
                "INSERT INTO farmers (name, village, contact, primary_crop) VALUES (%s, %s, %s, %s)",
                (name, village, contact, crop),
            )
            st.success(f"Added farmer {name}")

elif page == "Add Buyer":
    st.header("Register a Buyer")
    with st.form("buyer_form"):
        name = st.text_input("Name")
        buyer_type = st.selectbox("Type", ["retailer", "wholesaler", "consumer"])
        location = st.text_input("Location")
        contact = st.text_input("Contact")
        if st.form_submit_button("Add Buyer"):
            run_write(
                "INSERT INTO buyers (name, buyer_type, location, contact) VALUES (%s, %s, %s, %s)",
                (name, buyer_type, location, contact),
            )
            st.success(f"Added buyer {name}")

elif page == "Add Listing":
    st.header("List Produce")
    farmers = run_query("SELECT farmer_id, name FROM farmers ORDER BY name")
    if farmers.empty:
        st.warning("Add a farmer first.")
    else:
        with st.form("listing_form"):
            farmer = st.selectbox("Farmer", farmers["name"])
            farmer_id = int(farmers.loc[farmers["name"] == farmer, "farmer_id"].iloc[0])
            crop_name = st.text_input("Crop")
            quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
            unit = st.text_input("Unit", value="kg")
            price = st.number_input("Price per unit", min_value=0.0, step=1.0)
            harvest_date = st.date_input("Harvest date")
            if st.form_submit_button("Add Listing"):
                run_write(
                    """INSERT INTO listings (farmer_id, crop_name, quantity, unit, price_per_unit, harvest_date)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (farmer_id, crop_name, quantity, unit, price, harvest_date),
                )
                st.success(f"Listed {crop_name} for {farmer}")

elif page == "Place Order":
    st.header("Place an Order")
    buyers = run_query("SELECT buyer_id, name FROM buyers ORDER BY name")
    listings = run_query(
        """SELECT l.listing_id, f.name AS farmer_name, l.crop_name, l.quantity, l.price_per_unit
           FROM listings l JOIN farmers f ON l.farmer_id = f.farmer_id
           WHERE l.status = 'available'"""
    )
    if buyers.empty or listings.empty:
        st.warning("Need at least one buyer and one available listing.")
    else:
        listings["label"] = (
            listings["farmer_name"] + " — " + listings["crop_name"]
            + " (" + listings["quantity"].astype(str) + " available)"
        )
        with st.form("order_form"):
            buyer = st.selectbox("Buyer", buyers["name"])
            buyer_id = int(buyers.loc[buyers["name"] == buyer, "buyer_id"].iloc[0])
            listing_label = st.selectbox("Listing", listings["label"])
            listing_row = listings.loc[listings["label"] == listing_label].iloc[0]
            listing_id = int(listing_row["listing_id"])
            qty = st.number_input(
                "Quantity to order",
                min_value=0.0,
                max_value=float(listing_row["quantity"]),
                step=1.0,
            )
            if st.form_submit_button("Place Order"):
                run_write(
                    "INSERT INTO orders (buyer_id, listing_id, quantity_ordered) VALUES (%s, %s, %s)",
                    (buyer_id, listing_id, qty),
                )
                st.success("Order placed — listing quantity updated automatically by the trigger.")

elif page == "Active Listings":
    st.header("Active Listings")
    st.dataframe(run_query("SELECT * FROM active_listings_view ORDER BY harvest_date"))

elif page == "Reports":
    st.header("Reports")
    report = st.selectbox(
        "Choose a report",
        [
            "Revenue per farmer",
            "Most active buyers",
            "Price trend",
            "Unsold stock (15+ days)",
            "Average farmer rating",
            "Pending payments",
        ],
    )

    if report == "Revenue per farmer":
        farmers = run_query("SELECT farmer_id, name FROM farmers ORDER BY name")
        farmer = st.selectbox("Farmer", farmers["name"])
        farmer_id = int(farmers.loc[farmers["name"] == farmer, "farmer_id"].iloc[0])
        st.dataframe(run_query("SELECT * FROM get_farmer_revenue(%s)", (farmer_id,)))

    elif report == "Most active buyers":
        st.dataframe(run_query(
            """SELECT b.name, COUNT(o.order_id) AS total_orders, SUM(o.quantity_ordered) AS total_volume
               FROM buyers b JOIN orders o ON b.buyer_id = o.buyer_id
               GROUP BY b.name ORDER BY total_volume DESC"""
        ))

    elif report == "Price trend":
        crop = st.text_input("Crop name", value="Rubber Sheet")
        st.dataframe(run_query(
            "SELECT crop_name, record_date, avg_market_price FROM price_history WHERE crop_name = %s ORDER BY record_date",
            (crop,),
        ))

    elif report == "Unsold stock (15+ days)":
        st.dataframe(run_query(
            """SELECT f.name, l.crop_name, l.quantity, l.harvest_date
               FROM listings l JOIN farmers f ON l.farmer_id = f.farmer_id
               WHERE l.status = 'available' AND l.harvest_date < CURRENT_DATE - INTERVAL '15 days'"""
        ))

    elif report == "Average farmer rating":
        st.dataframe(run_query(
            """SELECT f.name, AVG(r.score) AS avg_rating, COUNT(r.rating_id) AS num_ratings
               FROM farmers f
               JOIN listings l ON f.farmer_id = l.farmer_id
               JOIN orders o ON l.listing_id = o.listing_id
               JOIN ratings r ON o.order_id = r.order_id
               GROUP BY f.name ORDER BY avg_rating DESC"""
        ))

    elif report == "Pending payments":
        st.dataframe(run_query(
            """SELECT o.order_id, b.name AS buyer, p.amount, p.status
               FROM orders o JOIN buyers b ON o.buyer_id = b.buyer_id
               JOIN payments p ON o.order_id = p.order_id
               WHERE p.status = 'pending'"""
        ))
