# AgriConnect — Report Handoff (Fact Sheet for Documentation AI)

Source of truth: `schema.sql` (Supabase/PostgreSQL) and `app.py` (Streamlit UI). Everything below is verified against those files. Use these exact terms — do not invent features.

---

# 1. Stack

- **Frontend/UI**: Streamlit (Python), single-file `app.py`.
- **Backend/DB**: Supabase (hosted PostgreSQL), accessed via the `supabase` Python client using the **anon/publishable key**.
- **Other libraries**: pandas (data), fpdf2 (PDF export), python-dotenv.
- **Hosting**: NAS (Tailscale Funnel) — runs the Streamlit server; DB stays on Supabase cloud.

---

# 2. Domain Model (tables — exact names)

`farmers`, `buyers`, `listings`, `orders`, `payments`, `ratings`, `schemes`, `price_history`, `crops`, `order_status_history`.

Key columns:

- **listings**: `crop_name, quantity, unit (default 'kg'), price_per_unit, harvest_date, status ('available' | 'sold_out')`.
- **orders**: `buyer_id, listing_id, quantity_ordered, order_date, status ('pending','confirmed','delivered','cancelled','paid')`.
- **payments**: `order_id, amount, status ('pending'|'paid'), payment_date` — payments are **tracked only; there is NO payment gateway**.
- **farmers / buyers**: each has `aadhaar_hash` — a **salted SHA-256 hash**; the raw Aadhaar is **never stored or returned**.
- **crops**: agronomy knowledge base (`seasons[]`, pH/moisture/N/P/K/temp ranges, `revenue_min`, `revenue_max`, `market_outlook`).

---

# 3. Views (exact names)

`active_listings_view`, `most_active_buyers_view`, `unsold_stock_view`, `farmer_avg_rating_view`, `pending_payments_view`, `inventory_view`, `low_stock_view`, `monthly_sales_summary_view`, `order_history_view`, `order_status_audit_view`.

---

# 4. RPC Functions (exact names)

`recommend_crops`, `update_order_status`, `get_farmer_revenue`, `get_most_active_buyers`, `get_farmer_ratings`, `aadhaar_farmer_login`, `aadhaar_buyer_login`, `set_farmer_aadhaar`, `set_buyer_aadhaar`.

---

# 5. Key Logic (state precisely)

- **Automated stock update**: DB trigger `after_order_insert` → function `update_listing_after_order()`: on every order insert, decrements `listings.quantity` by `quantity_ordered`; sets `status='sold_out'` when quantity ≤ 0. This is **automatic and server-side**.
- **Order lifecycle validation**: `update_order_status()` enforces allowed transitions — `pending→confirmed|cancelled`, `confirmed→delivered|cancelled`, `delivered→paid`. Every change is written to `order_status_history` (audit trail with `changed_by`, `changed_at`).
- **Crop Advisor**: calls `recommend_crops(ph, moisture, n, p, k, temp, season)`. Scores each crop in the `crops` table against **6 parameters** (pH, moisture, N, P, K, temperature), returns crops matching ≥ 4 parameters, ranked, with `match_pct`, `revenue`, `market_outlook`. It is **soil AND weather based**, not soil-only. It also has a **live weather fetch** (Open-Meteo / Nominatim geocoding).
- **Aadhaar auth**: login hashes the input and compares to the stored hash via `aadhaar_*_login` RPCs. Role is auto-detected (farmer then buyer). No raw number is logged or displayed anywhere.

---

# 6. Roles and Access (the app enforces this in the UI)

- **Guest**: can view Home, Active Listings, Reports, Profit Calculator, Scheme Explorer, Crop Advisor. Cannot buy or sell.
- **Farmer**: adds/edits own listings, sees own listings + incoming orders, advances order status, sees own schemes.
- **Buyer**: browses, searches/filters listings, places orders, sees own orders.
- Browse/search/filter on **Active Listings**: text search (crop/farmer/village), **Crop** select, **Village** select, **price-per-unit range slider**. Two views: **Cards** (product grid) and **Table**, plus **CSV export**.
- Note: row-level scoping is done in the UI/queries (views), because the app uses the anon key — **do not claim RLS restricts data** unless it says so.

---

# 7. Features That Exist (and are often missed)

