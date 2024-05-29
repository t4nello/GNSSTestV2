WITH measurements AS (
    SELECT
        latitude,
        longitude,
        sessionid,
        device
    FROM
        mqtt_consumer
    WHERE
        sessionid = 42
        AND device IN (SELECT DISTINCT device FROM mqtt_consumer WHERE sessionid = 2268)
),
reference_data AS (
    SELECT
        AVG(latitude::numeric) AS avg_latitude,
        AVG(longitude::numeric) AS avg_longitude
    FROM
        mqtt_consumer
    WHERE
        sessionid = 39
),
converted_measurements AS (
    SELECT
        device,
        ST_X(
            ST_Transform(
                ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),
                32633)) AS utm_measurements_x,
        ST_Y(
            ST_Transform(
                ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),
                32633)) AS utm_measurements_y
    FROM
        measurements
),
converted_reference_data AS (
    SELECT
        ST_X(
            ST_Transform(
                ST_SetSRID(ST_MakePoint(avg_longitude, avg_latitude), 4326),
                32633)) AS utm_reference_x,
        ST_Y(
            ST_Transform(
                ST_SetSRID(ST_MakePoint(avg_longitude, avg_latitude), 4326),
                32633)) AS utm_reference_y
    FROM
        reference_data
)
SELECT
    device,
   /* SQRT(AVG(POWER(CAST(utm_measurements_x AS numeric) - utm_reference_x, 2))) AS sigma_x,
    SQRT(AVG(POWER(CAST(utm_measurements_y AS numeric) - utm_reference_y, 2))) AS sigma_y, */
    0.62 * SQRT(AVG(POWER(CAST(utm_measurements_x AS numeric) - utm_reference_x, 2))) + 0.56 * SQRT(AVG(POWER(CAST(utm_measurements_y AS numeric) - utm_reference_y, 2))) AS cep_radius,
    2 * (SQRT(AVG(POWER(CAST(utm_measurements_x AS numeric) - utm_reference_x, 2))) + SQRT(AVG(POWER(CAST(utm_measurements_y AS numeric) - utm_reference_y, 2)))) AS twodrms_radius
FROM
    converted_measurements
JOIN
    converted_reference_data ON 1=1
GROUP BY
    device;
