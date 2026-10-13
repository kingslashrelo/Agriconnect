import os
import re
import html

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


_DB_ERROR = {"message": None}


def _record_db_error(exc):
    if _DB_ERROR["message"] is None:
        _DB_ERROR["message"] = f"{type(exc).__name__}: {exc}"


def _not_configured():
    if supabase is None:
        _DB_ERROR["message"] = (
            "Supabase client is not configured — missing SUPABASE_URL / SUPABASE_KEY."
        )
        return True
    return False


def to_df(rows):
    return pd.DataFrame(rows or [])


def fetch_all(table, columns="*", order_by=None):
    if _not_configured():
        return pd.DataFrame()
    try:
        query = supabase.from_(table).select(columns)
        if order_by:
            query = query.order(order_by)
        return to_df(query.execute().data)
    except Exception as e:
        _record_db_error(e)
        return pd.DataFrame()


def fetch_eq(table, column, value, columns="*", order_by=None):
    if _not_configured():
        return pd.DataFrame()
    try:
        query = supabase.from_(table).select(columns).eq(column, value)
        if order_by:
            query = query.order(order_by)
        return to_df(query.execute().data)
    except Exception as e:
        _record_db_error(e)
        return pd.DataFrame()


def insert_row(table, payload):
    if supabase is None:
        raise RuntimeError("Supabase client is not configured.")
    return supabase.from_(table).insert(payload).execute()


def validate_phone(phone):
    return bool(re.match(r"^[6-9]\d{9}$", str(phone).strip()))


def validate_name(name):
    return bool(re.match(r"^[a-zA-Z\s]{2,}$", str(name).strip()))


def validate_not_empty(value):
    if value is None:
        return False
    return bool(str(value).strip())


ADD_NEW_CROP = "➕ Add a new crop…"

MAX_FARMER_CROPS = 8


def title_case(value):
    if not value:
        return value
    words = str(value).strip().split()
    return " ".join(w[:1].upper() + w[1:] for w in words)


CROP_CATALOG = [
    "Wheat", "Paddy (Rice)", "Maize (Corn)", "Sugarcane", "Cotton", "Groundnut",
    "Soybean", "Mustard", "Sunflower", "Sesame", "Safflower", "Linseed (Flax)",
    "Chickpea (Chana)", "Pigeon Pea (Arhar)", "Green Gram (Moong)", "Black Gram (Urad)",
    "Lentil (Masoor)", "Pea", "Peanut", "Finger Millet (Ragi)", "Pearl Millet (Bajra)",
    "Sorghum (Jowar)", "Barley", "Oats", "Quinoa", "Buckwheat",
    "Potato", "Sweet Potato", "Onion", "Tomato", "Brinjal", "Chilli", "Bell Pepper",
    "Ginger", "Turmeric", "Garlic", "Cabbage", "Cauliflower", "Broccoli", "Carrot",
    "Radish", "Beetroot", "Turnip", "Spinach (Palak)", "Fenugreek (Methi)", "Coriander",
    "Mint", "Lettuce", "Okra (Bhindi)", "Bitter Gourd (Karela)", "Bottle Gourd (Lauki)",
    "Ridge Gourd (Turai)", "Pumpkin", "Ash Gourd", "Cucumber", "Watermelon", "Muskmelon",
    "Banana", "Mango", "Papaya", "Guava", "Pomegranate", "Apple", "Grapes", "Orange",
    "Lemon", "Sapota (Chikoo)", "Pineapple", "Jackfruit", "Custard Apple", "Fig",
    "Date", "Coconut", "Arecanut", "Cashew", "Rubber", "Tea", "Coffee", "Cardamom",
    "Black Pepper", "Clove", "Nutmeg", "Vanilla", "Cinnamon", "Turmeric Finger",
    "Jute", "Bamboo", "Tapioca (Cassava)", "Yam", "Elephant Foot Yam", "Gooseberry (Amla)",
    "Drumstick (Moringa)", "Basil (Tulsi)", "Hibiscus", "Agave",
]


def fetch_crop_names():
    known = list(CROP_CATALOG)
    df = fetch_all("crops", "name")
    if not df.empty and "name" in df.columns:
        for n in df["name"].dropna():
            n = str(n).strip()
            if n and n.lower() not in (c.lower() for c in known):
                known.append(n)
    for n in st.session_state.get("added_crops", []):
        n = str(n).strip()
        if n and n.lower() not in (c.lower() for c in known):
            known.append(n)
    return known


def in_stock_crops():
    stock = set()
    df = fetch_all("active_listings_view", "crop_name")
    if not df.empty and "crop_name" in df.columns:
        stock = {str(n).strip() for n in df["crop_name"].dropna()}
    return stock


def ordered_crop_options():
    pinned = [str(c).strip() for c in st.session_state.get("pinned_crops", [])]
    stock = in_stock_crops()
    all_crops = fetch_crop_names()

    def rank(c):
        if c in pinned:
            return 0
        if c in stock:
            return 1
        return 2

    ordered = sorted(all_crops, key=lambda c: (rank(c), c.lower()))
    ordered.append(ADD_NEW_CROP)
    return ordered, set(pinned), stock


def crop_option_label(c, pinned, stock):
    if c is None:
        return ""
    if c == ADD_NEW_CROP:
        return c
    if c in pinned:
        return "📌 " + c
    if c in stock:
        return "✅ " + c + " · in stock"
    return c


def ensure_crop(name):
    name = title_case(str(name or "").strip())
    if not name:
        return name
    try:
        existing = set()
        df = fetch_all("crops", "name")
        if not df.empty and "name" in df.columns:
            existing = {str(n).strip().lower() for n in df["name"].dropna()}
        if name.lower() not in existing:
            insert_row(
                "crops",
                {
                    "name": name,
                    "seasons": ["Winter", "Summer", "Monsoon", "Autumn", "Spring"],
                    "revenue_min": "—",
                    "revenue_max": "—",
                    "market_outlook": "Added from the app.",
                },
            )
        st.session_state.setdefault("added_crops", [])
        if name not in st.session_state["added_crops"]:
            st.session_state["added_crops"].append(name)
    except Exception as e:
        _record_db_error(e)
    return name


def render_crop_pinner():
    all_crops = fetch_crop_names()
    current = st.session_state.get("pinned_crops", [])
    picked = st.multiselect(
        "📌 Pin crops — pinned crops always appear at the top of crop lists",
        options=all_crops,
        default=[c for c in current if c in all_crops],
        placeholder="Choose crops to pin…",
    )
    pinned = list(dict.fromkeys(str(c).strip() for c in picked))
    st.session_state["pinned_crops"] = pinned
    stock = in_stock_crops()
    return pinned, stock


