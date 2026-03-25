-- Cấu hình: Lưu thành bảng (table) để Dashboard truy vấn cho nhanh
{{ config(materialized='table') }}

WITH event_logs AS (
    -- Gọi lại bảng Silver đã làm sạch
    SELECT * FROM {{ ref('stg_event_logs') }}
),

songs AS (
    -- Đọc trực tiếp Master Data từ MinIO
    SELECT * FROM read_csv_auto('s3://music-app-datalake/bronze/master_data/songs/songs.csv')
),

artists AS (
    SELECT * FROM read_csv_auto('s3://music-app-datalake/bronze/master_data/artists/artists.csv')
)

-- Bắt đầu tổng hợp dữ liệu (Aggregation)
SELECT
    CAST(e.event_time AS DATE) AS play_date,
    s.title AS song_title,
    a.name AS artist_name,
    COUNT(e.event_id) AS total_plays, -- Tổng số lượt nghe
    SUM(e.listen_duration_seconds) AS total_listen_time_seconds, -- Tổng thời gian nghe
    COUNT(DISTINCT e.user_id) AS unique_listeners -- Số lượng người nghe độc lập (khác nhau)
FROM event_logs e
JOIN songs s ON e.song_id = s.song_id
JOIN artists a ON s.artist_id = a.artist_id
WHERE e.event_type = 'play_song' -- Chỉ tính các sự kiện là nghe nhạc
GROUP BY 1, 2, 3
ORDER BY play_date DESC, total_plays DESC