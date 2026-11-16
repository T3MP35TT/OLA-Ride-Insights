"""Numbered business questions and their SQL for the SQL Explorer."""

QUESTIONS = {
    "Successful bookings": (
        "SELECT booking_id, customer_id, vehicle_type, booking_status, booking_value, payment_method, ride_distance "
        "FROM bookings WHERE LOWER(TRIM(booking_status)) = 'success' ORDER BY booking_id;",
        "Returns every successful source booking. The explorer shows a preview and provides the full result as CSV.",
    ),
    "Average ride distance by vehicle": (
        "SELECT vehicle_type, AVG(ride_distance) AS average_ride_distance, COUNT(ride_distance) AS trips_with_distance "
        "FROM bookings GROUP BY vehicle_type ORDER BY average_ride_distance DESC;",
        "Compares mean observed ride distance and contributing non-null trips by vehicle; source units are unspecified.",
    ),
    "Customer cancellations": (
        "SELECT COUNT(*) AS customer_cancellations FROM bookings "
        "WHERE LOWER(TRIM(booking_status)) = 'canceled by customer';",
        "Counts the exact customer-cancellation status; the denominator is all source bookings.",
    ),
    "Top five customers by rides": (
        "SELECT customer_id, COUNT(*) AS bookings FROM bookings "
        "WHERE customer_id IS NOT NULL GROUP BY customer_id "
        "ORDER BY bookings DESC, customer_id ASC LIMIT 5;",
        "Ranks non-null customer IDs by booking count; customer ID breaks ties alphabetically.",
    ),
    "Driver personal/car cancellations": (
        "SELECT COUNT(*) AS driver_personal_car_cancellations FROM bookings "
        "WHERE LOWER(TRIM(booking_status)) = 'canceled by driver' "
        "AND LOWER(COALESCE(canceled_rides_by_driver, '')) LIKE '%personal%' "
        "AND LOWER(COALESCE(canceled_rides_by_driver, '')) LIKE '%car%';",
        "Counts driver cancellations whose recorded reason contains both 'personal' and 'car'.",
    ),
    "Prime Sedan driver rating range": (
        "SELECT MAX(driver_ratings) AS maximum_driver_rating, "
        "MIN(driver_ratings) AS minimum_driver_rating FROM bookings "
        "WHERE LOWER(TRIM(vehicle_type)) = 'prime sedan';",
        "Returns the observed maximum and minimum non-null driver rating for Prime Sedan.",
    ),
    "UPI bookings": (
        "SELECT booking_id, customer_id, vehicle_type, booking_value, payment_method FROM bookings "
        "WHERE LOWER(TRIM(payment_method)) = 'upi' ORDER BY booking_id;",
        "Returns every booking recorded with UPI as the payment method.",
    ),
    "Average customer rating by vehicle": (
        "SELECT vehicle_type, AVG(customer_rating) AS average_customer_rating, "
        "COUNT(customer_rating) AS rated_trips FROM bookings "
        "GROUP BY vehicle_type ORDER BY average_customer_rating DESC;",
        "Compares observed customer-rating averages and feedback counts by vehicle; missing ratings remain excluded.",
    ),
    "Completed booking value": (
        "SELECT SUM(booking_value) AS completed_booking_value FROM bookings "
        "WHERE LOWER(TRIM(booking_status)) = 'success';",
        "Sums recorded booking value for successful bookings only; this is not verified accounting revenue.",
    ),
    "Incomplete rides and reason": (
        "SELECT booking_id, customer_id, incomplete_rides_reason FROM bookings "
        "WHERE LOWER(TRIM(COALESCE(incomplete_rides, ''))) = 'yes' ORDER BY booking_id;",
        "Returns rows marked incomplete by the source flag; incomplete is not a booking-status category.",
    ),
}
