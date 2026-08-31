import os
import psycopg2
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# DATABASE
# ============================================================

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


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AgriConnect",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM UI STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */
    .main {
        background-color: #FFFFFF;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F1F8F3;
        border-right: 1px solid #DDEBDD;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #2E7D32;
    }

    /* Main headings */
    h1 {
        color: #1B5E20;
        font-weight: 700;
    }

    h2 {
        color: #2E7D32;
        font-weight: 650;
    }

    h3 {
        color: #388E3C;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #2E7D32;
        background-color: #2E7D32;
        color: white;
        font-weight: 600;
        padding: 0.55rem 1.2rem;
    }

    .stButton > button:hover {
        background-color: #1B5E20;
        border-color: #1B5E20;
        color: white;
    }

    /* Form container */
    div[data-testid="stForm"] {
        border: 1px solid #DDEBDD;
        border-radius: 12px;
        padding: 25px;
        background-color: #FFFFFF;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    /* Inputs */
    input, textarea {
        border-radius: 7px !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #F1F8F3;
        border: 1px solid #DDEBDD;
        padding: 15px;
        border-radius: 10px;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Home hero */
    .hero {
        padding: 40px;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #E8F5E9,
            #F7FCF8
        );
        border: 1px solid #DDEBDD;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 750;
        color: #1B5E20;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 19px;
        color: #4A4A4A;
        max-width: 800px;
        line-height: 1.6;
    }

    .feature-card {
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #DDEBDD;
        background-color: #FFFFFF;
        min-height: 150px;
    }

    .feature-icon {
        font-size: 30px;
    }

    .feature-title {
        font-size: 19px;
        font-weight: 650;
        color: #2E7D32;
        margin-top: 8px;
    }

    .feature-text {
        color: #555555;
        line-height: 1.5;
        margin-top: 5px;
    }

    .section-label {
        color: #2E7D32;
        font-size: 15px;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="padding: 10px 0 20px 0;">
            <div style="font-size: 34px;">🌱</div>
            <h2 style="margin: 0;">AgriConnect</h2>
            <p style="color: #666; margin-top: 5px;">
                Farmer-Buyer Marketplace
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Navigation")

    page = st.radio(
        "Go to",
        [
            "Home",
            "Add Farmer",
            "Add Buyer",
            "Add Listing",
            "Place Order",
            "Active Listings",
            "Reports",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.caption("AgriConnect")
    st.caption("Connecting farmers with buyers 🌾")


# ============================================================
# HOME
# ============================================================

if page == "Home":

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                🌱 Welcome to AgriConnect
            </div>

            <div class="hero-subtitle">
                A simple digital marketplace connecting farmers
                and buyers while making agricultural produce
                easier to manage, discover, and sell.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">Platform Overview</div>',
        unsafe_allow_html=True,
    )

    st.header("Everything you need in one place")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">👨‍🌾</div>
                <div class="feature-title">Manage Farmers</div>
                <div class="feature-text">
                    Register farmers and maintain their
                    basic agricultural information.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🧺</div>
                <div class="feature-title">List Produce</div>
                <div class="feature-text">
                    Add agricultural products with quantity,
                    price, unit, and harvest information.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🤝</div>
                <div class="feature-title">Connect Buyers</div>
                <div class="feature-text">
                    Manage buyers and allow them to place
                    orders for available produce.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📦</div>
                <div class="feature-title">Manage Orders</div>
                <div class="feature-text">
                    Place and track produce orders directly
                    through the marketplace.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">View Reports</div>
                <div class="feature-text">
                    Analyze farmer revenue, buyer activity,
                    pricing, ratings, and payments.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🌾</div>
                <div class="feature-title">Fresh Produce</div>
                <div class="feature-text">
                    Keep track of available agricultural
                    products from registered farmers.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    st.info(
        "Use the navigation menu on the left to get started."
    )


# ============================================================
# ADD FARMER
# ============================================================

elif page == "Add Farmer":

    st.markdown(
        '<div class="section-label">Farmer Management</div>',
        unsafe_allow_html=True,
    )

    st.header("👨‍🌾 Register a Farmer")

    st.write(
        "Add a farmer and their primary agricultural information."
    )

    with st.form("farmer_form"):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Name",
                placeholder="Enter farmer name",
            )

        with col2:
            village = st.text_input(
                "Village",
                placeholder="Enter village",
            )

        col3, col4 = st.columns(2)

        with col3:
            contact = st.text_input(
                "Contact",
                placeholder="Phone number",
            )

        with col4:
            crop = st.text_input(
                "Primary crop",
                placeholder="e.g. Rubber, Coconut",
            )

        st.write("")

        submitted = st.form_submit_button(
            "Add Farmer",
            use_container_width=True,
        )

        if submitted:

            run_write(
                "INSERT INTO farmers (name, village, contact, primary_crop) VALUES (%s, %s, %s, %s)",
                (name, village, contact, crop),
            )

            st.success(f"Added farmer {name}")


# ============================================================
# ADD BUYER
# ============================================================

elif page == "Add Buyer":

    st.markdown(
        '<div class="section-label">Buyer Management</div>',
        unsafe_allow_html=True,
    )

    st.header("🛒 Register a Buyer")

    st.write(
        "Add a retailer, wholesaler, or consumer to the marketplace."
    )

    with st.form("buyer_form"):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Name",
                placeholder="Enter buyer name",
            )

        with col2:
            buyer_type = st.selectbox(
                "Type",
                [
                    "retailer",
                    "wholesaler",
                    "consumer",
                ],
            )

        col3, col4 = st.columns(2)

        with col3:
            location = st.text_input(
                "Location",
                placeholder="Enter location",
            )

        with col4:
            contact = st.text_input(
                "Contact",
                placeholder="Phone number",
            )

        st.write("")

        submitted = st.form_submit_button(
            "Add Buyer",
            use_container_width=True,
        )

        if submitted:

            run_write(
                "INSERT INTO buyers (name, buyer_type, location, contact) VALUES (%s, %s, %s, %s)",
                (name, buyer_type, location, contact),
            )

            st.success(f"Added buyer {name}")


# ============================================================
# ADD LISTING
# ============================================================

elif page == "Add Listing":

    st.markdown(
        '<div class="section-label">Marketplace</div>',
        unsafe_allow_html=True,
    )

    st.header("🌾 List Produce")

    farmers = run_query(
        "SELECT farmer_id, name FROM farmers ORDER BY name"
    )

    if farmers.empty:

        st.warning(
            "No farmers found. Please add a farmer first."
        )

    else:

        with st.form("listing_form"):

            col1, col2 = st.columns(2)

            with col1:
                farmer = st.selectbox(
                    "Farmer",
                    farmers["name"],
                )

            with col2:
                crop_name = st.text_input(
                    "Crop",
                    placeholder="e.g. Rubber Sheet",
                )

            col3, col4 = st.columns(2)

            with col3:
                quantity = st.number_input(
                    "Quantity",
                    min_value=0.0,
                    step=1.0,
                )

            with col4:
                unit = st.text_input(
                    "Unit",
                    value="kg",
                )

            col5, col6 = st.columns(2)

            with col5:
                price = st.number_input(
                    "Price per unit",
                    min_value=0.0,
                    step=1.0,
                )

            with col6:
                harvest_date = st.date_input(
                    "Harvest date"
                )

            st.write("")

            submitted = st.form_submit_button(
                "Add Listing",
                use_container_width=True,
            )

            farmer_id = int(
                farmers.loc[
                    farmers["name"] == farmer,
                    "farmer_id"
                ].iloc[0]
            )

            if submitted:

                run_write(
                    """INSERT INTO listings
                       (farmer_id, crop_name, quantity,
                        unit, price_per_unit, harvest_date)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        farmer_id,
                        crop_name,
                        quantity,
                        unit,
                        price,
                        harvest_date,
                    ),
                )

                st.success(
                    f"Listed {crop_name} for {farmer}"
                )


# ============================================================
# PLACE ORDER
# ============================================================

elif page == "Place Order":

    st.markdown(
        '<div class="section-label">Orders</div>',
        unsafe_allow_html=True,
    )

    st.header("📦 Place an Order")

    buyers = run_query(
        "SELECT buyer_id, name FROM buyers ORDER BY name"
    )

    listings = run_query(
        """SELECT l.listing_id, f.name AS farmer_name, l.crop_name,
                  l.quantity, l.price_per_unit
           FROM listings l JOIN farmers f
           ON l.farmer_id = f.farmer_id
           WHERE l.status = 'available'"""
    )

    if buyers.empty or listings.empty:

        st.warning(
            "Need at least one buyer and one available listing."
        )

    else:

        listings["label"] = (
            listings["farmer_name"]
            + " — "
            + listings["crop_name"]
            + " ("
            + listings["quantity"].astype(str)
            + " available)"
        )

        with st.form("order_form"):

            col1, col2 = st.columns(2)

            with col1:

                buyer = st.selectbox(
                    "Buyer",
                    buyers["name"],
                )

                buyer_id = int(
                    buyers.loc[
                        buyers["name"] == buyer,
                        "buyer_id"
                    ].iloc[0]
                )

            with col2:

                listing_label = st.selectbox(
                    "Listing",
                    listings["label"],
                )

                listing_row = listings.loc[
                    listings["label"] == listing_label
                ].iloc[0]

                listing_id = int(
                    listing_row["listing_id"]
                )

            st.write("")

            col3, col4 = st.columns(2)

            with col3:

                qty = st.number_input(
                    "Quantity to order",
                    min_value=0.0,
                    max_value=float(
                        listing_row["quantity"]
                    ),
                    step=1.0,
                )

            with col4:

                st.metric(
                    "Price per unit",
                    f"₹ {listing_row['price_per_unit']}"
                )

            st.write("")

            submitted = st.form_submit_button(
                "Place Order",
                use_container_width=True,
            )

            if submitted:

                run_write(
                    "INSERT INTO orders (buyer_id, listing_id, quantity_ordered) VALUES (%s, %s, %s)",
                    (
                        buyer_id,
                        listing_id,
                        qty,
                    ),
                )

                st.success(
                    "Order placed — listing quantity updated automatically by the trigger."
                )


# ============================================================
# ACTIVE LISTINGS
# ============================================================

elif page == "Active Listings":

    st.markdown(
        '<div class="section-label">Marketplace</div>',
        unsafe_allow_html=True,
    )

    st.header("🌱 Active Listings")

    listings = run_query(
        "SELECT * FROM active_listings_view ORDER BY harvest_date"
    )

    if listings.empty:

        st.info(
            "There are currently no active listings."
        )

    else:

        st.dataframe(
            listings,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":

    st.markdown(
        '<div class="section-label">Analytics</div>',
        unsafe_allow_html=True,
    )

    st.header("📊 Reports & Analytics")

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


    # --------------------------------------------------------
    # Revenue per farmer
    # --------------------------------------------------------

    if report == "Revenue per farmer":

        farmers = run_query(
            "SELECT farmer_id, name FROM farmers ORDER BY name"
        )

        if farmers.empty:

            st.info("No farmers available.")

        else:

            farmer = st.selectbox(
                "Farmer",
                farmers["name"],
            )

            farmer_id = int(
                farmers.loc[
                    farmers["name"] == farmer,
                    "farmer_id"
                ].iloc[0]
            )

            st.dataframe(
                run_query(
                    "SELECT * FROM get_farmer_revenue(%s)",
                    (farmer_id,),
                ),
                use_container_width=True,
                hide_index=True,
            )


    # --------------------------------------------------------
    # Most active buyers
    # --------------------------------------------------------

    elif report == "Most active buyers":

        st.dataframe(
            run_query(
                """SELECT b.name, COUNT(o.order_id) AS total_orders,
                          SUM(o.quantity_ordered) AS total_volume
                   FROM buyers b JOIN orders o
                   ON b.buyer_id = o.buyer_id
                   GROUP BY b.name
                   ORDER BY total_volume DESC"""
            ),
            use_container_width=True,
            hide_index=True,
        )


    # --------------------------------------------------------
    # Price trend
    # --------------------------------------------------------

    elif report == "Price trend":

        crop = st.text_input(
            "Crop name",
            value="Rubber Sheet",
        )

        st.dataframe(
            run_query(
                """SELECT crop_name, record_date,
                          avg_market_price
                   FROM price_history
                   WHERE crop_name = %s
                   ORDER BY record_date""",
                (crop,),
            ),
            use_container_width=True,
            hide_index=True,
        )


    # --------------------------------------------------------
    # Unsold stock
    # --------------------------------------------------------

    elif report == "Unsold stock (15+ days)":

        st.dataframe(
            run_query(
                """SELECT f.name, l.crop_name,
                          l.quantity, l.harvest_date
                   FROM listings l JOIN farmers f
                   ON l.farmer_id = f.farmer_id
                   WHERE l.status = 'available'
                   AND l.harvest_date <
                   CURRENT_DATE - INTERVAL '15 days'"""
            ),
            use_container_width=True,
            hide_index=True,
        )


    # --------------------------------------------------------
    # Average farmer rating
    # --------------------------------------------------------

    elif report == "Average farmer rating":

        st.dataframe(
            run_query(
                """SELECT f.name,
                          AVG(r.score) AS avg_rating,
                          COUNT(r.rating_id) AS num_ratings
                   FROM farmers f
                   JOIN listings l
                   ON f.farmer_id = l.farmer_id
                   JOIN orders o
                   ON l.listing_id = o.listing_id
                   JOIN ratings r
                   ON o.order_id = r.order_id
                   GROUP BY f.name
                   ORDER BY avg_rating DESC"""
            ),
            use_container_width=True,
            hide_index=True,
        )


    # --------------------------------------------------------
    # Pending payments
    # --------------------------------------------------------

    elif report == "Pending payments":

        st.dataframe(
            run_query(
                """SELECT o.order_id,
                          b.name AS buyer,
                          p.amount,
                          p.status
                   FROM orders o
                   JOIN buyers b
                   ON o.buyer_id = b.buyer_id
                   JOIN payments p
                   ON o.order_id = p.order_id
                   WHERE p.status = 'pending'"""
            ),
            use_container_width=True,
            hide_index=True,
        )