USE ola_ride_insights;

-- 01. All successful bookings. The app previews rows and exports the complete result.
SELECT booking_id, customer_id, vehicle_type, booking_status, booking_value, payment_method, ride_distance
FROM bookings
WHERE LOWER(TRIM(booking_status)) = 'success'
ORDER BY booking_id;

-- 02. Mean observed ride distance and sample count by vehicle; source unit is unspecified.
SELECT vehicle_type, AVG(ride_distance) AS average_ride_distance,
       COUNT(ride_distance) AS trips_with_distance
FROM bookings
GROUP BY vehicle_type
ORDER BY average_ride_distance DESC;

-- 03. Customer cancellations; all bookings are the denominator for a rate.
SELECT COUNT(*) AS customer_cancellations
FROM bookings
WHERE LOWER(TRIM(booking_status)) = 'canceled by customer';

-- 04. Top five non-null customers by booking count; ID resolves ties.
SELECT customer_id, COUNT(*) AS bookings
FROM bookings
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY bookings DESC, customer_id ASC
LIMIT 5;

-- 05. Driver cancellations with both reason terms in the recorded text.
SELECT COUNT(*) AS driver_personal_car_cancellations
FROM bookings
WHERE LOWER(TRIM(booking_status)) = 'canceled by driver'
  AND LOWER(COALESCE(canceled_rides_by_driver, '')) LIKE '%personal%'
  AND LOWER(COALESCE(canceled_rides_by_driver, '')) LIKE '%car%';

-- 06. Observed Prime Sedan driver-rating range.
SELECT MAX(driver_ratings) AS maximum_driver_rating,
       MIN(driver_ratings) AS minimum_driver_rating
FROM bookings
WHERE LOWER(TRIM(vehicle_type)) = 'prime sedan';

-- 07. All UPI bookings.
SELECT booking_id, customer_id, vehicle_type, booking_value, payment_method
FROM bookings
WHERE LOWER(TRIM(payment_method)) = 'upi'
ORDER BY booking_id;

-- 08. Observed customer rating average and feedback count by vehicle.
SELECT vehicle_type, AVG(customer_rating) AS average_customer_rating,
       COUNT(customer_rating) AS rated_trips
FROM bookings
GROUP BY vehicle_type
ORDER BY average_customer_rating DESC;

-- 09. Completed booking value is not confirmed accounting revenue.
SELECT SUM(booking_value) AS completed_booking_value
FROM bookings
WHERE LOWER(TRIM(booking_status)) = 'success';

-- 10. Incomplete rides use the source indicator, not a booking-status category.
SELECT booking_id, customer_id, incomplete_rides_reason
FROM bookings
WHERE LOWER(TRIM(COALESCE(incomplete_rides, ''))) = 'yes'
ORDER BY booking_id;
