USE ola_ride_insights;
-- Set local_infile=1 on the authorized client/server and change the path to an absolute path.
-- Input order follows the generated cleaned CSV. Empty CSV fields become SQL NULL.
LOAD DATA LOCAL INFILE 'data/processed/ola_cleaned.csv'
INTO TABLE bookings
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@src_date,@src_time,booking_id,booking_status,customer_id,vehicle_type,pickup_location,drop_location,
 @v_tat,@c_tat,canceled_rides_by_customer,canceled_rides_by_driver,incomplete_rides,incomplete_rides_reason,
 @booking_value,payment_method,@ride_distance,@driver_ratings,@customer_rating,
 @booking_datetime,@success_flag,@customer_cancel_flag,@driver_cancel_flag,@cancel_flag,@incomplete_flag,
 @booking_year,@booking_month,@booking_day,@day_of_week,@booking_hour,@weekday_weekend,@time_of_day)
SET date=NULLIF(@src_date,''), time=NULLIF(@src_time,''),
 v_tat=NULLIF(@v_tat,''), c_tat=NULLIF(@c_tat,''),
 booking_value=NULLIF(@booking_value,''), ride_distance=NULLIF(@ride_distance,''),
 driver_ratings=NULLIF(@driver_ratings,''), customer_rating=NULLIF(@customer_rating,'');
