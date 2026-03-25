-- Cấu hình: Lưu kết quả thành dạng Bảng (Table) trong DuckDB
{{ config(materialized='table') }}

WITH raw_logs AS (
    -- TUYỆT CHIÊU 1: Dùng glob pattern (**/*.jsonl) 
    -- DuckDB sẽ tự động chui vào tất cả các thư mục con (year=.../month=.../day=...) 
    -- để gom tất cả các file JSONL lại và đọc cùng một lúc!
    SELECT * FROM read_json_auto('s3://music-app-datalake/bronze/event_logs/**/*.jsonl')
),

cleaned_logs AS (
    SELECT
        event_id,
        user_id,
        event_type,
        
        -- Chuẩn hóa tên cột và ép kiểu dữ liệu thời gian
        CAST(timestamp AS TIMESTAMP) AS event_time, 
        
        platform,
        
        -- Các cột tùy chọn: DuckDB tự động điền NULL nếu dòng JSON đó không có key này
        song_id,
        CAST(listen_duration AS INTEGER) AS listen_duration_seconds
        
    FROM raw_logs
    WHERE event_id IS NOT NULL
)

SELECT * FROM cleaned_logs