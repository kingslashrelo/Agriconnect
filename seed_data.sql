-- Sample data for demoing the schema.
-- Run AFTER schema.sql in the Supabase SQL Editor (paste + Run).

INSERT INTO farmers (name, village, contact, primary_crop) VALUES
('Thomas Varghese', 'Marangattupilly', '9847012345', 'Rubber'),
('Sini Jose', 'Erattupetta', '9847012346', 'Pepper'),
('Rajan Pillai', 'Pala', '9847012347', 'Banana'),
('Mary Abraham', 'Kanjirappally', '9847012348', 'Coconut');

INSERT INTO buyers (name, buyer_type, location, contact) VALUES
('Kottayam Wholesale Traders', 'wholesaler', 'Kottayam', '9846012345'),
('Fresh Mart Retail', 'retailer', 'Pala', '9846012346'),
('Anil Kumar', 'consumer', 'Kottayam', '9846012347');

INSERT INTO listings (farmer_id, crop_name, quantity, unit, price_per_unit, harvest_date, status) VALUES
(1, 'Rubber Sheet', 500, 'kg', 165.00, '2026-06-01', 'available'),
(2, 'Black Pepper', 100, 'kg', 620.00, '2026-06-10', 'available'),
(3, 'Nendran Banana', 300, 'kg', 45.00, '2026-06-15', 'available'),
(4, 'Coconut', 1000, 'unit', 22.00, '2026-06-05', 'available');

INSERT INTO orders (buyer_id, listing_id, quantity_ordered, order_date, status) VALUES
(1, 1, 200, '2026-06-20', 'confirmed'),
(2, 2, 50, '2026-06-21', 'confirmed'),
(3, 3, 20, '2026-06-22', 'pending');

INSERT INTO payments (order_id, amount, status, payment_date) VALUES
(1, 33000.00, 'paid', '2026-06-20'),
(2, 31000.00, 'paid', '2026-06-21'),
(3, 900.00, 'pending', NULL);

INSERT INTO ratings (order_id, score, comment) VALUES
(1, 5, 'Good quality rubber sheets, on time'),
(2, 4, 'Fresh pepper, prompt delivery');

INSERT INTO schemes (farmer_id, scheme_name, eligible) VALUES
(1, 'Rubber Price Stabilisation Scheme', TRUE),
(3, 'PM-KISAN', TRUE);

INSERT INTO price_history (crop_name, record_date, avg_market_price) VALUES
('Rubber Sheet', '2026-05-01', 158.00),
('Rubber Sheet', '2026-06-01', 165.00),
('Black Pepper', '2026-05-01', 600.00),
('Black Pepper', '2026-06-01', 620.00);

-- Crop Advisor agronomy knowledge base.
-- Units match the app's frontend inputs: N/P/K on a 1.0-5.0 soil-rating scale,
-- moisture in % (0-100), temp in °C, pH 0-14, revenue as a range string.
DELETE FROM crops;
INSERT INTO crops (name, seasons, ph_min, ph_max, moisture_min, moisture_max,
                   n_min, n_max, p_min, p_max, k_min, k_max, temp_min, temp_max,
                   revenue_min, revenue_max, market_outlook)
VALUES
('Rice',        ARRAY['Kharif','Rabi','Summer'], 5.0, 7.5, 40, 90, 3.0, 5.0, 2.0, 4.0, 2.0, 4.0, 20, 35, '₹2,000/q',   '₹2,400/q',   'Steady demand; MSP floor supported'),
('Maize',       ARRAY['Kharif','Rabi'],          5.5, 7.5, 40, 80, 3.0, 5.0, 2.0, 4.0, 2.0, 4.0, 18, 32, '₹1,800/q',   '₹2,100/q',   'Growing as fodder + poultry feed'),
('Wheat',       ARRAY['Rabi'],                   6.0, 8.0, 30, 60, 2.5, 4.5, 2.0, 4.0, 2.0, 4.0, 15, 28, '₹2,200/q',   '₹2,500/q',   'Stable MSP; strong rabi demand'),
('Groundnut',   ARRAY['Kharif','Rabi'],         6.0, 7.0, 30, 60, 1.5, 3.0, 2.0, 4.0, 2.0, 4.0, 24, 32, '₹5,500/q',   '₹6,200/q',   'Edible oil demand rising'),
('Soybean',     ARRAY['Kharif'],                6.0, 7.0, 40, 70, 1.5, 3.0, 3.0, 5.0, 2.0, 4.0, 20, 30, '₹4,100/q',   '₹4,800/q',   'Oilseed crush + meal demand firm'),
('Cotton',      ARRAY['Kharif'],                6.0, 8.0, 40, 70, 2.5, 4.5, 2.0, 4.0, 2.5, 4.5, 25, 35, '₹6,000/q',   '₹7,200/q',   'Fabric demand strong; global prices high'),
('Sugarcane',   ARRAY['Kharif'],                6.0, 8.0, 50, 90, 3.0, 5.0, 2.0, 4.0, 3.0, 5.0, 25, 35, '₹340/quintal','₹360/quintal','Ethanol blending lifts price'),
('Black Pepper',ARRAY['Kharif'],                5.0, 6.5, 60, 90, 2.0, 4.0, 1.5, 3.0, 2.0, 4.0, 20, 30, '₹620/kg',    '₹720/kg',    'High-value export spice; demand strong'),
('Banana',      ARRAY['Kharif','Rabi'],         5.5, 7.0, 60, 90, 3.0, 5.0, 2.0, 4.0, 3.0, 5.0, 20, 35, '₹40/kg',     '₹55/kg',     'Year-round demand; good margins'),
('Coconut',     ARRAY['Kharif','Rabi','Summer'],5.5, 7.5, 50, 90, 2.0, 4.0, 1.5, 3.0, 2.0, 4.0, 25, 33, '₹20/unit',   '₹28/unit',   'Kerala staple; copra demand firm'),
('Tomato',      ARRAY['Kharif','Rabi','Summer'],6.0, 7.0, 50, 80, 2.5, 4.5, 2.0, 4.0, 2.5, 4.5, 20, 30, '₹15/kg',     '₹35/kg',     'Volatile but high upside in lean months'),
('Chilli',      ARRAY['Kharif','Rabi'],         5.5, 6.8, 40, 60, 2.0, 4.0, 2.0, 4.0, 2.0, 4.0, 20, 30, '₹60/kg',     '₹100/kg',    'Spice export + domestic kitchen demand');

-- Seed a couple of example order history transitions
INSERT INTO order_status_history (order_id, old_status, new_status, changed_by)
VALUES
(1, 'pending', 'confirmed', 'kottayam_traders'),
(2, 'pending', 'confirmed', 'fresh_mart'),
(1, 'confirmed', 'delivered', 'system'),
(2, 'confirmed', 'delivered', 'system');
