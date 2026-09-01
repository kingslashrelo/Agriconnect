-- AgriConnect schema for Supabase
-- Run this whole file in the Supabase SQL Editor (Dashboard -> SQL Editor -> New query -> paste -> Run).
-- This replaces the old Neon schema. It creates the tables, the quantity trigger,
-- the reporting views, and the revenue function used by the app.

-- ============ TABLES ============

CREATE TABLE farmers (
    farmer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    village VARCHAR(100),
    contact VARCHAR(15),
    primary_crop VARCHAR(50)
);

CREATE TABLE buyers (
    buyer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    buyer_type VARCHAR(20) NOT NULL CHECK (buyer_type IN ('retailer','wholesaler','consumer')),
    location VARCHAR(100),
    contact VARCHAR(15)
);

CREATE TABLE listings (
    listing_id SERIAL PRIMARY KEY,
    farmer_id INT REFERENCES farmers(farmer_id),
    crop_name VARCHAR(50) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL CHECK (quantity >= 0),
    unit VARCHAR(10) DEFAULT 'kg',
    price_per_unit DECIMAL(10,2) NOT NULL,
    harvest_date DATE,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available','sold_out'))
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    buyer_id INT REFERENCES buyers(buyer_id),
    listing_id INT REFERENCES listings(listing_id),
    quantity_ordered DECIMAL(10,2) NOT NULL,
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','confirmed','delivered','cancelled','paid'))
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','paid')),
    payment_date DATE
);

CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    score INT CHECK (score BETWEEN 1 AND 5),
    comment VARCHAR(255)
);

CREATE TABLE schemes (
    scheme_id SERIAL PRIMARY KEY,
    farmer_id INT REFERENCES farmers(farmer_id),
    scheme_name VARCHAR(100),
    eligible BOOLEAN DEFAULT FALSE,
    date_added DATE DEFAULT CURRENT_DATE
);

CREATE TABLE price_history (
    price_id SERIAL PRIMARY KEY,
    crop_name VARCHAR(50) NOT NULL,
    record_date DATE NOT NULL,
    avg_market_price DECIMAL(10,2) NOT NULL
);

-- ============ TRIGGER ============

-- Trigger: decrement listing quantity on order, auto-flag sold out
CREATE OR REPLACE FUNCTION update_listing_after_order()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE listings
    SET quantity = quantity - NEW.quantity_ordered
    WHERE listing_id = NEW.listing_id;

    UPDATE listings
    SET status = 'sold_out'
    WHERE listing_id = NEW.listing_id AND quantity <= 0;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_order_insert
AFTER INSERT ON orders
FOR EACH ROW
EXECUTE FUNCTION update_listing_after_order();

-- ============ VIEWS ============

-- Active listings with farmer details
CREATE OR REPLACE VIEW active_listings_view AS
SELECT l.listing_id, f.name AS farmer_name, f.village,
       l.crop_name, l.quantity, l.unit, l.price_per_unit, l.harvest_date
FROM listings l
JOIN farmers f ON l.farmer_id = f.farmer_id
WHERE l.status = 'available';

-- Report: most active buyers
CREATE OR REPLACE VIEW most_active_buyers_view AS
SELECT b.name, COUNT(o.order_id) AS total_orders, SUM(o.quantity_ordered) AS total_volume
FROM buyers b
JOIN orders o ON b.buyer_id = o.buyer_id
GROUP BY b.name
ORDER BY total_volume DESC;

-- Report: unsold stock sitting for 15+ days
CREATE OR REPLACE VIEW unsold_stock_view AS
SELECT f.name, l.crop_name, l.quantity, l.harvest_date
FROM listings l
JOIN farmers f ON l.farmer_id = f.farmer_id
WHERE l.status = 'available' AND l.harvest_date < CURRENT_DATE - INTERVAL '15 days';

