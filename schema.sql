-- AgriConnect schema — run this first against your Neon database

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
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','confirmed','delivered'))
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

-- View: active listings with farmer details
CREATE VIEW active_listings_view AS
SELECT l.listing_id, f.name AS farmer_name, f.village,
       l.crop_name, l.quantity, l.price_per_unit, l.harvest_date
FROM listings l
JOIN farmers f ON l.farmer_id = f.farmer_id
WHERE l.status = 'available';

-- Function: total paid revenue for a given farmer
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
