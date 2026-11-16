USE ola_ride_insights;
CREATE TABLE IF NOT EXISTS bookings (
 record_id BIGINT NOT NULL AUTO_INCREMENT,
 booking_id VARCHAR(80) NULL,
 date DATE NULL, time TIME NULL,
 booking_status VARCHAR(80) NULL,
 customer_id VARCHAR(80) NULL,
 vehicle_type VARCHAR(100) NULL,
 pickup_location VARCHAR(200) NULL,
 drop_location VARCHAR(200) NULL,
 v_tat DECIMAL(12,3) NULL, c_tat DECIMAL(12,3) NULL,
 canceled_rides_by_customer VARCHAR(30) NULL,
 canceled_rides_by_driver VARCHAR(30) NULL,
 incomplete_rides VARCHAR(30) NULL,
 incomplete_rides_reason VARCHAR(255) NULL,
 booking_value DECIMAL(14,2) NULL,
 payment_method VARCHAR(80) NULL,
 ride_distance DECIMAL(12,3) NULL,
 driver_ratings DECIMAL(5,2) NULL,
 customer_rating DECIMAL(5,2) NULL,
 canceled_rides_by_customer_reason VARCHAR(255) NULL,
 canceled_rides_by_driver_reason VARCHAR(255) NULL,
 PRIMARY KEY (record_id)
);
