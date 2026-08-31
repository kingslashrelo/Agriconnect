import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import re
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
    return to_df(query.execute().data)


def fetch_eq(table, column, value, columns="*", order_by=None):
    query = supabase.from_(table).select(columns).eq(column, value)
    if order_by:
        query = query.order(order_by)
    return to_df(query.execute().data)


def insert_row(table, payload):
    return supabase.from_(table).insert(payload).execute()


# ============================================================
# VALIDATION UTILITIES
# ============================================================

def validate_phone(phone):
    """Validate phone number format"""
    return bool(re.match(r'^[6-9]\d{9}$', str(phone).strip()))

def validate_name(name):
    """Validate name (letters and spaces only)"""
    return bool(re.match(r'^[a-zA-Z\s]{2,}$', str(name).strip()))

def validate_not_empty(value):
    """Validate field is not empty"""
    return bool(str(value).strip())


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
# CUSTOM UI STYLING - ENHANCED
# ============================================================

st.markdown(
    """
    <style>

    /* =========================================================
       AGRICONNECT — PREMIUM LIGHT UI WITH ENHANCED STYLING
       ========================================================= */

    * {
        margin: 0;
        padding: 0;
    }

    :root {
        --agri-green: #2F6B3C;
        --agri-green-dark: #1F4D2B;
        --agri-green-light: #E5F3E8;
        --agri-green-soft: #EEF7F0;
        --agri-border: #DCE8DF;
        --agri-text: #1E293B;
        --agri-muted: #64748B;
        --agri-light-muted: #94A3B8;
        --agri-surface: #FFFFFF;
        --agri-page: #F7FAF8;
        --agri-error: #DC2626;
        --agri-warning: #F59E0B;
        --agri-success: #10B981;
        --agri-info: #3B82F6;
    }

    /* ========= BASE ========= */
    .stApp {
        background: var(--agri-page);
        color: var(--agri-text);
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: var(--agri-page);
    }

    .main .block-container {
        max-width: 1400px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    /* ========= SIDEBAR ========= */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F1F7F2 0%, #FFFFFF 100%);
        border-right: 1px solid var(--agri-border);
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--agri-green-dark) !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: var(--agri-text) !important;
        font-weight: 500 !important;
    }

    /* Navigation Radio Group */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.35rem 0;
        transition: all 0.3s ease;
        color: var(--agri-text) !important;
        font-weight: 600 !important;
        cursor: pointer;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: var(--agri-green-light);
        border-color: var(--agri-border);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: var(--agri-green) !important;
        border-color: var(--agri-green) !important;
        box-shadow: 0 4px 12px rgba(47, 107, 60, 0.25);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none;
    }

    /* ========= TYPOGRAPHY ========= */
    h1 {
        color: var(--agri-text) !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        line-height: 1.2 !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        color: var(--agri-text) !important;
        font-weight: 750 !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.35rem !important;
    }

    h3 {
        color: var(--agri-text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }

    p, .stMarkdown, .stText, label {
        color: var(--agri-text) !important;
        line-height: 1.6 !important;
        font-weight: 500 !important;
    }

    .stMarkdown small {
        color: var(--agri-muted) !important;
        font-weight: 500 !important;
    }

    /* ========= BUTTONS ========= */
    .stButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        border-radius: 11px !important;
        border: 2px solid var(--agri-green) !important;
        background: var(--agri-green) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.25rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(47, 107, 60, 0.15) !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: var(--agri-green-dark) !important;
        border-color: var(--agri-green-dark) !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(47, 107, 60, 0.3) !important;
    }

    .stButton > button:active,
    .stFormSubmitButton > button:active {
        transform: translateY(0) !important;
    }

    /* ========= FORMS ========= */
    div[data-testid="stForm"] {
        border: 2px solid var(--agri-border) !important;
        border-radius: 18px !important;
        padding: 2rem !important;
        background: var(--agri-surface) !important;
        box-shadow: 0 10px 30px rgba(31, 77, 43, 0.08) !important;
    }

    div[data-testid="stForm"] > button {
        margin-top: 1.5rem !important;
    }

    /* ========= INPUT FIELDS ========= */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 11px !important;
        border: 2px solid var(--agri-border) !important;
        padding: 0.75rem 1rem !important;
        background: #FFFFFF !important;
        color: var(--agri-text) !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--agri-green) !important;
        box-shadow: 0 0 0 3px rgba(47, 107, 60, 0.1) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--agri-light-muted) !important;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        border-radius: 11px !important;
        border: 2px solid var(--agri-border) !important;
        background: #FFFFFF !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: var(--agri-green-light) !important;
    }

    div[data-baseweb="select"] > div:focus-visible {
        border-color: var(--agri-green) !important;
        box-shadow: 0 0 0 3px rgba(47, 107, 60, 0.1) !important;
    }

    /* ========= CARDS ========= */
    .feature-card {
        height: 100%;
        min-height: 200px;
        padding: 28px;
        border-radius: 18px;
        border: 2px solid var(--agri-border);
        background: var(--agri-surface);
        box-shadow: 0 8px 24px rgba(31, 77, 43, 0.06);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--agri-green), transparent);
    }

    .feature-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(31, 77, 43, 0.12);
        border-color: var(--agri-green);
    }

    /* ========= METRICS ========= */
    div[data-testid="stMetric"] {
        background: var(--agri-surface);
        border: 2px solid var(--agri-border);
        padding: 1.25rem;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 77, 43, 0.05);
    }

    div[data-testid="stMetric"] > div {
        font-weight: 600 !important;
    }

    /* ========= DATA TABLES ========= */
    div[data-testid="stDataFrame"] {
        border: 2px solid var(--agri-border) !important;
        border-radius: 14px !important;
        overflow: hidden;
        background: var(--agri-surface) !important;
        box-shadow: 0 4px 12px rgba(31, 77, 43, 0.05) !important;
    }

    [data-testid="stDataFrame"] tbody tr {
        border-bottom: 1px solid #E0E7FF !important;
    }

    [data-testid="stDataFrame"] tbody tr:hover {
        background-color: #F0F9FF !important;
    }

    [data-testid="stDataFrame"] thead tr {
        background: linear-gradient(90deg, var(--agri-green-light) 0%, #FFFFFF 100%) !important;
        border-bottom: 2px solid var(--agri-border) !important;
    }

    [data-testid="stDataFrame"] th {
        color: var(--agri-green-dark) !important;
        font-weight: 700 !important;
        padding: 1rem !important;
    }

    [data-testid="stDataFrame"] td {
        padding: 0.875rem 1rem !important;
        color: var(--agri-text) !important;
    }

    /* ========= ALERTS ========= */
    div[data-testid="stAlert"] {
        border-radius: 14px !important;
        border: 2px solid !important;
        padding: 1rem 1.25rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stAlert"] [data-testid="stAlertTitle"] {
        font-weight: 700 !important;
    }

    /* Success */
    .st-emotion-cache-1y4p8pa > div > div[role="alert"] {
        background-color: rgba(16, 185, 129, 0.08) !important;
        border-color: var(--agri-success) !important;
        color: var(--agri-success) !important;
    }

    /* Warning */
    div[data-testid="stAlert"] {
        background-color: rgba(245, 158, 11, 0.08) !important;
        border-color: var(--agri-warning) !important;
    }

    /* Info */
    div[data-testid="stAlert"][kind="info"] {
        background-color: rgba(59, 130, 246, 0.08) !important;
        border-color: var(--agri-info) !important;
    }

    /* ========= HERO ========= */
    .hero {
        padding: 48px;
        border-radius: 22px;
        background: linear-gradient(135deg, var(--agri-green-light) 0%, #F9FCF9 70%);
        border: 2px solid var(--agri-border);
        margin-bottom: 36px;
        box-shadow: 0 10px 30px rgba(31, 77, 43, 0.08);
    }

    .hero-title {
        font-size: clamp(36px, 5vw, 52px);
        font-weight: 800;
        color: var(--agri-green-dark);
        margin-bottom: 14px;
        letter-spacing: -0.04em;
        line-height: 1.1;
    }

    .hero-subtitle {
        font-size: 18px;
        color: var(--agri-muted);
        max-width: 800px;
        line-height: 1.8;
        font-weight: 500;
    }

    /* ========= SECTION LABELS ========= */
    .section-label {
        color: var(--agri-green);
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        display: inline-block;
    }

    /* ========= FEATURE ICONS & TEXT ========= */
    .feature-icon {
        font-size: 42px;
        line-height: 1;
        display: inline-block;
        margin-bottom: 12px;
    }

    .feature-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--agri-green-dark);
        margin-bottom: 8px;
    }

    .feature-text {
        color: var(--agri-muted);
        line-height: 1.7;
        margin-top: 8px;
        font-weight: 500;
        font-size: 15px;
    }

    /* ========= COLUMN GAPS ========= */
    div[data-testid="column"] {
        gap: 1.5rem !important;
    }

    /* ========= DIVIDERS ========= */
    hr {
        border: 0;
        border-top: 2px solid var(--agri-border);
        margin: 1.5rem 0 !important;
    }

    /* ========= RESPONSIVE ========= */
    @media (max-width: 1024px) {
        .main .block-container {
            max-width: 100%;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }

        div[data-testid="stForm"] {
            padding: 1.5rem !important;
        }

        .hero {
            padding: 36px;
        }

        .hero-title {
            font-size: clamp(28px, 4vw, 42px);
        }
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 1rem;
        }

        .hero {
            padding: 28px;
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 30px;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            font-size: 16px;
        }

        div[data-testid="stForm"] {
            padding: 1.25rem !important;
            border-radius: 14px !important;
        }

        .feature-card {
            min-height: 160px;
            padding: 20px;
        }

        .feature-icon {
            font-size: 36px;
        }

        .feature-title {
            font-size: 18px;
        }
    }

    @media (max-width: 640px) {
        .main .block-container {
            max-width: 100%;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        h1 {
            font-size: 24px !important;
        }

        .hero-title {
            font-size: 24px;
        }

        .hero-subtitle {
            font-size: 15px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR - ENHANCED NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="padding: 20px 0 30px 0; border-bottom: 2px solid var(--agri-border);">
            <div style="font-size: 40px; margin-bottom: 10px;">🌱</div>
            <h1 style="margin: 0; font-size: 28px;">AgriConnect</h1>
            <p style="color: var(--agri-muted); margin-top: 8px; font-size: 14px; font-weight: 600;">
                Farmer-Buyer Marketplace
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin: 24px 0 16px 0;'><p style='font-size: 13px; font-weight: 800; color: var(--agri-green); text-transform: uppercase; letter-spacing: 1.2px; margin: 0;'>Navigation</p></div>", unsafe_allow_html=True)

    page = st.radio(
        "Go to",
        [
            "🏠 Home",
            "👨‍🌾 Add Farmer",
            "🛒 Add Buyer",
            "🌾 Add Listing",
            "📦 Place Order",
            "📋 Active Listings",
            "📊 Reports",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='margin: 24px 0;'>", unsafe_allow_html=True)

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption("AgriConnect")
    with col_info2:
        st.caption("v1.0")

    st.caption("🌾 Connect farmers with buyers")


# ============================================================
# HOME PAGE - ENHANCED
# ============================================================

if page == "🏠 Home":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">🌱 Welcome to AgriConnect</div>
            <div class="hero-subtitle">
                A modern digital marketplace connecting farmers and buyers 
                while making agricultural produce easier to manage, discover, and sell.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">📈 Platform Features</div>',
        unsafe_allow_html=True,
    )
    st.header("Everything you need in one place", anchor=False)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">👨‍🌾</div>
                <div class="feature-title">Manage Farmers</div>
                <div class="feature-text">
                    Register farmers and maintain their agricultural 
                    profile information with ease.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🌾</div>
                <div class="feature-title">List Produce</div>
                <div class="feature-text">
                    Add agricultural products with quantity, price, 
                    unit, and harvest date information.
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
                    Manage buyers and allow them to place orders 
                    for available produce seamlessly.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    col4, col5, col6 = st.columns(3, gap="large")

    with col4:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📦</div>
                <div class="feature-title">Manage Orders</div>
                <div class="feature-text">
                    Place and track produce orders directly through 
                    the marketplace in real-time.
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
                    Analyze farmer revenue, buyer activity, pricing trends, 
                    ratings, and payment status.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">💡</div>
                <div class="feature-title">Smart Insights</div>
                <div class="feature-text">
                    Get actionable insights on market trends, 
                    demand, and pricing opportunities.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    col_info1, col_info2 = st.columns([1, 1])
    with col_info1:
        st.info("📌 **Getting Started**\n\nUse the navigation menu on the left to get started. Start by registering farmers and buyers, then create listings and place orders.")
    
    with col_info2:
        st.success("✅ **Ready to go**\n\nYour marketplace is fully set up and ready to connect farmers with buyers. Create your first listing today!")


# ============================================================
# ADD FARMER - ENHANCED WITH VALIDATION
# ============================================================

elif page == "👨‍🌾 Add Farmer":

    st.markdown('<div class="section-label">👨‍🌾 Farmer Management</div>', unsafe_allow_html=True)
    st.header("Register a Farmer", anchor=False)
    st.markdown("<p style='color: var(--agri-muted); margin-bottom: 24px;'>Add a new farmer and their primary agricultural information to the marketplace.</p>", unsafe_allow_html=True)

    with st.form("farmer_form", clear_on_submit=True):

        col1, col2 = st.columns(2, gap="large")

        with col1:
            name = st.text_input(
                "Full Name*",
                placeholder="Enter farmer name",
                max_chars=100,
            )
            st.caption("Required field - letters and spaces only")

        with col2:
            village = st.text_input(
                "Village / Area*",
                placeholder="Enter village or area name",
                max_chars=100,
            )
            st.caption("Required field")

        col3, col4 = st.columns(2, gap="large")

        with col3:
            contact = st.text_input(
                "Phone Number*",
                placeholder="Enter 10-digit mobile number",
                max_chars=10,
            )
            st.caption("Format: 10-digit number (6-9...)")

        with col4:
            crop = st.text_input(
                "Primary Crop*",
                placeholder="e.g. Rubber, Coconut, Rice",
                max_chars=50,
            )
            st.caption("Main crop cultivated")

        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "✓ Register Farmer",
            use_container_width=True,
        )

        if submitted:
            # Validation
            errors = []
            
            if not validate_name(name):
                errors.append("Name must be 2+ letters only")
            if not validate_not_empty(village):
                errors.append("Village name is required")
            if not validate_phone(contact):
                errors.append("Phone must be 10 digits (6-9)")
            if not validate_not_empty(crop):
                errors.append("Primary crop is required")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    insert_row(
                        "farmers",
                        {
                            "name": name.strip(),
                            "village": village.strip(),
                            "contact": contact.strip(),
                            "primary_crop": crop.strip(),
                        },
                    )
                    st.success(f"✅ Successfully registered farmer **{name}**!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Database error: {str(e)}")


# ============================================================
# ADD BUYER - ENHANCED WITH VALIDATION
# ============================================================

elif page == "🛒 Add Buyer":

    st.markdown('<div class="section-label">🛒 Buyer Management</div>', unsafe_allow_html=True)
    st.header("Register a Buyer", anchor=False)
    st.markdown("<p style='color: var(--agri-muted); margin-bottom: 24px;'>Add a retailer, wholesaler, or consumer to the marketplace.</p>", unsafe_allow_html=True)

    with st.form("buyer_form", clear_on_submit=True):

        col1, col2 = st.columns(2, gap="large")

        with col1:
            name = st.text_input(
                "Business/Name*",
                placeholder="Enter buyer name or business name",
                max_chars=100,
            )
            st.caption("Required field")

        with col2:
            buyer_type = st.selectbox(
                "Buyer Type*",
                ["", "Retailer", "Wholesaler", "Consumer"],
            )
            if buyer_type:
                st.caption(f"Selected: {buyer_type}")
            else:
                st.caption("Select a category")

        col3, col4 = st.columns(2, gap="large")

        with col3:
            location = st.text_input(
                "Location/City*",
                placeholder="Enter city or location",
                max_chars=100,
            )
            st.caption("Required field")

        with col4:
            contact = st.text_input(
                "Phone Number*",
                placeholder="Enter 10-digit mobile number",
                max_chars=10,
            )
            st.caption("Format: 10-digit number")

        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "✓ Register Buyer",
            use_container_width=True,
        )

        if submitted:
            errors = []
            
            if not validate_not_empty(name):
                errors.append("Buyer name is required")
            if not buyer_type:
                errors.append("Please select a buyer type")
            if not validate_not_empty(location):
                errors.append("Location is required")
            if not validate_phone(contact):
                errors.append("Phone must be 10 digits")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    insert_row(
                        "buyers",
                        {
                            "name": name.strip(),
                            "buyer_type": buyer_type.strip().lower(),
                            "location": location.strip(),
                            "contact": contact.strip(),
                        },
                    )
                    st.success(f"✅ Successfully registered buyer **{name}** as {buyer_type}!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Database error: {str(e)}")



# ============================================================
# ADD LISTING - ENHANCED WITH VALIDATION
# ============================================================

elif page == "🌾 Add Listing":

    st.markdown('<div class="section-label">🌾 Marketplace</div>', unsafe_allow_html=True)
    st.header("List Your Produce", anchor=False)
    st.markdown("<p style='color: var(--agri-muted); margin-bottom: 24px;'>Add agricultural products to the marketplace with pricing and availability information.</p>", unsafe_allow_html=True)

    farmers = fetch_all(
        "farmers", "farmer_id, name", order_by="name"
    )

    if farmers.empty:
        st.warning("⚠️ No farmers found. Please register a farmer first before listing produce.", icon="⚠️")
        st.info("Click on '👨‍🌾 Add Farmer' in the sidebar to get started.")

    else:

        with st.form("listing_form", clear_on_submit=True):

            col1, col2 = st.columns(2, gap="large")

            with col1:
                farmer = st.selectbox(
                    "Select Farmer*",
                    farmers["name"],
                )
                st.caption("Required field")

            with col2:
                crop_name = st.text_input(
                    "Product Name*",
                    placeholder="e.g. Rubber Sheet, Premium Rice",
                    max_chars=100,
                )
                st.caption("Product name or variety")

            col3, col4 = st.columns(2, gap="large")

            with col3:
                quantity = st.number_input(
                    "Quantity Available*",
                    min_value=0.1,
                    step=0.5,
                    format="%.2f",
                )
                st.caption("Amount in selected units")

            with col4:
                unit = st.selectbox(
                    "Unit of Measurement*",
                    ["kg", "tons", "liters", "quintal", "bag", "box", "piece"],
                )
                st.caption("Unit type")

            col5, col6 = st.columns(2, gap="large")

            with col5:
                price = st.number_input(
                    "Price per Unit (₹)*",
                    min_value=0.0,
                    step=10.0,
                    format="%.2f",
                )
                st.caption("Price in rupees")

            with col6:
                harvest_date = st.date_input(
                    "Harvest Date*",
                )
                st.caption("Date of harvest")

            # Summary
            st.markdown("<div style='margin: 20px 0; padding: 16px; background: var(--agri-green-light); border-radius: 12px;'>", unsafe_allow_html=True)
            col_sum1, col_sum2 = st.columns(2)
            with col_sum1:
                st.metric("Total Value (₹)", f"₹ {quantity * price:,.2f}")
            with col_sum2:
                st.metric("Units", f"{quantity} {unit}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

            submitted = st.form_submit_button(
                "✓ Create Listing",
                use_container_width=True,
            )

            farmer_id = int(
                farmers.loc[
                    farmers["name"] == farmer,
                    "farmer_id"
                ].iloc[0]
            )

            if submitted:
                errors = []
                
                if not validate_not_empty(crop_name):
                    errors.append("Product name is required")
                if quantity <= 0:
                    errors.append("Quantity must be greater than 0")
                if price <= 0:
                    errors.append("Price must be greater than 0")

                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        insert_row(
                            "listings",
                            {
                                "farmer_id": farmer_id,
                                "crop_name": crop_name.strip(),
                                "quantity": quantity,
                                "unit": unit,
                                "price_per_unit": price,
                                "harvest_date": str(harvest_date),
                            },
                        )
                        st.success(f"✅ Successfully listed **{crop_name}** ({quantity} {unit}) for ₹{price}!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Database error: {str(e)}")


# ============================================================
# PLACE ORDER - ENHANCED
# ============================================================

elif page == "📦 Place Order":

    st.markdown('<div class="section-label">📦 Orders</div>', unsafe_allow_html=True)
    st.header("Place an Order", anchor=False)
    st.markdown("<p style='color: var(--agri-muted); margin-bottom: 24px;'>Create a new order for available produce.</p>", unsafe_allow_html=True)

    buyers = fetch_all(
        "buyers", "buyer_id, name", order_by="name"
    )

    listings = fetch_all(
        "active_listings_view",
        "listing_id, farmer_name, crop_name, quantity, price_per_unit, unit",
        order_by="farmer_name",
    )

    if buyers.empty or listings.empty:
        col_warn1, col_warn2 = st.columns(2)
        with col_warn1:
            st.warning("⚠️ No buyers registered yet.", icon="⚠️")
            st.info("Add a buyer to place orders.")
        with col_warn2:
            st.warning("⚠️ No available listings yet.", icon="⚠️")
            st.info("Create a listing first.")

    else:

        listings["label"] = (
            listings["farmer_name"]
            + " — "
            + listings["crop_name"]
            + " ("
            + listings["quantity"].astype(str)
            + " " 
            + listings["unit"]
            + " available @ ₹"
            + listings["price_per_unit"].astype(str)
            + ")"
        )

        with st.form("order_form", clear_on_submit=True):

            col1, col2 = st.columns(2, gap="large")

            with col1:
                buyer = st.selectbox(
                    "Select Buyer*",
                    buyers["name"],
                )
                st.caption("Required field")

                buyer_id = int(
                    buyers.loc[
                        buyers["name"] == buyer,
                        "buyer_id"
                    ].iloc[0]
                )

            with col2:
                listing_label = st.selectbox(
                    "Select Listing*",
                    listings["label"],
                )
                st.caption("Available produce")

                listing_row = listings.loc[
                    listings["label"] == listing_label
                ].iloc[0]

                listing_id = int(
                    listing_row["listing_id"]
                )

            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

            col3, col4 = st.columns(2, gap="large")

            with col3:
                qty = st.number_input(
                    "Quantity to Order*",
                    min_value=0.1,
                    max_value=float(
                        listing_row["quantity"]
                    ),
                    step=0.5,
                    format="%.2f",
                )
                st.caption(f"Max: {listing_row['quantity']} {listing_row['unit']}")

            with col4:
                total_price = qty * listing_row['price_per_unit']
                st.metric(
                    "Order Total (₹)",
                    f"₹ {total_price:,.2f}",
                )
                st.caption(f"@ ₹{listing_row['price_per_unit']}/unit")

            # Order Summary
            st.markdown("<div style='margin: 20px 0; padding: 16px; background: var(--agri-green-light); border-radius: 12px;'>", unsafe_allow_html=True)
            st.markdown(f"""
            **Order Summary**
            - Buyer: **{buyer}**
            - Product: **{listing_row['crop_name']}** (from {listing_row['farmer_name']})
            - Quantity: **{qty} {listing_row['unit']}**
            - Price/Unit: **₹{listing_row['price_per_unit']}**
            - **Total: ₹{total_price:,.2f}**
            """)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

            submitted = st.form_submit_button(
                "✓ Place Order",
                use_container_width=True,
            )

            if submitted:
                errors = []
                
                if qty <= 0:
                    errors.append("Order quantity must be greater than 0")
                if qty > float(listing_row["quantity"]):
                    errors.append(f"Insufficient stock. Maximum: {listing_row['quantity']} {listing_row['unit']}")

                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    try:
                        insert_row(
                            "orders",
                            {
                                "buyer_id": buyer_id,
                                "listing_id": listing_id,
                                "quantity_ordered": qty,
                            },
                        )
                        st.success(f"✅ Order placed successfully! ₹{total_price:,.2f} order created.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Database error: {str(e)}")


# ============================================================
# ACTIVE LISTINGS - ENHANCED
# ============================================================

elif page == "📋 Active Listings":

    st.markdown('<div class="section-label">📋 Marketplace</div>', unsafe_allow_html=True)
    st.header("Active Listings", anchor=False)
    st.markdown("<p style='color: var(--agri-muted); margin-bottom: 24px;'>Browse all currently available produce listings.</p>", unsafe_allow_html=True)

    listings = fetch_all(
        "active_listings_view", "*", order_by="harvest_date"
    )

    if listings.empty:
        st.info("📭 There are currently no active listings. Check back soon!")

    else:
        # Stats
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total Listings", len(listings))
        
        with col_stat2:
            total_qty = listings.get("quantity", pd.Series()).sum()
            st.metric("Total Quantity", f"{total_qty:,.1f}")
        
        with col_stat3:
            unique_farmers = listings.get("farmer_name", pd.Series()).nunique() if "farmer_name" in listings.columns else 0
            st.metric("Active Farmers", unique_farmers)

        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

        st.dataframe(
            listings,
            use_container_width=True,
            hide_index=True,
            column_config={
                "price_per_unit": st.column_config.NumberColumn(
                    label="Price (₹)",
                    format="₹%,.2f"
                ),
            }
        )


# ============================================================
# REPORTS
# ============================================================

elif page == "📊 Reports":

    st.markdown('<div class="section-label">📊 Analytics</div>', unsafe_allow_html=True)
    st.header("Reports & Analytics", anchor=False)
    st.markdown("<p style='color: var(--agri-muted); margin-bottom: 24px;'>View comprehensive insights and analytics about your marketplace activity.</p>", unsafe_allow_html=True)

    report = st.selectbox(
        "Choose a report",
        [
            "📈 Revenue per Farmer",
            "🏆 Most Active Buyers",
            "💹 Price Trend",
            "📦 Unsold Stock (15+ days)",
            "⭐ Average Farmer Rating",
            "💰 Pending Payments",
        ],
    )

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)


    # --------------------------------------------------------
    # Revenue per farmer
    # --------------------------------------------------------

    if report == "📈 Revenue per Farmer":

        farmers = fetch_all(
            "farmers", "farmer_id, name", order_by="name"
        )

        if farmers.empty:
            st.info("📭 No farmers available.")
        else:
            farmer = st.selectbox(
                "Select Farmer",
                farmers["name"],
            )
            st.caption("Choose a farmer to view their revenue details")

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

    elif report == "🏆 Most Active Buyers":

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

    elif report == "💹 Price Trend":

        crop = st.text_input(
            "Crop Name",
            value="Rubber Sheet",
            placeholder="e.g., Rice, Wheat, Rubber Sheet",
        )
        st.caption("Enter the crop name to view price history")

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

    elif report == "📦 Unsold Stock (15+ days)":

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

    elif report == "⭐ Average Farmer Rating":

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

    elif report == "💰 Pending Payments":

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