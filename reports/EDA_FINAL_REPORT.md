# Exploratory data analysis

## Definitions

The source workbook covers July 2024. Successful bookings are exactly `Success`. Customer and driver cancellations are counted from their respective exact status labels. `Driver Not Found` is a separate status. Percentages use all booking rows as denominator. Completed-trip distance and completed booking value use successful bookings only; booking value is not verified accounting revenue.

## Verified findings

- **Source rows retained:** 103,024
- **Successful bookings:** 63,967 (62.09% of all rows)
- **Unsuccessful bookings:** 39,057 retained for operational analysis
- **Customer cancellations:** 10,499 (10.19% of all rows)
- **Driver cancellations:** 18,434 (17.89% of all rows)
- **Driver not found:** 10,124 (9.83% of all rows)
- **Highest volume vehicle:** Prime Sedan
- **Most used recorded payment:** Cash
- **Mean completed ride distance (successful bookings only):** 22.85
- **Mean booking value, all statuses:** 548.75
- **Completed booking value:** 35,080,467.00
- **Mean customer rating:** 4.00
- **Mean driver rating:** 4.00
- **Peak booking hour:** 12:00 (booking count, not completed rides).
- **Most frequent customer cancellation reason:** Driver is not moving towards pickup location (3,175).
- **Most frequent driver cancellation reason:** Personal & Car related issue (6,542).

## Top five vehicles by completed ride distance

- Mini: 225,703 source units
- Prime Plus: 227,186 source units
- Bike: 227,746 source units
- eBike: 230,842 source units
- Prime Sedan: 234,535 source units

## Top customers by total recorded booking value

- `CID785112`: 8,025
- `CID308763`: 6,281
- `CID734557`: 6,177
- `CID353074`: 6,110
- `CID836942`: 6,019

## Completed booking value by vehicle

- Prime Sedan: 5,224,050
- eBike: 5,054,662
- Auto: 5,051,846
- Prime Plus: 5,015,165
- Bike: 4,971,968
- Mini: 4,885,961
- Prime SUV: 4,876,815

## Completed booking value by payment method

- Cash: 19,260,316
- UPI: 14,168,436
- Credit Card: 1,312,793
- Debit Card: 338,922

## Charts

- [booking_status](eda_charts/booking_status.png)
- [booking_value](eda_charts/booking_value.png)
- [bookings_by_hour](eda_charts/bookings_by_hour.png)
- [bookings_by_weekday](eda_charts/bookings_by_weekday.png)
- [cancellations_by_hour](eda_charts/cancellations_by_hour.png)
- [completed_value_by_payment](eda_charts/completed_value_by_payment.png)
- [completed_value_by_vehicle](eda_charts/completed_value_by_vehicle.png)
- [customer_cancel_reason](eda_charts/customer_cancel_reason.png)
- [customer_rating](eda_charts/customer_rating.png)
- [customer_rating_by_vehicle](eda_charts/customer_rating_by_vehicle.png)
- [daily_average_distance](eda_charts/daily_average_distance.png)
- [daily_booking_volume](eda_charts/daily_booking_volume.png)
- [daily_completed_booking_value](eda_charts/daily_completed_booking_value.png)
- [daily_completed_distance](eda_charts/daily_completed_distance.png)
- [distance_by_vehicle](eda_charts/distance_by_vehicle.png)
- [distance_value_scatter](eda_charts/distance_value_scatter.png)
- [driver_cancel_reason](eda_charts/driver_cancel_reason.png)
- [driver_not_found_by_pickup](eda_charts/driver_not_found_by_pickup.png)
- [driver_rating](eda_charts/driver_rating.png)
- [driver_rating_by_vehicle](eda_charts/driver_rating_by_vehicle.png)
- [incomplete_reason](eda_charts/incomplete_reason.png)
- [payment_method](eda_charts/payment_method.png)
- [ride_distance](eda_charts/ride_distance.png)
- [successful_drop_locations](eda_charts/successful_drop_locations.png)
- [top5_completed_distance_by_vehicle](eda_charts/top5_completed_distance_by_vehicle.png)
- [turnaround_metric_correlation](eda_charts/turnaround_metric_correlation.png)
- [value_by_status](eda_charts/value_by_status.png)
- [value_by_vehicle](eda_charts/value_by_vehicle.png)
- [vehicle_type](eda_charts/vehicle_type.png)
- [weekday_hour_heatmap](eda_charts/weekday_hour_heatmap.png)
- [weekday_weekend_bookings](eda_charts/weekday_weekend_bookings.png)

## Business recommendations

- Examine the separate driver-not-found share by hour and pickup area as a driver matching/availability issue.
- Align supply to observed completed-trip distance and hourly/location demand; evaluate changes through a measured pilot.
- Use customer and driver cancellation reason breakdowns separately to target process fixes.
- Analyze payment preference using successful bookings and completed booking value.
- Interpret ratings with feedback coverage; missing ratings are unavailable feedback, not zero.
