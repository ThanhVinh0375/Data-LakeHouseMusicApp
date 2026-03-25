{{ config(materialized='table') }}

WITH event_logs AS (
    SELECT * FROM {{ ref('stg_event_logs') }}
)

SELECT
    user_id,
    song_id,
    -- Đếm số lần nghe
    COUNT(CASE WHEN event_type = 'play_song' THEN 1 END) AS play_count,
    -- Gắn cờ xem user có "Like" bài này không (1 là có, 0 là không)
    MAX(CASE WHEN event_type = 'like_song' THEN 1 ELSE 0 END) AS is_liked,
    -- Gắn cờ xem user có hay "Skip" (bỏ qua) bài này không
    SUM(CASE WHEN event_type = 'skip_song' THEN 1 ELSE 0 END) AS skip_count
FROM event_logs
WHERE song_id IS NOT NULL 
GROUP BY 1, 2