- Profit & **yield calculator**.
- **Live weather** integration.
- **CSV export** of listings/reports and **PDF export** (fpdf2).
- **Guest browsing** mode.
- **Order tracker** with a **horizontal status timeline** (Flipkart-style) and per-order audit ("changed by"/date).
- **Market watch** — per-crop price cards on Home from `price_history`.

---

# 8. Do NOT Claim (common errors)

- No online payment processing / gateway.
- No real-time chat, notifications, or messaging.
- No ML/AI model — the Crop Advisor is **rule/scoring-based** over a predefined knowledge base.
- No mobile app — it is a **web app**.
- No admin dashboard role.
- Do not claim the DB is movable/self-hosted; it is Supabase cloud.

---

# 9. Suggested Mapping to Report Sections

- **Objectives** → direct farmer-buyer trade, automated stock/order handling, data-driven crop guidance, transparency via price history/ratings.
- **Proposed System** → three roles (guest/farmer/buyer), trigger-based stock, validated order lifecycle, RPC-driven advisor & auth.
- **Database Design** → 10 tables, 10 views, 9 RPCs (use exact names above); ER diagram from the FK relations below.
- **Testing** → cover: auth (valid/invalid Aadhaar, role auto-detect), stock decrement + sold-out, invalid order transitions, advisor scoring, guest access limits.
- **Future Enhancements** → online payments, notifications, ratings from real orders, mobile app, real market-price feeds (currently `price_history` is seeded data).

---

# 10. Entity-Relationship (derived from FKs in `schema.sql`)

| Parent | Child | FK column | Cardinality | Notes |
|---|---|---|---|---|
| farmers | listings | listings.farmer_id | 1 : N | a farmer has many listings |
| farmers | schemes | schemes.farmer_id | 1 : N | a farmer may have many scheme records |
| buyers | orders | orders.buyer_id | 1 : N | a buyer places many orders |
| listings | orders | orders.listing_id | 1 : N | a listing can be ordered many times |
| orders | payments | payments.order_id | 1 : N | an order can have payment records |
| orders | ratings | ratings.order_id | 1 : N | a rating is tied to an order |
| orders | order_status_history | order_status_history.order_id | 1 : N | audit trail; ON DELETE CASCADE |

Standalone / reference tables (no FK out): `crops` (knowledge base), `price_history` (market prices).

Indirect relations (via views, not FKs):

- farmers ← listings ← orders ← ratings → `farmer_avg_rating_view` (average score per farmer).
- farmers ← listings ← orders ← payments → `get_farmer_revenue` (paid revenue per farmer).

**PK naming:** every table uses `<entity>_id` (e.g. `farmer_id`, `listing_id`, `order_id`, `history_id`).

**Attributes to show per table in the ER diagram:**

- **farmers**: farmer_id (PK), name, village, contact, primary_crop, user_id, aadhaar_hash.
- **buyers**: buyer_id (PK), name, buyer_type (retailer/wholesaler/consumer), location, contact, user_id, aadhaar_hash.
- **listings**: listing_id (PK), farmer_id (FK), crop_name, quantity, unit, price_per_unit, harvest_date, status.
- **orders**: order_id (PK), buyer_id (FK), listing_id (FK), quantity_ordered, order_date, status.
- **payments**: payment_id (PK), order_id (FK), amount, status, payment_date.
- **ratings**: rating_id (PK), order_id (FK), score (1–5), comment.
- **schemes**: scheme_id (PK), farmer_id (FK), scheme_name, eligible, date_added.
- **price_history**: price_id (PK), crop_name, record_date, avg_market_price.
- **crops**: crop_id (PK), name, seasons[], ph_min/max, moisture_min/max, n/p/k_min/max, temp_min/max, revenue_min, revenue_max, market_outlook.
- **order_status_history**: history_id (PK), order_id (FK), old_status, new_status, changed_by, changed_at.

---

# 11. Test Cases

## A. Authentication & Access

