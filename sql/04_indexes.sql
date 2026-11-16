USE ola_ride_insights;
CREATE INDEX ix_bookings_status ON bookings(booking_status);
CREATE INDEX ix_bookings_customer ON bookings(customer_id);
CREATE INDEX ix_bookings_date ON bookings(date);
CREATE INDEX ix_bookings_vehicle ON bookings(vehicle_type);
CREATE INDEX ix_bookings_payment ON bookings(payment_method);
CREATE INDEX ix_bookings_booking_id ON bookings(booking_id);
