# AgriConnect Presentation Handoff

Last updated: 2026-10-27

## 1. Goal

- Rebuild the AgriConnect DBMS presentation as an 18-slide, 16:9 deck.
- Keep the current green/black SJCET visual style.
- Use points only; no paragraphs.
- Target 13–14 minutes presenting + 2–3 minutes Q&A.
- Split delivery across 3 presenters.

## 2. Source Files

- `~/Downloads/DBMS Project Presentation.pdf` — current 18-page deck; reuse layout and screenshots.
- `~/Downloads/AgriConnect_DBMS_Report.docx` — authoritative content and terminology.
- `~/Downloads/AgriConnect_PO_PSO_Tables.docx` — PO/PSO wording and mapping.
- `~/ProjectServers/agriconnect/schema.sql` — exact table, view, function and trigger names.
- `~/Projects/agriconnect/agriconnect_handoff.md` — **do not use for stack/testing**; it still describes the older Streamlit version.

## 3. Hard Constraints

- Every content slide must be in bullet points.
- Maximum 5–6 bullets per slide.
- Maximum 10–12 words per bullet.
- No paragraphs.
- No full-sentence blocks.
- One idea per bullet.
- Tables and diagrams are allowed.
- Put detailed explanation in speaker notes, not on slides.
- Use British spelling to match the report: `normalisation`, `behaviour`.
- Use `Electronics & Computer Engineering`, not `electronics and computer`.
- Add slide numbers.
- Keep the SJCET header and footer.
- Minimum body text size: 20 pt.
- Remove the blank final slide and replace it with useful content.

## 4. Design Direction

- Format: 16:9, 1440 × 810.
- Theme: dark green, emerald and black.
- Accent green: `#166534`.
- Headings: Space Grotesk.
- Body: Inter.
- Keep translucent glass cards and soft green shadows.
- Use one screenshot on the implementation slide.
- Use one ER diagram on the ER slide.
- Use one compact table on the database-design slide.
- Do not add new colours or decorative clutter.

## 5. Final Slide Order

1. Title
2. Contents
3. Abstract
4. Introduction
5. Problem Statement
6. Objectives
7. Literature Survey
8. ER Diagram
9. Technology Stack + Architecture
10. Implementation & Interface
11. Modules & Features
12. Database Design Highlights
13. UI Design
14. Testing & Results
15. Conclusion & Future Scope
16. SDGs
17. PO/PSO Mapping
18. References

## 6. Slide-by-Slide Build Sheet

### Slide 1 — Title

- `AGRICONNECT`
- `Marketplace and Crop Advisor`
- `DBMS Mini Project`
- Joseph Boby — SJC24ECE046
- Kuriakose Sebastian — SJC24ECE049
- Niranjana S Kumar — SJC24ECE055
- Sujith S — SJC24ECE066
- Department of Electronics & Computer Engineering, SJCET Palai
- October 2026

Do not use `Sebastion`.

### Slide 2 — Contents

- Introduction & Problem Statement
- Objectives & Literature Survey
- System Design & Architecture
- Implementation & Features
- Testing & Results
- SDGs, POs/PSOs & Conclusion

### Slide 3 — Abstract

- Web marketplace connecting farmers directly with buyers
- PostgreSQL/Supabase database with 10 tables
- Trigger updates stock and marks listings sold out
- Buyers search, filter and place orders
- Rule-based Crop Advisor; Aadhaar stored as salted SHA-256
- 10 views and 9 stored functions power reports

### Slide 4 — Introduction

- Direct marketplace reduces dependence on intermediaries
- Farmers list produce and manage stock and orders
- Buyers browse, filter and place orders
- Next.js frontend, FastAPI backend, Supabase PostgreSQL

### Slide 5 — Problem Statement

- Farmers depend on intermediaries and lose margin
- Prices and demand are scattered across informal channels
- Orders and payments are tracked manually
- Buyers cannot compare produce reliably
- Sales and inventory reporting is slow

### Slide 6 — Objectives

- Build a direct farmer-to-buyer marketplace
- Enable listing, discovery and ordering in one platform
- Track every order through a status timeline
- Recommend crops from soil, weather and season inputs
- Surface relevant government schemes
- Generate sales, buyer, inventory and low-stock reports

### Slide 7 — Literature Survey

