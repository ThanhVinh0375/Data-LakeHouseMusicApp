-- Cấu hình: Lưu kết quả dưới dạng Table trong DuckDB
{{ config(materialized='table') }}

WITH raw_users AS (
    -- DuckDB có hàm read_csv_auto tự động đọc và nhận diện kiểu dữ liệu từ S3
    SELECT * FROM read_csv_auto('s3://music-app-datalake/bronze/master_data/users/users.csv')
),

cleaned_users AS (
    SELECT
        user_id,
        name AS user_name,
        email,
        country,
        UPPER(subscription_tier) AS subscription_tier, -- Chuẩn hóa viết hoa
        CAST(created_at AS TIMESTAMP) AS created_at    -- Ép kiểu thời gian chuẩn
    FROM raw_users
    WHERE user_id IS NOT NULL
)

SELECT * FROM cleaned_users