-- Report: average farmer rating
CREATE OR REPLACE VIEW farmer_avg_rating_view AS
SELECT f.name, AVG(r.score) AS avg_rating, COUNT(r.rating_id) AS num_ratings
FROM farmers f
JOIN listings l ON f.farmer_id = l.farmer_id
JOIN orders o ON l.listing_id = o.listing_id
JOIN ratings r ON o.order_id = r.order_id
GROUP BY f.name
ORDER BY avg_rating DESC;

-- Report: pending payments
CREATE OR REPLACE VIEW pending_payments_view AS
SELECT o.order_id, b.name AS buyer, p.amount, p.status
FROM orders o
JOIN buyers b ON o.buyer_id = b.buyer_id
JOIN payments p ON o.order_id = p.order_id
WHERE p.status = 'pending';

-- ============ FUNCTION (called via RPC) ============

-- Total paid revenue for a given farmer
CREATE OR REPLACE FUNCTION get_farmer_revenue(p_farmer_id INT)
RETURNS TABLE(farmer_name VARCHAR, total_revenue DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT f.name, SUM(p.amount)
    FROM farmers f
    JOIN listings l ON f.farmer_id = l.farmer_id
    JOIN orders o ON l.listing_id = o.listing_id
    JOIN payments p ON o.order_id = p.order_id
    WHERE f.farmer_id = p_farmer_id AND p.status = 'paid'
    GROUP BY f.name;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- FEATURE 1: ORDER LIFECYCLE & HISTORY
-- ============================================================

-- Tracks every status change on an order
CREATE TABLE order_status_history (
    history_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ DEFAULT now()
);

-- Update an order's status with validation + audit history.
-- Callable via RPC: supabase.rpc("update_order_status", {...})
CREATE OR REPLACE FUNCTION update_order_status(
    p_order_id INT,
    p_new_status VARCHAR,
    p_changed_by VARCHAR DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
    v_old orders.status%TYPE;
BEGIN
    SELECT status INTO v_old FROM orders WHERE order_id = p_order_id;
    IF v_old IS NULL THEN
        RAISE EXCEPTION 'Order % not found', p_order_id;
    END IF;

    IF NOT (
        (v_old = 'pending'    AND p_new_status IN ('confirmed','cancelled'))
        OR (v_old = 'confirmed' AND p_new_status IN ('delivered','cancelled'))
        OR (v_old = 'delivered'  AND p_new_status = 'paid')
    ) THEN
        RAISE EXCEPTION 'Invalid status transition: % -> %', v_old, p_new_status;
    END IF;

    UPDATE orders SET status = p_new_status WHERE order_id = p_order_id;
    INSERT INTO order_status_history (order_id, old_status, new_status, changed_by)
    VALUES (p_order_id, v_old, p_new_status, p_changed_by);

    RETURN p_new_status;
END;
$$ LANGUAGE plpgsql;

-- Full order history with buyer/farmer context
CREATE OR REPLACE VIEW order_history_view AS
SELECT o.order_id, o.quantity_ordered, o.order_date, o.status,
       b.name AS buyer_name, b.buyer_type,
       f.name AS farmer_name, l.crop_name, l.unit,
       (o.quantity_ordered * l.price_per_unit) AS order_value
FROM orders o
JOIN buyers b   ON o.buyer_id = b.buyer_id
JOIN listings l ON o.listing_id = l.listing_id
JOIN farmers f  ON l.farmer_id = f.farmer_id;

-- Audit trail helper (history of a single order's transitions)
CREATE OR REPLACE VIEW order_status_audit_view AS
SELECT h.history_id, h.order_id, h.old_status, h.new_status,
       h.changed_by, h.changed_at
FROM order_status_history h
ORDER BY h.changed_at DESC;


-- ============================================================
-- FEATURE 2: DATABASE CROP ENGINE
-- ============================================================

-- Agronomy knowledge base (soil/weather suitability + revenue)
CREATE TABLE crops (
    crop_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    seasons TEXT[] NOT NULL,
    ph_min NUMERIC(4,1), ph_max NUMERIC(4,1),
    moisture_min NUMERIC(5,2), moisture_max NUMERIC(5,2),
    n_min NUMERIC(4,1), n_max NUMERIC(4,1),
    p_min NUMERIC(4,1), p_max NUMERIC(4,1),
    k_min NUMERIC(4,1), k_max NUMERIC(4,1),
    temp_min NUMERIC(4,1), temp_max NUMERIC(4,1),
    revenue_min VARCHAR(40), revenue_max VARCHAR(40),
    market_outlook TEXT
);

-- Score crops against provided soil/weather params.
-- Callable via RPC: supabase.rpc("recommend_crops", {...})
CREATE OR REPLACE FUNCTION recommend_crops(
    p_ph NUMERIC, p_moisture NUMERIC,
    p_n NUMERIC, p_p NUMERIC, p_k NUMERIC,
    p_temp NUMERIC, p_season TEXT
)
RETURNS TABLE(crop_name VARCHAR, match_score INT, match_pct INT,
              revenue VARCHAR, market_outlook TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT scored.name, scored.match_score, scored.match_pct,
           scored.revenue, scored.market_outlook
    FROM (
        SELECT c.name,
               ((CASE WHEN p_ph BETWEEN c.ph_min AND c.ph_max THEN 1 ELSE 0 END)
              + (CASE WHEN p_moisture BETWEEN c.moisture_min AND c.moisture_max THEN 1 ELSE 0 END)
              + (CASE WHEN p_n BETWEEN c.n_min AND c.n_max THEN 1 ELSE 0 END)
              + (CASE WHEN p_p BETWEEN c.p_min AND c.p_max THEN 1 ELSE 0 END)
              + (CASE WHEN p_k BETWEEN c.k_min AND c.k_max THEN 1 ELSE 0 END)
              + (CASE WHEN p_temp BETWEEN c.temp_min AND c.temp_max THEN 1 ELSE 0 END))::INT AS match_score,
               round(
                  ((CASE WHEN p_ph BETWEEN c.ph_min AND c.ph_max THEN 1 ELSE 0 END)
                + (CASE WHEN p_moisture BETWEEN c.moisture_min AND c.moisture_max THEN 1 ELSE 0 END)
                + (CASE WHEN p_n BETWEEN c.n_min AND c.n_max THEN 1 ELSE 0 END)
                + (CASE WHEN p_p BETWEEN c.p_min AND c.p_max THEN 1 ELSE 0 END)
                + (CASE WHEN p_k BETWEEN c.k_min AND c.k_max THEN 1 ELSE 0 END)
                + (CASE WHEN p_temp BETWEEN c.temp_min AND c.temp_max THEN 1 ELSE 0 END)) / 6.0 * 100)::INT AS match_pct,
               CAST(c.revenue_min || '–' || c.revenue_max AS VARCHAR) AS revenue,
               c.market_outlook
        FROM crops c
        WHERE p_season = ANY(c.seasons)
    ) scored
    WHERE scored.match_score >= 4
    ORDER BY scored.match_score DESC, scored.match_pct DESC
    LIMIT 5;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- FEATURE 3: INVENTORY & SALES SUMMARY
-- ============================================================

-- Current stock position for every listing
CREATE OR REPLACE VIEW inventory_view AS
SELECT l.listing_id, l.crop_name, l.quantity, l.unit,
       l.price_per_unit, l.status, l.harvest_date,
       f.name AS farmer_name, f.village
FROM listings l
JOIN farmers f ON l.farmer_id = f.farmer_id
ORDER BY l.crop_name;

-- Low-stock alerts (available but running low)
CREATE OR REPLACE VIEW low_stock_view AS
SELECT l.listing_id, l.crop_name, l.quantity, l.unit, f.name AS farmer_name
FROM listings l
JOIN farmers f ON l.farmer_id = f.farmer_id
WHERE l.status = 'available' AND l.quantity <= 20
ORDER BY l.quantity ASC;

-- Monthly sales summary (value = ordered qty x listing price)
CREATE OR REPLACE VIEW monthly_sales_summary_view AS
SELECT TO_CHAR(o.order_date, 'YYYY-MM') AS month,
       COUNT(o.order_id)                AS total_orders,
       COALESCE(SUM(o.quantity_ordered), 0)                AS total_quantity,
       COALESCE(SUM(o.quantity_ordered * l.price_per_unit), 0) AS sales_value
FROM orders o
JOIN listings l ON o.listing_id = l.listing_id
GROUP BY month
ORDER BY month DESC;


-- ============================================================
-- FEATURE 4: AUTH (user linkage + Row Level Security)
-- ============================================================
-- The app works with the secret key (bypasses RLS). These policies matter
-- only if you switch to anon/publishable keys. Every farmer/buyer row can be
-- optionally linked to a Supabase Auth user via auth.users(id).

ALTER TABLE farmers ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE buyers  ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

ALTER TABLE farmers   ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyers    ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings  ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders    ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments  ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings   ENABLE ROW LEVEL SECURITY;

-- A farmer can only manage their own profile row
DROP POLICY IF EXISTS "farmers_own_rows" ON farmers;
CREATE POLICY "farmers_own_rows" ON farmers
    FOR ALL USING (auth.uid() = user_id);

-- A buyer can only manage their own profile row
DROP POLICY IF EXISTS "buyers_own_rows" ON buyers;
CREATE POLICY "buyers_own_rows" ON buyers
    FOR ALL USING (auth.uid() = user_id);

-- Anyone can view listings; the owning farmer manages them
DROP POLICY IF EXISTS "listings_read_public" ON listings;
CREATE POLICY "listings_read_public" ON listings
    FOR SELECT USING (true);
DROP POLICY IF EXISTS "listings_owner_all" ON listings;
CREATE POLICY "listings_owner_all" ON listings
    FOR ALL USING (
        auth.uid() = (SELECT user_id FROM farmers f WHERE f.farmer_id = listings.farmer_id)
    );

-- Orders visible to the buyer or the listing's farmer
DROP POLICY IF EXISTS "orders_visible" ON orders;
CREATE POLICY "orders_visible" ON orders
    FOR SELECT USING (
        auth.uid() = (SELECT user_id FROM buyers b WHERE b.buyer_id = orders.buyer_id)
        OR auth.uid() = (
            SELECT f.user_id FROM farmers f
            JOIN listings l ON l.farmer_id = f.farmer_id
            WHERE l.listing_id = orders.listing_id
        )
    );


-- ============================================================
-- REPORT RPC FUNCTIONS (used by the UI's Reports pages)
-- ============================================================
-- The UI calls these via supabase.rpc("get_most_active_buyers") and
-- supabase.rpc("get_farmer_ratings"). They wrap the equivalent views
-- so the front-end gets the same data through RPC calls.

-- Report: most active buyers (by total order volume)
CREATE OR REPLACE FUNCTION get_most_active_buyers()
RETURNS TABLE(name VARCHAR, total_orders BIGINT, total_volume NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT b.name,
           COUNT(o.order_id)::BIGINT,
           COALESCE(SUM(o.quantity_ordered), 0)
    FROM buyers b
    JOIN orders o ON b.buyer_id = o.buyer_id
    GROUP BY b.name
    ORDER BY total_volume DESC;
END;
$$ LANGUAGE plpgsql;

-- Report: average farmer rating (from buyer ratings)
CREATE OR REPLACE FUNCTION get_farmer_ratings()
RETURNS TABLE(name VARCHAR, avg_rating NUMERIC, num_ratings BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT f.name,
           ROUND(AVG(r.score), 2),
           COUNT(r.rating_id)::BIGINT
    FROM farmers f
    JOIN listings l ON f.farmer_id = l.farmer_id
    JOIN orders o ON l.listing_id = o.listing_id
    JOIN ratings r ON o.order_id = r.order_id
    GROUP BY f.name
    ORDER BY avg_rating DESC;
END;
$$ LANGUAGE plpgsql;