- eNAM: unified market; complex for small farmers
- ONDC: digital commerce; limited advisory integration
- Existing marketplaces: general e-commerce, weak agri workflows
- Gap: simple role-based platform combining trade, advisory and schemes

Add official eNAM and ONDC sources in references.

### Slide 8 — ER Diagram

- Diagram: use report ER figure
- 10 entities and 7 relationships
- Core chain: farmers → listings → orders → payments
- Support entities: buyers, ratings, schemes, crops, price history, order status history

### Slide 9 — Technology Stack + Architecture

- Frontend: Next.js 16, React 19, TypeScript
- Backend: FastAPI, Uvicorn, Python 3.13
- Database: Supabase PostgreSQL
- Auth: Aadhaar login via RPC; farmer and buyer roles
- Hosting: NAS plus secure tunnel

Verify the actual tunnel name before writing `Cloudflare` or `Tailscale`.

### Slide 10 — Implementation & Interface

- Use current dashboard screenshot
- Farmer dashboard with live counts
- Active listings with search and filters
- Order placement and status tracking
- Rule-based Crop Advisor and scheme explorer
- Reports and profit calculator

Remove `AI-powered`.

### Slide 11 — Modules & Features

- Marketplace: listings, search, filters and CSV export
- Orders: placement, tracking, status timeline and cancellation
- Crop Advisor: soil, weather and season inputs
- Farmer tools: profit calculator, schemes and reports
- Auth: Aadhaar demo login; farmer, buyer and guest roles

### Slide 12 — Database Design Highlights

Use a 3-column table.

- Tables: `farmers`, `buyers`, `listings`, `orders`, `payments`, `ratings`, `schemes`, `price_history`, `crops`, `order_status_history`
- Views: `active_listings_view`, `order_history_view`, `order_status_audit_view`, `inventory_view`, `low_stock_view`, `monthly_sales_summary_view`, `most_active_buyers_view`, `farmer_avg_rating_view`, `unsold_stock_view`, `pending_payments_view`
- Functions: `recommend_crops`, `update_order_status`, `get_farmer_revenue`, `get_most_active_buyers`, `get_farmer_ratings`, `aadhaar_farmer_login`, `aadhaar_buyer_login`, `set_farmer_aadhaar`, `set_buyer_aadhaar`

Add bullets:

- Trigger `after_order_insert` reduces stock and marks sold out
- `update_order_status()` enforces valid transitions

Do not write `order_status_h istory`.

### Slide 13 — UI Design

- Emerald glassmorphism; Space Grotesk and Inter
- Fixed top dock and floating bottom navigation
- Translucent cards, gradient accents and soft shadows
- Responsive at 320, 360 and 390 px
- Verified with Playwright for layout and console errors

### Slide 14 — Testing & Results

- 43 functional test cases; all passed
- Role access tested for farmer, buyer and guest
- Order lifecycle: pending → confirmed → delivered → paid
- Stock trigger and low-stock checks passed
- Aadhaar validation and negative cases passed
- Playwright checks at 320, 360 and 390 px

Remove all Streamlit references.

### Slide 15 — Conclusion & Future Scope

- Direct marketplace improves price transparency
- One platform for trade, advisory, schemes and reports
- Current scope: rule-based advice and tracked payments only
- Future: multilingual support and mobile app
- Future: UPI/Razorpay, notifications and logistics
- Future: ML-based price prediction

### Slide 16 — SDGs

- SDG 2: direct market access and better farmer income
- SDG 8: digital entrepreneurship and revenue tracking
- SDG 9: low-cost digital marketplace infrastructure
- SDG 10: reduces information asymmetry
- Supporting: SDG 1, 12 and 13

Use title `AGRICONNECT AND THE SDGs`.

Do not use `SDG'S`.

### Slide 17 — PO/PSO Mapping

- PO1, PO2, PO3: engineering knowledge, problem analysis, solution design
- PO5, PO6: modern tools and societal impact
- PO8: ethics, access control and Aadhaar privacy
- PSO1: analyse and design database-backed systems
- PSO2: use modern tools to design and communicate

Use the detailed table in `AgriConnect_PO_PSO_Tables.docx` if the rubric requires full mapping.

### Slide 18 — References

- Next.js, React and FastAPI documentation
- PostgreSQL, Supabase and Playwright documentation
- eNAM and ONDC official sources
- Department of Agriculture & Farmers Welfare
- Open-Meteo and Nominatim