st.set_page_config(
    page_title="AgriConnect",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --agri-green: #059669;
        --agri-green-dark: #047857;
        --agri-green-deep: #065F46;
        --agri-green-light: #ECFDF5;
        --agri-green-soft: #F0FDF4;
        --agri-lime: #34D399;
        --agri-border: #E6EBE8;
        --agri-text: #000000;
        --agri-muted: #1A1A1A;
        --agri-light-muted: #4B5563;
        --agri-surface: #FFFFFF;
        --agri-page: #FFFFFF;
        --agri-glass: rgba(255, 255, 255, 0.72);
        --agri-error: #DC2626;
        --agri-warning: #D97706;
        --agri-success: #059669;
        --agri-info: #2563EB;

        --agri-font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --agri-font-heading: 'Space Grotesk', 'Inter', -apple-system, sans-serif;

        --agri-shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.05);
        --agri-shadow-sm: 0 2px 10px rgba(15, 23, 42, 0.06);
        --agri-shadow-md: 0 16px 44px rgba(15, 23, 42, 0.09);
        --agri-shadow-lg: 0 24px 60px rgba(5, 150, 105, 0.16);
        --agri-radius: 16px;

        --glass-bg: rgba(255, 255, 255, 0.55);
        --glass-bg-strong: rgba(255, 255, 255, 0.72);
        --glass-border: rgba(255, 255, 255, 0.65);
        --glass-blur: blur(18px) saturate(160%);
        --glass-shadow: 0 10px 34px rgba(2, 6, 23, 0.09);
    }

    html { scroll-behavior: smooth; }

    .stApp {
        background-color: #FFFFFF;
        background-image:
            radial-gradient(46rem 46rem at 10% 6%, rgba(5, 150, 105, 0.12), transparent 62%),
            radial-gradient(40rem 40rem at 92% 10%, rgba(16, 185, 129, 0.10), transparent 64%),
            radial-gradient(44rem 44rem at 82% 94%, rgba(59, 130, 246, 0.07), transparent 66%);
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: 0% 0%, 100% 0%, 0% 100%;
        background-size: 130% 130%;
        animation: agriAurora 36s ease-in-out infinite;
        color: var(--agri-text);
        font-family: var(--agri-font-body) !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] { background: transparent; }

    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding: 2rem 1.5rem 4rem;
    }

    ::selection { background: #D1FAE5; color: var(--agri-green-deep); }

    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
    [data-testid="stAppDeployButton"] { display: none !important; }

    section[data-testid="stSidebar"] {
        background: var(--glass-bg-strong);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border-right: 1px solid var(--glass-border);
    }

    section[data-testid="stSidebar"] > div { background: transparent; }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.25rem 0 1rem;
    }

    .brand-mark {
        width: 44px;
        height: 44px;
        border-radius: 13px;
        background: var(--agri-green-light);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }

    .brand-name {
        font-family: var(--agri-font-heading);
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--agri-green-deep);
        line-height: 1.1;
    }

    .brand-tag {
        font-size: 0.74rem;
        color: var(--agri-muted);
        font-weight: 500;
    }

    .nav-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--agri-light-muted);
        margin: 0.75rem 0 0.35rem;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        width: 100%;
        border: 1px solid transparent;
        border-radius: 12px;
        padding: 0.6rem 0.8rem;
        margin: 2px 0;
        color: var(--agri-text);
        font-weight: 600;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: var(--agri-green-soft);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, var(--agri-green), var(--agri-lime));
        border-color: transparent;
        box-shadow: 0 8px 20px rgba(5, 150, 105, 0.25);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 0.95rem;
        font-weight: 600;
    }

    h1, h2, h3, h4 {
        font-family: var(--agri-font-heading) !important;
        color: var(--agri-text) !important;
        letter-spacing: -0.02em !important;
    }

    h1 { font-weight: 700 !important; line-height: 1.15; }
    h2, h3 { font-weight: 600 !important; }

    p, .stMarkdown, label { color: var(--agri-text); }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] *,
    .stCaption,
    small {
        color: var(--agri-muted) !important;
    }

    .page-subtitle {
        color: var(--agri-muted) !important;
        font-size: 1rem;
        margin: -0.25rem 0 1.5rem;
    }

    .section-label {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--agri-green-dark);
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin-bottom: 0.5rem;
    }

    .section-label::before {
        content: "";
        width: 20px;
        height: 2px;
        border-radius: 2px;
        background: linear-gradient(90deg, var(--agri-green), var(--agri-lime));
    }

    .stButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        border-radius: 12px !important;
        border: 1px solid transparent !important;
        background: linear-gradient(135deg, var(--agri-green), var(--agri-lime)) !important;
        color: #FFFFFF !important;
        font-family: var(--agri-font-body) !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
        padding: 0.7rem 1.2rem !important;
        box-shadow: 0 8px 22px rgba(5, 150, 105, 0.28) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        filter: brightness(1.05);
        transform: translateY(-1px);
        box-shadow: 0 12px 28px rgba(5, 150, 105, 0.36) !important;
    }

    .stButton > button:active,
    .stFormSubmitButton > button:active { transform: translateY(0); }

    div[data-testid="stForm"] {
        border: 1px solid var(--glass-border) !important;
        border-radius: 20px !important;
        background: var(--glass-bg-strong) !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
        padding: 1.75rem !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid var(--agri-border) !important;
        background: #FFFFFF !important;
        color: var(--agri-text) !important;
        font-family: var(--agri-font-body) !important;
        padding: 0.65rem 0.85rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--agri-green) !important;
        box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.14) !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder { color: var(--agri-light-muted) !important; }

    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1px solid var(--agri-border) !important;
        background: #FFFFFF !important;
        transition: all 0.2s ease !important;
    }

    div[data-baseweb="select"] > div:focus-within {
        border-color: var(--agri-green) !important;
        box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.14) !important;
    }

    .feature-card {
        height: 100%;
        padding: 1.6rem;
        border-radius: var(--agri-radius);
        border: 1px solid var(--agri-border);
        background: var(--agri-glass);
        backdrop-filter: blur(12px) saturate(140%);
        -webkit-backdrop-filter: blur(12px) saturate(140%);
        box-shadow: var(--agri-shadow-sm);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--agri-green), var(--agri-lime));
        opacity: 0.9;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--agri-shadow-md);
        border-color: #D1FAE5;
    }

    .feature-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 52px;
        height: 52px;
        border-radius: 14px;
        background: var(--agri-green-light);
        font-size: 26px;
        margin-bottom: 0.9rem;
    }

    .feature-title {
        font-family: var(--agri-font-heading);
        font-size: 1.08rem;
        font-weight: 600;
        color: var(--agri-text);
        margin-bottom: 0.35rem;
    }

    .feature-text {
        color: var(--agri-muted);
        font-size: 0.92rem;
        line-height: 1.65;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 3rem 2.5rem;
        border-radius: 24px;
        border: 1px solid var(--agri-border);
        background: radial-gradient(120% 160% at 0% 0%, #ECFDF5 0%, #FFFFFF 60%);
        box-shadow: var(--agri-shadow-sm);
        margin-bottom: 2rem;
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(5, 150, 105, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(5, 150, 105, 0.05) 1px, transparent 1px);
        background-size: 34px 34px;
        -webkit-mask-image: radial-gradient(120% 120% at 100% 0%, #000 0%, transparent 55%);
        mask-image: radial-gradient(120% 120% at 100% 0%, #000 0%, transparent 55%);
    }

    .hero-title {
        font-family: var(--agri-font-heading);
        font-size: clamp(2rem, 4.4vw, 3rem);
        font-weight: 700;
        color: var(--agri-green-deep);
        letter-spacing: -0.03em;
        line-height: 1.08;
        margin-bottom: 0.75rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: var(--agri-muted);
        max-width: 640px;
        line-height: 1.7;
    }

    div[data-testid="stMetric"] {
        background: var(--agri-glass);
        border: 1px solid var(--agri-border);
        border-radius: var(--agri-radius);
        padding: 1rem 1.1rem;
        box-shadow: var(--agri-shadow-xs);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    div[data-testid="stMetricLabel"] { color: var(--agri-muted) !important; font-weight: 600 !important; }

    div[data-testid="stMetricValue"] {
        font-family: var(--agri-font-heading) !important;
        color: var(--agri-text) !important;
        font-weight: 600 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--agri-border) !important;
        border-radius: var(--agri-radius) !important;
        overflow: hidden;
        background: #FFFFFF !important;
        box-shadow: var(--agri-shadow-xs) !important;
    }

    .st-key-agri_glass_a,
    .st-key-agri_glass_b {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 18px !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
    }

    div[data-testid="stExpander"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
        overflow: hidden;
    }

    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] summary { background: transparent !important; }

    div[data-testid="stAlert"] {
        background: var(--glass-bg-strong) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 14px !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
        padding: 0.9rem 1.1rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--agri-radius) !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
        overflow: hidden;
    }

    div[data-testid="stMetric"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
    }

    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[data-testid="stSelectboxVirtualDropdown"],
    div[data-testid="stSelectboxVirtualDropdown"] {
        background: var(--glass-bg-strong) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 14px !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
    }

    div[data-testid="stDialog"] > div,
    div[data-testid="stModal"] > div,
    div[role="dialog"] > div {
        background: var(--glass-bg-strong) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 20px !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        transition: all 0.2s ease;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: var(--glass-bg-strong) !important;
        border: 1px solid var(--glass-border) !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
    }

    div[data-testid="stSidebarUserContent"] .stButton > button {
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
    }

    hr { border: 0; border-top: 1px solid var(--agri-border); margin: 1.25rem 0; }

    @media (max-width: 1024px) {
        [data-testid="stMainBlockContainer"] { padding: 1.5rem 1.25rem 3rem; }
        .hero { padding: 2.25rem 1.75rem; }
    }

    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem 1rem 2.25rem; }
        .hero { padding: 1.75rem 1.25rem; border-radius: 18px; }
        .hero-title { font-size: 1.7rem; }
        .feature-card { padding: 1.25rem; }
    }

    /* ========= REACTIVE / ENHANCED INTERACTIONS ========= */

    @keyframes agriRise {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes agriFloat {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(20px, -24px) scale(1.08); }
    }

    @keyframes agriNavGlow {
        0%, 100% { box-shadow: 0 8px 20px rgba(5, 150, 105, 0.25); }
        50% { box-shadow: 0 8px 28px rgba(5, 150, 105, 0.45); }
    }

    @keyframes agriAurora {
        0%, 100% { background-position: 0% 0%, 100% 0%, 0% 100%; }
        33% { background-position: 12% 10%, 86% 6%, 8% 94%; }
        66% { background-position: 6% 8%, 92% 14%, 16% 90%; }
    }

    @keyframes agriPulse {
        0%, 100% { opacity: 0.65; }
        50% { opacity: 1; }
    }

    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #F3F6F4; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--agri-green), var(--agri-lime));
        border-radius: 999px;
        border: 2px solid #F3F6F4;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--agri-green-deep); }

    *:focus-visible {
        outline: 2px solid var(--agri-green) !important;
        outline-offset: 2px !important;
        border-radius: 6px;
    }

    a {
        color: var(--agri-green-dark);
        transition: color 0.2s ease;
    }
    a:hover { color: var(--agri-green); }

    [data-testid="stFooter"] { display: none !important; }

    .brand-mark { animation: agriFloat 7s ease-in-out infinite; }

    .section-label::before { animation: agriPulse 2.8s ease-in-out infinite; }

    .hero {
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .hero:hover {
        transform: translateY(-3px);
        box-shadow: 0 26px 60px rgba(5, 150, 105, 0.15);
        border-color: #D1FAE5;
    }
    .hero::before {
        content: "";
        position: absolute;
        right: -90px;
        top: -90px;
        width: 280px;
        height: 280px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.35), rgba(5, 150, 105, 0) 70%);
        filter: blur(12px);
        pointer-events: none;
        animation: agriFloat 9s ease-in-out infinite;
        z-index: 0;
    }
    .hero-title { transition: transform 0.2s ease, color 0.2s ease; }
    .hero:hover .hero-title { transform: translateX(5px); }
    .hero * { position: relative; z-index: 1; }

    .feature-card::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(115deg, transparent 30%, rgba(255, 255, 255, 0.6) 50%, transparent 70%);
        transform: translateX(-130%) skewX(-16deg);
        transition: transform 0.7s ease;
        pointer-events: none;
    }
    .feature-card:hover::after { transform: translateX(130%) skewX(-16deg); }

    .stButton > button,
    .stFormSubmitButton > button {
        position: relative;
        overflow: hidden;
    }
    .stButton > button::after,
    .stFormSubmitButton > button::after {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        width: 45%;
        background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.35), transparent);
        transform: translateX(-160%) skewX(-18deg);
        transition: transform 0.6s ease;
        pointer-events: none;
    }
    .stButton > button:hover::after,
    .stFormSubmitButton > button:hover::after { transform: translateX(260%) skewX(-18deg); }
    .stButton > button:active,
    .stFormSubmitButton > button:active { transform: scale(0.98); }

    div[data-testid="stMetric"] {
        animation: agriRise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease, border-color 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 44px rgba(5, 150, 105, 0.16) !important;
        border-color: var(--agri-lime) !important;
    }

    div[data-testid="stExpander"] {
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        animation: agriRise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    div[data-testid="stExpander"]:hover {
        transform: translateY(-2px);
        border-color: rgba(5, 150, 105, 0.4) !important;
        box-shadow: 0 16px 40px rgba(5, 150, 105, 0.12) !important;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        animation: agriRise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        transition: box-shadow 0.25s ease, border-color 0.25s ease;
    }
    div[data-testid="stDataFrame"]:hover {
        box-shadow: 0 16px 44px rgba(5, 150, 105, 0.14) !important;
        border-color: #D1FAE5 !important;
    }

    div[data-testid="stForm"] { animation: agriRise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both; }

    div[data-testid="stAlert"] { animation: agriRise 0.45s cubic-bezier(0.22, 1, 0.36, 1) both; }

    div[data-testid="stTabs"] button[role="tab"]:hover {
        background: rgba(5, 150, 105, 0.08) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        transition: all 0.22s ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        transform: translateX(3px);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        animation: agriNavGlow 3s ease-in-out infinite;
    }

    [data-testid="stVegaLiteChart"],
    [data-testid="stPlotlyChart"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--agri-radius) !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        box-shadow: var(--glass-shadow) !important;
    }

    [data-testid="stImage"] {
        border: 1px solid var(--agri-border);
        border-radius: var(--agri-radius);
        overflow: hidden;
        box-shadow: var(--agri-shadow-sm);
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) .feature-card,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) div[data-testid="stMetric"] { animation-delay: 0.06s; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) .feature-card,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) div[data-testid="stMetric"] { animation-delay: 0.14s; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) .feature-card,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) div[data-testid="stMetric"] { animation-delay: 0.22s; }

    /* ========= MICRO-INTERACTIONS II ========= */

    input, textarea { caret-color: var(--agri-green); }

    div[data-baseweb="input"] {
        border-radius: 12px !important;
        border-color: var(--agri-border) !important;
        background: #FFFFFF !important;
        transition: all 0.2s ease !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: var(--agri-green) !important;
        box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.14) !important;
    }

    div[data-testid="stNumberInput"] button {
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background: var(--agri-green-light) !important;
    }

    .stMarkdown code {
        background: var(--agri-green-light);
        color: var(--agri-green-deep);
        border-radius: 6px;
        padding: 0.15em 0.4em;
        font-size: 0.88em;
    }

    .stMarkdown pre {
        border: 1px solid var(--agri-border);
        border-radius: 12px;
        background: #F8FAF9 !important;
        padding: 1rem;
    }

    table {
        border-collapse: separate;
        border-spacing: 0;
        border: 1px solid var(--agri-border) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    .stMarkdown table thead th {
        background: var(--agri-green-soft) !important;
        color: var(--agri-green-deep) !important;
        font-weight: 700;
    }

    .stMarkdown blockquote {
        border-left: 3px solid var(--agri-green);
        background: var(--agri-green-light);
        border-radius: 0 10px 10px 0;
        padding: 0.6rem 1rem;
    }

    h2::after {
        content: "";
        display: block;
        width: 54px;
        height: 3px;
        border-radius: 3px;
        background: linear-gradient(90deg, var(--agri-green), var(--agri-lime));
        margin-top: 0.3rem;
    }

    .hero-title {
        background: linear-gradient(120deg, var(--agri-green-deep), var(--agri-green) 55%, #10B981);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .feature-icon {
        transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .feature-card:hover .feature-icon {
        transform: scale(1.12) rotate(-6deg);
    }

    .feature-card::before {
        transform-origin: left;
        animation: agriAccentIn 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.15s both;
    }
    .feature-card:hover::before { filter: brightness(1.08); }

    @keyframes agriAccentIn {
        from { transform: scaleX(0); }
        to { transform: scaleX(1); }
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background-size: 160% 160% !important;
        background-position: 0% 50% !important;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-position: 100% 50% !important;
        filter: brightness(1.04);
    }

    div[data-testid="stForm"],
    .st-key-agri_glass_a,
    .st-key-agri_glass_b {
        position: relative;
    }
    div[data-testid="stForm"]::before,
    .st-key-agri_glass_a::before,
    .st-key-agri_glass_b::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 26px;
        border-radius: 20px 20px 0 0;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.55), transparent);
        pointer-events: none;
    }

    hr {
        border: 0 !important;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--agri-lime), var(--agri-green), transparent);
        opacity: 0.5;
        margin: 1.25rem 0;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        border-bottom: 2px solid transparent !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        border-bottom: 2px solid var(--agri-green) !important;
    }

    @media (max-width: 768px) {
        :root { --glass-blur: blur(10px) saturate(150%); }
    }

    /* ========= MICRO-INTERACTIONS III ========= */

    .stTextInput input,
    .stTextArea textarea { text-transform: capitalize; }

    input[type="range"],
    input[type="checkbox"] { accent-color: var(--agri-green); }

    * { -webkit-tap-highlight-color: transparent; }

    [data-baseweb="tag"] {
        border-radius: 999px !important;
        background: var(--agri-green-light) !important;
        color: var(--agri-green-deep) !important;
        border: 1px solid #A7F3D0 !important;
        font-weight: 600;
    }
    [data-baseweb="tag"] span,
    [data-baseweb="tag"] svg { color: var(--agri-green-deep) !important; }
    [data-baseweb="tag"] button:hover { background: transparent !important; }

    .hint-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0.25rem 0 1rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.32rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid var(--agri-border);
        background: var(--agri-green-light);
        color: var(--agri-green-deep);
        animation: agriRise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    .chip.pinned { background: #FFFBEB; border-color: #FDE68A; color: #92400E; }

    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: var(--agri-lime) !important;
    }

    /* ========= MICRO-INTERACTIONS IV ========= */

    .crop-label {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0.2rem 0 0.4rem;
        font-family: var(--agri-font-heading);
        font-weight: 600;
        color: var(--agri-text);
        animation: agriRise 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    .crop-slot-index {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 26px;
        height: 26px;
        padding: 0 9px;
        border-radius: 999px;
        background: linear-gradient(135deg, var(--agri-green), var(--agri-lime));
        color: #FFFFFF;
        font-size: 0.76rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.32);
    }

    div[data-testid="stForm"]::after {
        content: "";
        position: absolute;
        inset: -1px;
        border-radius: 20px;
        padding: 1.5px;
        background: linear-gradient(135deg, var(--agri-green), var(--agri-lime), var(--agri-green));
        -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        -webkit-mask-composite: xor;
        mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        mask-composite: exclude;
        opacity: 0;
        transition: opacity 0.35s ease;
        pointer-events: none;
        z-index: 0;
    }
    div[data-testid="stForm"]:hover::after,
    div[data-testid="stForm"]:focus-within::after { opacity: 1; }

    strong { color: var(--agri-green-deep); }

    .stMarkdown li::marker { color: var(--agri-green); font-weight: 700; }

    .stButton > button {
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.28),
            0 8px 22px rgba(5, 150, 105, 0.26) !important;
    }

    .brand:hover .brand-mark {
        box-shadow: 0 0 0 6px rgba(52, 211, 153, 0.18);
        transition: box-shadow 0.3s ease;
    }

    div[data-testid="stExpander"] summary::marker,
    div[data-testid="stExpander"] summary::-webkit-details-marker {
        color: var(--agri-green);
    }

    div[data-baseweb="menu"] li,
    div[data-testid="stSelectboxVirtualDropdown"] li {
        border-radius: 8px;
        margin: 0 4px;
    }
    div[data-baseweb="menu"] li:hover,
    div[data-testid="stSelectboxVirtualDropdown"] li:hover {
        background: var(--agri-green-soft) !important;
    }

    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus {
        -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset;
        -webkit-text-fill-color: var(--agri-text);
        transition: background-color 9999s ease-in-out 0s;
    }

    div[data-testid="stFormSubmitButton"] button {
        min-height: 2.7rem;
        font-weight: 700;
    }

    [data-testid="stCaptionContainer"] strong,
    [data-testid="stCaptionContainer"] em { color: var(--agri-green-deep); }

    /* ========= MICRO-INTERACTIONS V ========= */

    ::selection {
        background: var(--agri-lime);
        color: var(--agri-green-deep);
    }

    .slot-hint {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0.55rem 1rem;
        border-radius: 12px;
        border: 1px dashed #A7F3D0;
        background: rgba(209, 250, 229, 0.55);
        color: var(--agri-green-deep);
        font-size: 0.82rem;
        font-weight: 600;
        animation: agriRise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    .slot-hint b {
        color: var(--agri-green);
        font-size: 1.02rem;
    }

    .stButton > button {
        transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1),
            box-shadow 0.25s ease,
            background-color 0.25s ease !important;
    }
    .stButton > button:not(:disabled):hover {
        transform: translateY(-1px);
    }
    .stButton > button:not(:disabled):active {
        transform: translateY(0) scale(0.97);
    }

    div[data-testid="stFormSubmitButton"] button:not(:disabled):hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 28px rgba(5, 150, 105, 0.34) !important;
    }
    div[data-testid="stFormSubmitButton"] button:focus-visible {
        box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.28) !important;
    }

    div[data-testid="stMetric"] {
        transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1),
            box-shadow 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 2px 0 0 var(--agri-lime), var(--glass-shadow) !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { letter-spacing: 0.3px; }
    [data-testid="stCaptionContainer"] { letter-spacing: 0.2px; }

    div[data-testid="stCodeBlock"] {
        background: rgba(255, 255, 255, 0.72) !important;
        backdrop-filter: blur(10px);
        border: 1px solid var(--agri-border);
        border-radius: 14px;
        overflow: hidden;
    }

    [data-testid="stWidgetLabel"] { font-weight: 600; color: var(--agri-text); }

    input, select, textarea { cursor: text; }
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] [role="radio"],
    [role="tab"] { cursor: pointer !important; }

    [role="tab"] svg { transition: transform 0.3s ease; }
    [role="tab"]:hover svg { transform: rotate(-8deg); }

    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] ,
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
    }

    .feature-icon { transition: transform 0.3s ease; }
    .feature-card:hover .feature-icon { transform: scale(1.12) rotate(-3deg); }

    .creators {
        margin-top: 1rem;
        padding: 1px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.6), rgba(6, 95, 70, 0.06) 48%, rgba(5, 150, 105, 0.45));
        box-shadow: 0 18px 40px -22px rgba(5, 150, 105, 0.45);
        animation: agriRise 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    .creators-inner {
        background: rgba(255, 255, 255, 0.85);
        -webkit-backdrop-filter: blur(14px);
        backdrop-filter: blur(14px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.65);
        padding: 0.9rem 1rem 1rem;
    }
    .creators-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: var(--agri-font-heading);
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        background: linear-gradient(120deg, var(--agri-green-deep), var(--agri-green));
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.6rem;
    }
    .creators-title::after {
        content: "";
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(6, 95, 70, 0.28), transparent);
    }
    .creators ul { list-style: none; margin: 0; padding: 0; }
    .creators li {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.18rem 0;
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--agri-muted);
        transition: color 0.2s ease, transform 0.2s ease;
    }
    .creators li:hover { color: var(--agri-green-deep); transform: translateX(2px); }
    .creators .avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: none;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #065f46, #10b981);
        color: #FFFFFF;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        box-shadow: 0 4px 12px -3px rgba(5, 150, 105, 0.55);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .creators li:hover .avatar {
        transform: scale(1.08);
        box-shadow: 0 6px 16px -4px rgba(5, 150, 105, 0.7);
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01s !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01s !important;
        }
    }

    .st-key-home_top {
        position: fixed;
        top: 0.85rem;
        right: 1.35rem;
        z-index: 1000000;
        width: auto !important;
    }
    .st-key-home_top button {
        width: auto !important;
        padding: 0.5rem 1.1rem !important;
        border-radius: 999px !important;
        background: rgba(255, 255, 255, 0.82) !important;
        color: var(--agri-green-deep) !important;
        border: 1px solid var(--agri-border) !important;
        font-weight: 700 !important;
        box-shadow: var(--glass-shadow) !important;
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
    }
    .st-key-home_top button:hover {
        background: #FFFFFF !important;
        border-color: var(--agri-green) !important;
        box-shadow: 0 10px 24px rgba(5, 150, 105, 0.22) !important;
        transform: translateY(-1px);
    }
    @media (max-width: 640px) {
        .st-key-home_top { top: 0.6rem; right: 0.75rem; }
    }

    .login-head {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 1rem 0 1.25rem;
        padding: 1.4rem 1.5rem;
        border-radius: 20px;
        border: 1px solid var(--glass-border);
        background: linear-gradient(135deg, #ECFDF5 0%, rgba(255, 255, 255, 0.65) 70%);
        box-shadow: var(--glass-shadow);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
    }
    .login-mark { font-size: 2.1rem; line-height: 1; }
    .login-brand {
        font-family: var(--agri-font-heading);
        font-weight: 700;
        font-size: 1.55rem;
        color: var(--agri-green-deep);
        letter-spacing: -0.02em;
    }
    .login-tag { color: var(--agri-muted); font-size: 0.9rem; }

    .whoami {
        margin: 0.35rem 0 0.6rem;
        padding: 0.55rem 0.75rem;
        border-radius: 12px;
        border: 1px solid var(--glass-border);
        background: var(--glass-bg);
        color: var(--agri-text);
        font-size: 0.85rem;
        line-height: 1.3;
    }
    .whoami-role {
        display: inline-block;
        margin-top: 4px;
        padding: 0.05rem 0.5rem;
        border-radius: 999px;
        background: var(--agri-green-light);
        color: var(--agri-green-deep);
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .st-key-logout button {
        background: transparent !important;
        color: #B91C1C !important;
        border: 1px solid rgba(185, 28, 28, 0.35) !important;
        box-shadow: none !important;
    }
    .st-key-logout button:hover {
        background: #FEF2F2 !important;
        border-color: #B91C1C !important;
        transform: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def page_header(eyebrow, title, subtitle=None):
    st.markdown(f'<div class="section-label">{eyebrow}</div>', unsafe_allow_html=True)
    st.header(title, anchor=False)
    if subtitle:
        st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)


def _go_home():
    st.session_state["nav"] = "🏠 Home"


def _go_to(target):
    st.session_state["nav"] = target


def _logout():
    st.session_state.pop("auth", None)
    st.session_state["nav"] = "🏠 Home"


def _skip_login():
    st.session_state["auth"] = {"role": "guest", "id": None, "name": "Guest"}
    st.session_state["nav"] = "🏠 Home"


AADHAAR_RE = re.compile(r"^[0-9]{12}$")


def _attempt_login(role, aadhaar):
    if not AADHAAR_RE.match((aadhaar or "").strip()):
        return False, "Enter a valid 12-digit Aadhaar number."
    if supabase is None:
        return False, "The database is not configured. Set SUPABASE_URL and SUPABASE_KEY."
    fn = "aadhaar_farmer_login" if role == "farmer" else "aadhaar_buyer_login"
    id_col = "farmer_id" if role == "farmer" else "buyer_id"
    try:
        rows = supabase.rpc(fn, {"p_aadhaar": aadhaar.strip()}).execute().data or []
    except Exception as e:
        _record_db_error(e)
        return False, "Could not reach the database. Please try again."
    if not rows:
        return False, "No account matches that Aadhaar. Please register first."
    row = rows[0]
    st.session_state["auth"] = {"role": role, "id": row.get(id_col), "name": row.get("name")}
    return True, None


def _register(role, aadhaar, fields):
    if not AADHAAR_RE.match((aadhaar or "").strip()):
        return False, "Enter a valid 12-digit Aadhaar number."
    if supabase is None:
        return False, "The database is not configured. Set SUPABASE_URL and SUPABASE_KEY."
    table = "farmers" if role == "farmer" else "buyers"
    id_col = "farmer_id" if role == "farmer" else "buyer_id"
    set_fn = "set_farmer_aadhaar" if role == "farmer" else "set_buyer_aadhaar"
    set_arg = "p_farmer_id" if role == "farmer" else "p_buyer_id"
    try:
        res = insert_row(table, fields)
        new_id = res.data[0].get(id_col) if res.data else None
        if new_id is None:
            return False, "Registration failed. Please try again."
        supabase.rpc(set_fn, {set_arg: new_id, "p_aadhaar": aadhaar.strip()}).execute()
    except Exception as e:
        _record_db_error(e)
        return False, f"Could not register: {e}"
    st.session_state["auth"] = {"role": role, "id": new_id, "name": fields.get("name")}
    return True, None


def render_login_page():
    _, mid, _ = st.columns([1, 1.25, 1])
    with mid:
        st.markdown(
            '<div class="login-head">'
            '<span class="login-mark">🌱</span>'
            "<div>"
            '<div class="login-brand">AgriConnect</div>'
            '<div class="login-tag">Sign in to buy &amp; sell produce</div>'
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        role_label = st.radio(
            "Account type",
            ["👨‍🌾 Farmer", "🛒 Buyer"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_role",
        )
        role = "farmer" if role_label.startswith("👨") else "buyer"

        mode = st.radio(
            "Mode",
            ["Log in", "Register"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode",
        )

        if mode == "Log in":
            with st.form(f"login_{role}"):
                aadhaar = st.text_input(
                    "Aadhaar number (12 digits)",
                    type="password",
                    max_chars=12,
                    placeholder="•••• •••• ••••",
                    key=f"login_aadhaar_{role}",
                )
                st.caption(
                    "Your Aadhaar is used only to sign in and is never shown or stored in plain text."
                )
                submitted = st.form_submit_button("Log in", icon=":material/login:")
                if submitted:
                    ok, msg = _attempt_login(role, aadhaar)
                    if ok:
                        st.session_state["nav"] = "🏠 Home"
                        st.rerun()
                    else:
                        st.error(msg, icon=":material/error:")
        else:
            with st.form(f"register_{role}"):
                if role == "farmer":
                    name = st.text_input("Full name*", placeholder="Enter your name", max_chars=100)
                    village = st.text_input("Village / area*", max_chars=100)
                    contact = st.text_input(
                        "Phone number*", max_chars=10, placeholder="10-digit mobile number"
                    )
                    crop = st.text_input("Primary crop", placeholder="e.g. Wheat", max_chars=40)
                else:
                    name = st.text_input(
                        "Business / name*", placeholder="Enter buyer or business name", max_chars=100
                    )
                    buyer_type = st.selectbox("Buyer type*", ["", "Retailer", "Wholesaler", "Consumer"])
                    location = st.text_input("Location / city*", max_chars=100)
                    contact = st.text_input(
                        "Phone number*", max_chars=10, placeholder="10-digit mobile number"
                                    aadhaar = st.text_input(
                    "Aadhaar number (12 digits)*",
                    type="password",
                    max_chars=12,
                    placeholder="•••• •••• ••••",
                )
                st.caption("Stored only as a one-way hash — never shown or saved in plain text.")
                submitted = st.form_submit_button("Create account", icon=":material/person_add:")

                if submitted:
                    errors = []
                    if not validate_not_empty(name):
                        errors.append("Name is required.")
                    if not validate_phone(contact):
                        errors.append("Phone must be 10 digits starting with 6–9.")
                    if role == "farmer" and not validate_not_empty(village):
                        errors.append("Village / area is required.")
                    if role == "buyer":
                        if not buyer_type:
                            errors.append("Please select a buyer type.")
                        if not validate_not_empty(location):
                            errors.append("Location is required.")
                    if not AADHAAR_RE.match((aadhaar or "").strip()):
                        errors.append("Aadhaar must be exactly 12 digits.")
                    if errors:
                        for err in errors:
                            st.error(err, icon=":material/error:")
                    else:
                        if role == "farmer":
                            fields = {
                                "name": title_case(name),
                                "village": title_case(village),
                                "contact": contact.strip(),
                                "primary_crop": title_case(crop) or None,
                            }
                        else:
                            fields = {
                                "name": title_case(name),
                                "buyer_type": buyer_type.strip().lower(),
                                "location": title_case(location),
                                "contact": contact.strip(),
                            }
                        ok, msg = _register(role, aadhaar, fields)
                        if ok:
                            st.session_state["nav"] = "🏠 Home"
                            st.rerun()
                        else:
                            st.error(msg, icon=":material/error:")

        if _DB_ERROR["message"]:
            st.warning(
                "Database unavailable — sign-in will not work until the connection is restored.\n\n"
                f"`{_DB_ERROR['message']}`",
                icon=":material/cloud_off:",
            )

        st.divider()
        st.button(
            "Skip — browse as guest",
            key="skip_login",
            on_click=_skip_login,
            icon=":material/visibility:",
            use_container_width=True,
        )
        st.caption(
            "View listings, reports and every page without an account. "
            "Signing in is only needed to buy or sell."
        )


if not st.session_state.get("auth"):
    render_login_page()
    st.stop()


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">🌱</div>
            <div>
                <div class="brand-name">AgriConnect</div>
                <div class="brand-tag">Farm-to-market marketplace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-label">Menu</div>', unsafe_allow_html=True)

    st.session_state.setdefault("nav", "🏠 Home")

    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "👨‍🌾 Add Farmer",
            "🛒 Add Buyer",
            "🌾 Add Listing",
            "📦 Place Order",
            "📋 Active Listings",
            "📊 Reports",
        ],
        key="nav",
        label_visibility="collapsed",
    )

    auth = st.session_state["auth"]
    if auth["role"] == "guest":
        st.markdown(
            '<div class="whoami">Browsing as <b>Guest</b>'
            '<span class="whoami-role">Guest</span></div>',
            unsafe_allow_html=True,
        )
        st.button(
            "Log in",
            key="guest_login",
            on_click=_logout,
            icon=":material/login:",
            use_container_width=True,
        )
    else:
        st.markdown(
            f'<div class="whoami">Signed in as <b>{html.escape(str(auth["name"]))}</b>'
            f'<span class="whoami-role">{auth["role"].title()}</span></div>',
            unsafe_allow_html=True,
        )
        st.button("Log out", key="logout", on_click=_logout, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="creators">
            <div class="creators-inner">
                <div class="creators-title">Creators</div>
                <ul>
                    <li><span class="avatar">JB</span><span>Joseph Boby</span></li>
                    <li><span class="avatar">KS</span><span>Kuriakose Sebastion</span></li>
                    <li><span class="avatar">SS</span><span>Sujith S</span></li>
                    <li><span class="avatar">NK</span><span>Niranjana S Kummar</span></li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.button("🏠 Home", key="home_top", on_click=_go_home, help="Go to the home page")

_db_banner = st.empty()


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

    st.markdown('<div class="section-label">📈 Platform Features</div>', unsafe_allow_html=True)
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

    st.space("small")

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

    st.space("medium")

    auth = st.session_state["auth"]
    if auth["role"] == "farmer":
        st.markdown('<div class="section-label">🏛️ Government schemes</div>', unsafe_allow_html=True)
        st.header("Subsidies & pensions", anchor=False)
        schemes = fetch_eq("schemes", "farmer_id", auth["id"], order_by="date_added")
        if schemes.empty:
            st.info(
                "No government schemes are on record for your account yet.",
                icon=":material/policy:",
            )
        else:
            if "eligible" in schemes.columns:
                eligible_n = int(schemes["eligible"].fillna(False).astype(bool).sum())
                s1, s2 = st.columns(2, gap="large")
                s1.metric("Schemes listed", f"{len(schemes):,}", icon=":material/policy:")
                s2.metric("You are eligible for", f"{eligible_n:,}", icon=":material/verified:")
            st.dataframe(
                schemes.rename(
                    columns={
                        "scheme_name": "Scheme",
                        "eligible": "Eligible",
                        "date_added": "Date added",
                    }
                ),
                width="stretch",
                hide_index=True,
            )
        st.space("small")

    col_info1, col_info2 = st.columns([1, 1], gap="large")
    with col_info1:
        st.info(
            "📌 **Getting Started**\n\nUse the navigation menu on the left to get started. "
            "Start by registering farmers and buyers, then create listings and place orders."
        )
    with col_info2:
        st.success(
            "✅ **Ready to go**\n\nYour marketplace is fully set up and ready to connect "
            "farmers with buyers. Create your first listing today!"
        )

    st.space("medium")
    st.markdown('<div class="section-label">🚀 Quick actions</div>', unsafe_allow_html=True)
    st.header("Open a page", anchor=False)
    st.caption("Jump straight to any part of the marketplace.")

    _quick_pages = [
        "👨‍🌾 Add Farmer",
        "🛒 Add Buyer",
        "🌾 Add Listing",
        "📦 Place Order",
        "📋 Active Listings",
        "📊 Reports",
    ]
    _qa_cols = st.columns(3, gap="medium")
    for _i, _target in enumerate(_quick_pages):
        with _qa_cols[_i % 3]:
            st.button(
                _target,
                key=f"qa_{_i}",
                on_click=_go_to,
                args=(_target,),
                use_container_width=True,
            )


elif page == "👨‍🌾 Add Farmer":

    page_header("Farmer management", "Register a farmer", "Add a farmer and their key details to the marketplace.")

    st.session_state.setdefault("farmer_crop_max", 2)

    with st.form("farmer_form", clear_on_submit=True):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            name = st.text_input(
                "Full name*",
                placeholder="Enter farmer name",
                max_chars=100,
                key="farmer_name",
            )
            st.caption("Letters and spaces only · auto-capitalized")
        with col2:
            village = st.text_input(
                "Village / area*",
                placeholder="Enter village or area",
                max_chars=100,
                key="farmer_village",
            )

        col3, col4 = st.columns(2, gap="large")
        with col3:
            contact = st.text_input("Phone number*", placeholder="10-digit mobile number", max_chars=10)
            st.caption("Format: 6–9 followed by 9 digits")

        st.markdown('<div class="section-label">🌾 Primary crops</div>', unsafe_allow_html=True)

        crop_opts, pinned_set, stock_set = ordered_crop_options()
        fmt = lambda c: crop_option_label(c, pinned_set, stock_set)

        crop_slots = []
        for i in range(st.session_state["farmer_crop_max"]):
            st.markdown(
                f'<div class="crop-label"><span class="crop-slot-index">{i + 1}</span>Crop {i + 1}</div>',
                unsafe_allow_html=True,
            )
            choice = st.selectbox(
                f"Crop {i + 1}",
                crop_opts,
                index=None,
                key=f"farmer_crop_{i}",
                format_func=fmt,
                placeholder="— Select crop —",
            )
            custom = ""
            if choice == ADD_NEW_CROP:
                custom = st.text_input(
                    f"New crop {i + 1} name*",
                    placeholder="e.g. Dragon fruit",
                    key=f"farmer_new_crop_{i}",
                )
            crop_slots.append((choice, custom))
            st.space("small")

        submitted = st.form_submit_button("Register farmer", icon=":material/person_add:")

        if submitted:
            errors = []
            if not validate_name(name):
                errors.append("Name must be at least 2 letters.")
            if not validate_not_empty(village):
                errors.append("Village / area is required.")
            if not validate_phone(contact):
                errors.append("Phone must be 10 digits starting with 6–9.")

            selected = []
            for i, (choice, custom) in enumerate(crop_slots):
                if choice == ADD_NEW_CROP:
                    if not validate_not_empty(custom):
                        errors.append(f"Crop {i + 1}: please enter the new crop name.")
                    else:
                        selected.append(ensure_crop(custom))
                elif choice:
                    selected.append(choice)

            selected = list(dict.fromkeys(selected))

            if not selected:
                errors.append("Select at least one primary crop.")

            primary_crop = ", ".join(selected)
            if selected and len(primary_crop) > 50:
                errors.append(
                    f"Too many or too-long crop names ({len(primary_crop)}/50 characters). "
                    "Choose fewer or shorter crops for the farmer profile."
                )

            if errors:
                for error in errors:
                    st.error(error, icon=":material/error:")
            else:
                try:
                    insert_row(
                        "farmers",
                        {
                            "name": title_case(name),
                            "village": title_case(village),
                            "contact": contact.strip(),
                            "primary_crop": primary_crop,
                        },
                    )
                    st.success(
                        f"Registered **{title_case(name)}** — growing {primary_crop}.",
                        icon=":material/check_circle:",
                    )
                    st.balloons()
                except Exception as e:
                    st.error(f"Database error: {e}", icon=":material/error:")

    st.space("small")

    add_crop_col, slot_hint_col = st.columns([1, 2], gap="large")
    with add_crop_col:
        st.button(
            "＋ Add another crop",
            key="add_farmer_crop",
            type="secondary",
            use_container_width=True,
            disabled=st.session_state["farmer_crop_max"] >= MAX_FARMER_CROPS,
            on_click=lambda: st.session_state.__setitem__("farmer_crop_max", st.session_state["farmer_crop_max"] + 1),
        )
    with slot_hint_col:
        st.markdown(
            f'<div class="slot-hint">🌾 Crop slots: <b>{st.session_state["farmer_crop_max"]}</b> / {MAX_FARMER_CROPS}'
            f" — fields keep their values when you add more.</div>",
            unsafe_allow_html=True,
        )


elif page == "🛒 Add Buyer":

    page_header("Buyer management", "Register a buyer", "Add a retailer, wholesaler or consumer to the marketplace.")

    with st.form("buyer_form", clear_on_submit=True):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            name = st.text_input(
                "Business / name*",
                placeholder="Enter buyer or business name",
                max_chars=100,
                key="buyer_name",
            )
        with col2:
            buyer_type = st.selectbox("Buyer type*", ["", "Retailer", "Wholesaler", "Consumer"])

        col3, col4 = st.columns(2, gap="large")
        with col3:
            location = st.text_input(
                "Location / city*",
                placeholder="Enter city or location",
                max_chars=100,
                key="buyer_location",
            )
        with col4:
            contact = st.text_input("Phone number*", placeholder="10-digit mobile number", max_chars=10)

        submitted = st.form_submit_button("Register buyer", icon=":material/person_add:")

        if submitted:
            errors = []
            if not validate_not_empty(name):
                errors.append("Buyer name is required.")
            if not buyer_type:
                errors.append("Please select a buyer type.")
            if not validate_not_empty(location):
                errors.append("Location is required.")
            if not validate_phone(contact):
                errors.append("Phone must be 10 digits starting with 6–9.")

            if errors:
                for error in errors:
                    st.error(error, icon=":material/error:")
            else:
                try:
                    insert_row(
                        "buyers",
                        {
                            "name": title_case(name),
                            "buyer_type": buyer_type.strip().lower(),
                            "location": title_case(location),
                            "contact": contact.strip(),
                        },
                    )
                    st.success(f"Registered **{title_case(name)}** as a {buyer_type.lower()}.", icon=":material/check_circle:")
                    st.balloons()
                except Exception as e:
                    st.error(f"Database error: {e}", icon=":material/error:")


elif page == "🌾 Add Listing":

    page_header("Marketplace", "List your produce", "Describe what is ready to sell with pricing and availability.")

    farmers = fetch_all("farmers", "farmer_id, name", order_by="name")

    if farmers.empty:
        st.info("No farmers yet. Register a farmer first to create a listing.", icon=":material/person_add:")

    else:
        render_crop_pinner()

        with st.form("listing_form", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="large")
            with col1:
                farmer = st.selectbox("Farmer*", farmers["name"])
            with col2:
                crop_opts, pinned_set, stock_set = ordered_crop_options()
                crop_choice = st.selectbox(
                    "Produce*",
                    crop_opts,
                    format_func=lambda c: crop_option_label(c, pinned_set, stock_set),
                )
                crop_custom = ""
                if crop_choice == ADD_NEW_CROP:
                    crop_custom = st.text_input(
                        "New produce name*",
                        placeholder="e.g. Dragon fruit",
                        key="listing_new_crop",
                    )

            col3, col4 = st.columns(2, gap="large")
            with col3:
                quantity = st.number_input("Quantity*", min_value=0.1, step=0.5, format="%.2f")
            with col4:
                unit = st.selectbox("Unit*", ["kg", "tons", "liters", "quintal", "bag", "box", "piece"])

            col5, col6 = st.columns(2, gap="large")
            with col5:
                price = st.number_input("Price per unit (₹)*", min_value=0.0, step=10.0, format="%.2f")
            with col6:
                harvest_date = st.date_input("Harvest date*")

            with st.container(border=True, key="agri_glass_a"):
                sum1, sum2 = st.columns(2, gap="large")
                sum1.metric("Estimated value", f"₹ {quantity * price:,.2f}")
                sum2.metric("Quantity", f"{quantity:g} {unit}")

            submitted = st.form_submit_button("Create listing", icon=":material/add_circle:")

            if submitted:
                errors = []
                crop_name = crop_custom if crop_choice == ADD_NEW_CROP else crop_choice
                if crop_choice == ADD_NEW_CROP and not validate_not_empty(crop_custom):
                    errors.append("Please enter the new produce name.")
                elif not validate_not_empty(crop_name):
                    errors.append("Produce name is required.")
                if quantity <= 0:
                    errors.append("Quantity must be greater than 0.")
                if price <= 0:
                    errors.append("Price must be greater than 0.")

                if errors:
                    for error in errors:
                        st.error(error, icon=":material/error:")
                else:
                    if crop_choice == ADD_NEW_CROP:
                        crop_name = ensure_crop(crop_custom)
                    try:
                        farmer_id = int(farmers.loc[farmers["name"] == farmer, "farmer_id"].iloc[0])
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
                            f"Listed **{crop_name}** ({quantity:g} {unit}) at ₹{price:,.2f}.",
                            icon=":material/check_circle:",
                        )
                        st.balloons()
                    except Exception as e:
                        st.error(f"Database error: {e}", icon=":material/error:")


elif page == "📦 Place Order":

    page_header("Orders", "Place an order", "Pick a buyer and an active listing to create an order.")

    buyers = fetch_all("buyers", "buyer_id, name", order_by="name")
    listings = fetch_all(
        "active_listings_view",
        "listing_id, farmer_name, crop_name, quantity, price_per_unit, unit",
        order_by="farmer_name",
    )

    if not listings.empty and "quantity" in listings.columns:
        listings["quantity"] = pd.to_numeric(listings["quantity"], errors="coerce")
        listings = listings[listings["quantity"] > 0].reset_index(drop=True)

    if buyers.empty or listings.empty:
        if buyers.empty:
            st.warning("No buyers registered yet. Add a buyer first.", icon=":material/person_add:")
        if listings.empty:
            st.warning("No active listings yet. Create a listing first.", icon=":material/add_circle:")
    else:
        pinned = [str(c).strip() for c in st.session_state.get("pinned_crops", [])]

        if pinned and not listings.empty:
            listings["_pinned"] = listings["crop_name"].isin(pinned).astype(int)
            listings = (
                listings.sort_values(["_pinned", "farmer_name"])
                .drop(columns="_pinned")
                .reset_index(drop=True)
            )

        def listing_label(row):
            mark = "📌 " if row["crop_name"] in pinned else ""
            return (
                mark
                + row["farmer_name"]
                + " — "
                + row["crop_name"]
                + " ("
                + str(row["quantity"])
                + " "
                + row["unit"]
                + " @ ₹"
                + str(row["price_per_unit"])
                + ")"
            )

        listings["label"] = listings.apply(listing_label, axis=1)

        with st.form("order_form", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="large")
            with col1:
                buyer = st.selectbox("Buyer*", buyers["name"])
                buyer_id = int(buyers.loc[buyers["name"] == buyer, "buyer_id"].iloc[0])
            with col2:
                listing_pick = st.selectbox("Listing*", listings["label"])
                listing_row = listings.loc[listings["label"] == listing_pick].iloc[0]
                listing_id = int(listing_row["listing_id"])

            col3, col4 = st.columns(2, gap="large")
            with col3:
                max_qty = float(listing_row["quantity"])
                qty = st.number_input(
                    "Quantity*",
                    min_value=min(0.1, max_qty),
                    max_value=max_qty,
                    step=0.5,
                    format="%.2f",
                )
                st.caption(f"Max {listing_row['quantity']} {listing_row['unit']}")
            with col4:
                total_price = qty * listing_row["price_per_unit"]
                st.metric("Order total", f"₹ {total_price:,.2f}")
                st.caption(f"@ ₹{listing_row['price_per_unit']}/unit")

            with st.container(border=True, key="agri_glass_b"):
                st.markdown(
                    f"""
                    **Order summary**

                    - Buyer: {buyer}
                    - Produce: {listing_row['crop_name']} from {listing_row['farmer_name']}
                    - Quantity: {qty:g} {listing_row['unit']}
                    - Total: ₹{total_price:,.2f}
                    """
                )

            submitted = st.form_submit_button("Place order", icon=":material/shopping_cart_checkout:")

            if submitted:
                errors = []
                if qty <= 0:
                    errors.append("Order quantity must be greater than 0.")
                if qty > float(listing_row["quantity"]):
                    errors.append(f"Insufficient stock. Maximum is {listing_row['quantity']} {listing_row['unit']}.")

                if errors:
                    for error in errors:
                        st.error(error, icon=":material/error:")
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
                        st.success(f"Order placed — ₹{total_price:,.2f}.", icon=":material/check_circle:")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Database error: {e}", icon=":material/error:")


elif page == "📋 Active Listings":

    page_header("Marketplace", "Active listings", "Browse everything currently available from farmers.")

    listings = fetch_all("active_listings_view", "*", order_by="harvest_date")

    if listings.empty:
        st.info("No active listings right now. Check back soon.", icon=":material/inventory_2:")
    else:
        pinned = [str(c).strip() for c in st.session_state.get("pinned_crops", [])]
        if pinned:
            listings["_pinned"] = listings["crop_name"].isin(pinned).astype(int)
            listings = (
                listings.sort_values(["_pinned", "harvest_date"], ascending=[False, True])
                .drop(columns="_pinned")
                .reset_index(drop=True)
            )

        total_qty = listings["quantity"].sum() if "quantity" in listings.columns else 0
        farmers_count = listings["farmer_name"].nunique() if "farmer_name" in listings.columns else 0

        stat1, stat2, stat3 = st.columns(3, gap="large")
        stat1.metric("Listings", f"{len(listings):,}", icon=":material/inventory_2:")
        stat2.metric("Total quantity", f"{total_qty:,.1f}", icon=":material/scale:")
        stat3.metric("Farmers", f"{farmers_count:,}", icon=":material/agriculture:")

        st.dataframe(
            listings,
            width="stretch",
            hide_index=True,
            column_config={
                "price_per_unit": st.column_config.NumberColumn(label="Price (₹)", format="₹%.2f"),
            },
        )


elif page == "📊 Reports":

    page_header("Analytics", "Reports", "Insights into revenue, buyers, pricing, ratings and payments.")

    report = st.selectbox(
        "Choose a report",
        [
            "📈 Revenue per farmer",
            "🏆 Most active buyers",
            "💹 Price trend",
            "📦 Unsold stock (15+ days)",
            "⭐ Average farmer rating",
            "💰 Pending payments",
        ],
    )

    st.space("small")

    if report == "📈 Revenue per farmer":

        farmers = fetch_all("farmers", "farmer_id, name", order_by="name")

        if farmers.empty:
            st.info("No farmers available.", icon=":material/agriculture:")
        else:
            farmer = st.selectbox("Select farmer", farmers["name"])
            farmer_id = int(farmers.loc[farmers["name"] == farmer, "farmer_id"].iloc[0])

            try:
                revenue_df = to_df(supabase.rpc("get_farmer_revenue", {"p_farmer_id": farmer_id}).execute().data)

                if revenue_df.empty:
                    st.info(f"{farmer} has no revenue yet.", icon=":material/payments:")
                else:
                    total = revenue_df["total_revenue"].sum() if "total_revenue" in revenue_df.columns else 0
                    rev1, rev2 = st.columns(2, gap="large")
                    rev1.metric("Total revenue (₹)", f"₹ {total:,.2f}", icon=":material/payments:")
                    rev2.metric("Transactions", f"{len(revenue_df):,}", icon=":material/receipt_long:")
                    st.dataframe(revenue_df, width="stretch", hide_index=True)
            except Exception as e:
                st.warning(f"Could not load revenue data: {e}", icon=":material/warning:")

    elif report == "🏆 Most active buyers":

        try:
            buyers_df = to_df(supabase.rpc("get_most_active_buyers").execute().data)

            if buyers_df.empty:
                st.info("No buyer activity yet.", icon=":material/storefront:")
            else:
                top_buyer = buyers_df.iloc[0]["name"] if len(buyers_df) > 0 else "—"
                avg_orders = buyers_df["total_orders"].mean() if "total_orders" in buyers_df.columns else 0

                buy1, buy2, buy3 = st.columns(3, gap="large")
                buy1.metric("Top buyer", top_buyer, icon=":material/emoji_events:")
                buy2.metric("Active buyers", f"{len(buyers_df):,}", icon=":material/groups:")
                buy3.metric("Avg orders / buyer", f"{avg_orders:.1f}", icon=":material/receipt_long:")
                st.dataframe(buyers_df, width="stretch", hide_index=True)
        except Exception as e:
            st.warning(f"Could not load buyer data: {e}", icon=":material/warning:")

    elif report == "💹 Price trend":

        crop = st.text_input("Crop name", value="Rubber Sheet", placeholder="e.g. Rice, Wheat, Rubber Sheet")

        try:
            price_data = fetch_eq("price_history", "crop_name", crop, "*", order_by="record_date")

            if price_data.empty:
                st.warning(f"No price history found for '{crop}'.", icon=":material/warning:")
            else:
                if "avg_market_price" in price_data.columns:
                    current_price = price_data.iloc[-1]["avg_market_price"]
                    min_price = price_data["avg_market_price"].min()
                    max_price = price_data["avg_market_price"].max()

                    p1, p2, p3 = st.columns(3, gap="large")
                    p1.metric("Current price (₹)", f"₹ {current_price:,.2f}", icon=":material/sell:")
                    p2.metric("Min price (₹)", f"₹ {min_price:,.2f}", icon=":material/trending_down:")
                    p3.metric("Max price (₹)", f"₹ {max_price:,.2f}", icon=":material/trending_up:")

                st.dataframe(price_data, width="stretch", hide_index=True)
        except Exception as e:
            st.warning(f"Could not load price data: {e}", icon=":material/warning:")

    elif report == "📦 Unsold stock (15+ days)":

        try:
            unsold = fetch_all("unsold_stock_view", "*", order_by="harvest_date")

            if unsold.empty:
                st.success("No old unsold stock found.", icon=":material/check_circle:")
            else:
                total_qty = unsold["quantity"].sum() if "quantity" in unsold.columns else 0
                u1, u2 = st.columns(2, gap="large")
                u1.metric("Unsold items", f"{len(unsold):,}", icon=":material/inventory:")
                u2.metric("Total quantity", f"{total_qty:,.1f}", icon=":material/scale:")
                st.warning("These items have been unsold for more than 15 days.", icon=":material/schedule:")
                st.dataframe(unsold, width="stretch", hide_index=True)
        except Exception as e:
            st.warning(f"Could not load unsold stock data: {e}", icon=":material/warning:")

    elif report == "⭐ Average farmer rating":

        try:
            rating_df = to_df(supabase.rpc("get_farmer_ratings").execute().data)

            if rating_df.empty:
                st.info("No ratings available yet.", icon=":material/star:")
            else:
                if "avg_rating" in rating_df.columns:
                    top_rating = rating_df.iloc[0]["avg_rating"] if len(rating_df) > 0 else 0
                    overall = rating_df["avg_rating"].mean()
                    r1, r2 = st.columns(2, gap="large")
                    r1.metric("Highest rating", f"⭐ {top_rating:.2f}", icon=":material/star:")
                    r2.metric("Average rating", f"⭐ {overall:.2f}", icon=":material/star_half:")
                st.dataframe(rating_df, width="stretch", hide_index=True)
        except Exception as e:
            st.warning(f"Could not load rating data: {e}", icon=":material/warning:")

    elif report == "💰 Pending payments":

        try:
            payments = fetch_all("pending_payments_view", "*")

            if payments.empty:
                st.success("No pending payments.", icon=":material/check_circle:")
            else:
                total_pending = payments["amount"].sum() if "amount" in payments.columns else 0
                pay1, pay2 = st.columns(2, gap="large")
                pay1.metric("Pending payments", f"{len(payments):,}", icon=":material/pending_actions:")
                pay2.metric("Total amount (₹)", f"₹ {total_pending:,.2f}", icon=":material/account_balance_wallet:")
                st.warning(f"{len(payments)} payment(s) pending collection.", icon=":material/schedule:")
                st.dataframe(payments, width="stretch", hide_index=True)
        except Exception as e:
            st.warning(f"Could not load payment data: {e}", icon=":material/warning:")


if _DB_ERROR["message"]:
    _db_banner.error(
        "**Database unavailable** — the app could not reach Supabase, so lists and "
        "reports below may appear empty. Check your network connection and that the "
        "Supabase project is online.\n\n"
        f"`{_DB_ERROR['message']}`",
        icon=":material/cloud_off:",
    )
