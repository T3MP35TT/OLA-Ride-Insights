USE ola_ride_insights;
SELECT COUNT(*) AS rows_loaded, COUNT(DISTINCT booking_id) AS unique_booking_ids FROM bookings;
SELECT booking_status, COUNT(*) AS bookings FROM bookings GROUP BY booking_status ORDER BY bookings DESC;
SELECT COUNT(*) AS missing_booking_ids FROM bookings WHERE booking_id IS NULL OR TRIM(booking_id)='';
SELECT COUNT(*) AS suspicious_values FROM bookings WHERE booking_value<0 OR ride_distance<0 OR customer_rating NOT BETWEEN 0 AND 5 OR driver_ratings NOT BETWEEN 0 AND 5;
