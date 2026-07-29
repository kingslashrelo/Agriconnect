-- Sample data for demoing the schema — run after schema.sql

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