| ID | Test | Input | Expected |
|---|---|---|---|
| A1 | Farmer login (valid) | Registered farmer Aadhaar (12 digits) | Logs in, role = farmer, name shown |
| A2 | Buyer login (valid) | Registered buyer Aadhaar | Logs in, role = buyer |
| A3 | Role auto-detect | Aadhaar in DB | Correct role resolved without picking role |
| A4 | Invalid Aadhaar format | < 12 digits / non-numeric | "Enter a valid 12-digit Aadhaar number." |
| A5 | Unknown Aadhaar | 12 digits not in DB | "No account matches that Aadhaar. Please register first." |
| A6 | Guest access | "Skip — browse as guest" | Views listings/reports/tools; no buy/sell |
| A7 | Raw Aadhaar never shown/logged | Any login | No raw number in UI or logs |
| A8 | Session persistence | Reload page after login | Still logged in (localStorage restore, re-validated against DB) |

## B. Listings & Marketplace

| ID | Test | Input | Expected |
|---|---|---|---|
| B1 | Add listing (farmer) | Crop, qty, unit, price | Listing appears in Active Listings |
| B2 | Non-farmer add | Guest/buyer opens add | Blocked/disabled |
| B3 | Search | "Rice" | Only matching crop/farmer/village |
| B4 | Filter by crop | Crop = Tomato | Only Tomato listings |
| B5 | Filter by village | Village = X | Only village X listings |
| B6 | Price range | Slider lo–hi | Only listings within range |
| B7 | Card view | Default | Product cards with ₹price/unit |
| B8 | Table view | Toggle "Table" | Dataframe with formatted price |
| B9 | CSV export | Click export | File `active_listings.csv` downloads |

## C. Orders & Stock

| ID | Test | Input | Expected |
|---|---|---|---|
| C1 | Place order (buyer) | Listing + valid qty | Order row created |
| C2 | Auto stock decrement | Place order qty N | `listings.quantity` reduced by N (trigger) |
| C3 | Auto sold-out | Order reduces qty to ≤ 0 | `status = 'sold_out'` |
| C4 | Insufficient stock | Qty > available | Error: "Insufficient stock…" |
| C5 | Zero/negative qty | Qty ≤ 0 | Error: "must be greater than 0" |
| C6 | Correct total | Qty × price | Total matches live calculation |
| C7 | Valid transition | pending→confirmed | Status updated + history row |
| C8 | Invalid transition | pending→delivered | DB raises "Invalid status transition" |
| C9 | Audit trail | Any status change | Row in `order_status_history` with changed_by/date |
| C10 | Buyer sees own orders only | Two buyers | Each sees only their orders |
| C11 | Farmer sees own-listing orders | Farmer login | Orders on their listings only |

## D. Crop Advisor

| ID | Test | Input | Expected |
|---|---|---|---|
| D1 | Recommendation | pH, moisture, N,P,K, temp, season | Crops matching ≥ 4 params, ranked |
| D2 | Match percentage | Same inputs | `match_pct` = (matched/6)×100 |
| D3 | Season filter | Season = Kharif | Only crops with that season |
| D4 | Empty result | Poorly matched inputs | "no suitable crops"/empty handled |
| D5 | Revenue + outlook | Valid crop | Shows revenue range + market outlook |
| D6 | Live weather | Enter place | Weather card populates |

## E. Reports & Tools

| ID | Test | Input | Expected |
|---|---|---|---|
| E1 | Revenue per farmer | Select report | Sums paid payments per farmer |
| E2 | Most active buyers | Select report | Ranked by total volume |
| E3 | Price trend | Crop name | Current/min/max + line chart |
| E4 | Unsold stock 15+ days | Select report | Listings where harvest_date < today−15 |
| E5 | Avg farmer rating | Select report | Average score per farmer |
| E6 | Pending payments | Select report | Payments with status = 'pending' |
| E7 | Profit calculator | Cost/price/yield inputs | Computed profit/yield |
| E8 | Scheme eligibility | Land/livestock/organic/income | Indicative scheme matches |
| E9 | PDF export | Export report | PDF generated (fpdf2) |

---

# 12. Testing Methodology Note (for section 11.1)

Describe: **unit-ish verification of DB logic** (trigger, transitions, RPC outputs), **page-level functional testing** across the three roles (guest/farmer/buyer), **negative testing** (invalid Aadhaar, over-ordering, illegal status jumps), and **UI/state testing** (session persistence, filters, view toggles). If the rubric wants a formal framework, state that testing was done via scripted functional walkthroughs plus Streamlit's built-in `AppTest` harness for page-level run checks.