Remove Streamlit documentation.

## 7. Three-Person Split

### Person 1 — Slides 1–7, about 4 minutes

- Title and team
- Contents
- Abstract
- Introduction
- Problem statement
- Objectives
- Literature survey
- Handoff: “Next, the system design and database.”

### Person 2 — Slides 8–13, about 5 minutes

- ER diagram
- Technology stack and architecture
- Implementation and interface
- Modules and features
- Database design highlights
- UI design
- Handoff: “Next, testing, results and impact.”

### Person 3 — Slides 14–18, about 4 minutes

- Testing and results
- Conclusion and future scope
- SDGs
- PO/PSO mapping
- References
- Close with the impact statement

## 8. Q&A Ownership

- Person 1: problem, objectives, users and scope.
- Person 2: schema, SQL, triggers, functions, architecture and security.
- Person 3: testing, SDGs, PO/PSO mapping and future scope.

## 9. Fact Bank

### Database

- 10 tables.
- 10 views.
- 9 stored functions.
- 1 trigger: `after_order_insert`.
- 1 trigger function: `update_listing_after_order()`.
- 7 foreign-key relationships.
- Aadhaar stored as salted SHA-256 hash.
- Raw Aadhaar never stored or returned.
- Payments tracked only; no payment gateway.

### Order Lifecycle

- `pending → confirmed`
- `pending → cancelled`
- `confirmed → delivered`
- `confirmed → cancelled`
- `delivered → paid`
- Every change recorded in `order_status_history`.

### Test Results

- 43 test cases.
- All passed on the deployed build.
- Browser checks with Playwright at 320, 360 and 390 px.
- Negative tests: invalid Aadhaar, over-ordering, illegal status jumps.

### Crop Advisor

- Rule-based, deterministic scoring function.
- Inputs: pH, moisture, N, P, K, temperature, season.
- Weather support: Open-Meteo.
- Geocoding: Nominatim.
- Returns crops matching at least four parameters.
- Includes match percentage, revenue and market outlook.

### Stack

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- FastAPI
- Python 3.13
- Uvicorn
- Supabase PostgreSQL
- supabase-py
- Open-Meteo
- Nominatim
- fpdf2
- pandas
- Playwright
- Git and GitHub

## 10. Do Not Say

- Do not say `AI-powered Crop Advisor`.
- Do not say `machine-learning Crop Advisor`.
- Do not say `Streamlit`.
- Do not say `Streamlit AppTest`.
- Do not say `stored procedures`; use `stored functions` or `RPCs`.
- Do not say `removes middlemen`; use `reduces dependence on intermediaries`.
- Do not say `Cloudflare Tunnel` unless verified.
- Do not say `SDG'S`.
- Do not write `Sebastion`.
- Do not claim payments are processed.
- Do not claim real-time mandi prices.
- Do not claim full RLS enforcement unless verified.

## 11. References

- Next.js: https://nextjs.org/docs
- React: https://react.dev
- FastAPI: https://fastapi.tiangolo.com
- PostgreSQL: https://www.postgresql.org/docs
- Supabase: https://supabase.com/docs
- Playwright: https://playwright.dev/docs
- eNAM: https://enam.gov.in
- ONDC: https://ondc.org
- Department of Agriculture & Farmers Welfare: https://agricoop.nic.in
- Open-Meteo: https://open-meteo.com
- Nominatim: https://nominatim.org

## 12. Build Order

1. Duplicate the current deck.
2. Delete the blank slide.
3. Add PO/PSO slide before references.
4. Convert slides 3, 4 and 10 to bullets.
5. Cut slides 7, 11, 14, 15 and 16 to 5–6 bullets.
6. Fix stack, testing, spelling and terminology errors.
7. Add speaker notes from the report.
8. Export PDF.
9. Verify all 18 slides and all references.

## 13. Final Checks

- No paragraph text.
- No slide over 6 bullets.
- No bullet over 12 words.
- No Streamlit text.
- No `AI-powered` text.
- No `stored procedures` text.
- No blank slide.
- Correct names and registration numbers.
- Correct order lifecycle.
- Correct test count: 43.
- Correct database count: 10 tables, 10 views, 9 functions, 1 trigger.
- Correct PO/PSO wording.
- Correct SDG wording.
- References match the content.
