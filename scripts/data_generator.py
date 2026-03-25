import csv
import json
import random
from faker import Faker
from datetime import datetime, timedelta
import pandas as pd

# Khởi tạo Faker
fake = Faker()

# Cấu hình số lượng dữ liệu muốn sinh ra
NUM_USERS = 1000
NUM_ARTISTS = 100
NUM_SONGS_PER_ARTIST = 5
NUM_EVENTS = 10000

# Danh sách các hằng số
SUBSCRIPTION_TIERS = ['Free', 'Premium']
PLATFORMS = ['iOS', 'Android', 'Web']
EVENT_TYPES = ['play_song', 'like_song', 'skip_song', 'search_artist']
GENRES = ['Pop', 'Rock', 'Hip Hop', 'Jazz', 'EDM', 'Classical', 'R&B']

def generate_master_data():
    print("⏳ Đang tạo Master Data...")
    
    # 1. Generate Users
    users = []
    for _ in range(NUM_USERS):
        users.append({
            "user_id": fake.uuid4(),
            "name": fake.name(),
            "email": fake.email(),
            "country": fake.country_code(),
            "subscription_tier": random.choice(SUBSCRIPTION_TIERS),
            "created_at": fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
        })
    pd.DataFrame(users).to_csv("users.csv", index=False)
    
    # 2. Generate Artists
    artists = []
    for _ in range(NUM_ARTISTS):
        artists.append({
            "artist_id": fake.uuid4(),
            "name": fake.name(), # Dùng tên người giả làm tên nghệ sĩ
            "genre": random.choice(GENRES)
        })
    pd.DataFrame(artists).to_csv("artists.csv", index=False)
    
    # 3. Generate Songs
    songs = []
    for artist in artists:
        for _ in range(random.randint(1, NUM_SONGS_PER_ARTIST)):
            songs.append({
                "song_id": fake.uuid4(),
                "artist_id": artist["artist_id"],
                "title": fake.sentence(nb_words=3).replace('.', ''),
                "duration_seconds": random.randint(120, 360), # Bài hát từ 2-6 phút
                "release_year": random.randint(2010, 2023)
            })
    pd.DataFrame(songs).to_csv("songs.csv", index=False)
    
    print("✅ Đã tạo xong: users.csv, artists.csv, songs.csv")
    return users, artists, songs

def generate_event_logs(users, artists, songs):
    print("⏳ Đang tạo Event Logs...")
    
    user_ids = [u["user_id"] for u in users]
    song_ids = [s["song_id"] for s in songs]
    artist_names = [a["name"] for a in artists]
    
    with open("event_logs.jsonl", "w", encoding="utf-8") as f:
        for _ in range(NUM_EVENTS):
            event_type = random.choices(EVENT_TYPES, weights=[0.6, 0.1, 0.2, 0.1])[0] # 60% là play_song
            
            # Cấu trúc chung của mọi event
            event = {
                "event_id": fake.uuid4(),
                "user_id": random.choice(user_ids),
                "event_type": event_type,
                "timestamp": fake.date_time_between(start_date='-10d', end_date='now').isoformat(),
                "platform": random.choice(PLATFORMS)
            }
            
            # Bổ sung properties tùy theo loại event
            if event_type == 'play_song':
                song_id = random.choice(song_ids)
                event["song_id"] = song_id
                event["listen_duration"] = random.randint(10, 360) # Nghe bao nhiêu giây
            elif event_type in ['like_song', 'skip_song']:
                event["song_id"] = random.choice(song_ids)
            elif event_type == 'search_artist':
                event["search_query"] = random.choice(artist_names) # Tìm kiếm tên nghệ sĩ
                
            # Ghi từng dòng JSON (JSONL)
            f.write(json.dumps(event) + "\n")
            
    print("✅ Đã tạo xong: event_logs.jsonl")

if __name__ == "__main__":
    # Chạy quy trình
    users_data, artists_data, songs_data = generate_master_data()
    generate_event_logs(users_data, artists_data, songs_data)
    print("🚀 Hoàn thành sinh dữ liệu giả lập cho Bronze Layer!")