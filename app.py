import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


# ============================================================
# DATABASE (Supabase / PostgREST)
# ============================================================

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def to_df(rows):
    return pd.DataFrame(rows or [])


def fetch_all(table, columns="*", order_by=None):
    query = supabase.from_(table).select(columns)
    if order_by:
        query = query.order(order_by)
    return query.execute().data


def fetch_eq(table, column, value, columns="*", order_by=None):
    query = supabase.from_(table).select(columns).eq(column, value)
    if order_by:
        query = query.order(order_by)
    return query.execute().data


def insert_row(table, payload):
    return supabase.from_(table).insert(payload).execute()


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

            insert_row(
                "farmers",
                {
                    "name": name,
                    "village": village,
                    "contact": contact,
                    "primary_crop": crop,
                },
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

            insert_row(
                "buyers",
                {
                    "name": name,
                    "buyer_type": buyer_type,
                    "location": location,
                    "contact": contact,
                },
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

    farmers = to_df(
        fetch_all("farmers", "farmer_id, name", order_by="name")
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

                insert_row(
                    "listings",
                    {
                        "farmer_id": farmer_id,
                        "crop_name": crop_name,
                        "quantity": quantity,
                        "unit": unit,
                        "price_per_unit": price,
                        "harvest_date": str(harvest_date),
                    },
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

    buyers = to_df(
        fetch_all("buyers", "buyer_id, name", order_by="name")
    )

    listings = to_df(
        fetch_all(
            "active_listings_view",
            "listing_id, farmer_name, crop_name, quantity, price_per_unit",
            order_by="farmer_name",
        )
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

                insert_row(
                    "orders",
                    {
                        "buyer_id": buyer_id,
                        "listing_id": listing_id,
                        "quantity_ordered": qty,
                    },
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

    listings = to_df(
        fetch_all(
            "active_listings_view",
            "*",
            order_by="harvest_date",
        )
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

        farmers = to_df(
            fetch_all("farmers", "farmer_id, name", order_by="name")
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

            revenue = supabase.rpc(
                "get_farmer_revenue", {"p_farmer_id": farmer_id}
            ).execute().data

            st.dataframe(
                to_df(revenue),
                use_container_width=True,
                hide_index=True,
            )


    # --------------------------------------------------------
    # Most active buyers
    # --------------------------------------------------------

    elif report == "Most active buyers":

        st.dataframe(
            to_df(
                fetch_all("most_active_buyers_view", "*")
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
            to_df(
                fetch_eq(
                    "price_history",
                    "crop_name",
                    crop,
                    "crop_name, record_date, avg_market_price",
                    order_by="record_date",
                )
            ),
            use_container_width=True,
            hide_index=True,
        )


    # --------------------------------------------------------
    # Unsold stock
    # --------------------------------------------------------

    elif report == "Unsold stock (15+ days)":

        st.dataframe(
            to_df(
                fetch_all("unsold_stock_view", "*")
            ),
            use_container_width=True,
            hide_index=True,
        )


    # --------------------------------------------------------
    # Average farmer rating
    # --------------------------------------------------------

    elif report == "Average farmer rating":

        st.dataframe(
            to_df(
                fetch_all("farmer_avg_rating_view", "*")
            ),
            use_container_width=True,
            hide_index=True,
        )


    # --------------------------------------------------------
    # Pending payments
    # --------------------------------------------------------

    elif report == "Pending payments":

        st.dataframe(
            to_df(
                fetch_all("pending_payments_view", "*")
            ),
            use_container_width=True,
            hide_index=True,
        )