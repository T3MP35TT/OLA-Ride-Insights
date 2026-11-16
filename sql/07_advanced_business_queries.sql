USE ola_ride_insights;
SELECT COUNT(*) AS total_bookings,
 SUM(LOWER(TRIM(booking_status))='success') AS successful_bookings,
 ROUND(100.0*SUM(LOWER(TRIM(booking_status))='success')/NULLIF(COUNT(*),0),2) AS success_pct,
 SUM(LOWER(TRIM(booking_status)) IN ('canceled by customer','canceled by driver')) AS customer_or_driver_cancellations,
 SUM(LOWER(TRIM(booking_status))='driver not found') AS driver_not_found FROM bookings;
SELECT vehicle_type, SUM(booking_value) AS booking_value_total, AVG(ride_distance) AS avg_distance FROM bookings GROUP BY vehicle_type ORDER BY booking_value_total DESC;
SELECT payment_method, SUM(booking_value) AS completed_booking_value FROM bookings WHERE LOWER(TRIM(booking_status))='success' GROUP BY payment_method ORDER BY completed_booking_value DESC;
SELECT customer_id, SUM(booking_value) AS total_booking_value FROM bookings GROUP BY customer_id ORDER BY total_booking_value DESC LIMIT 5;
SELECT date, COUNT(*) AS ride_volume FROM bookings GROUP BY date ORDER BY date;
SELECT DATE_FORMAT(date,'%Y-%m') AS booking_month, SUM(CASE WHEN LOWER(TRIM(booking_status))='success' THEN booking_value ELSE 0 END) AS completed_booking_value FROM bookings GROUP BY DATE_FORMAT(date,'%Y-%m') ORDER BY booking_month;
SELECT HOUR(time) AS booking_hour, COUNT(*) AS booking_count FROM bookings GROUP BY HOUR(time) ORDER BY booking_hour;
SELECT ROUND(100.0*SUM(LOWER(TRIM(booking_status))='canceled by customer')/NULLIF(COUNT(*),0),2) AS customer_cancellation_pct, ROUND(100.0*SUM(LOWER(TRIM(booking_status))='canceled by driver')/NULLIF(COUNT(*),0),2) AS driver_cancellation_pct FROM bookings;
SELECT vehicle_type, AVG(driver_ratings) AS mean_driver_rating, AVG(customer_rating) AS mean_customer_rating FROM bookings GROUP BY vehicle_type;
SELECT 'Customer' AS cancellation_side, canceled_rides_by_customer AS reason, COUNT(*) AS records FROM bookings WHERE LOWER(TRIM(booking_status))='canceled by customer' GROUP BY canceled_rides_by_customer UNION ALL SELECT 'Driver', canceled_rides_by_driver, COUNT(*) FROM bookings WHERE LOWER(TRIM(booking_status))='canceled by driver' GROUP BY canceled_rides_by_driver;
