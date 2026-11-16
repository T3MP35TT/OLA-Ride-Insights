USE ola_ride_insights;
-- Compare against Python output by row count and aggregations.
SELECT COUNT(*) AS row_count, COUNT(DISTINCT booking_id) AS booking_ids, SUM(booking_value) AS all_status_booking_value FROM bookings;
SELECT SUM(CASE WHEN LOWER(TRIM(booking_status))='success' THEN 1 ELSE 0 END) AS successful_count,
 SUM(CASE WHEN LOWER(TRIM(booking_status))='success' THEN booking_value ELSE 0 END) AS completed_booking_value FROM bookings;
