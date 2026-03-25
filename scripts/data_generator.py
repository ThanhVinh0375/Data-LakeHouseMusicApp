import json
import random
import os
import pandas as pd
from faker import Faker
from datetime import datetime
import boto3
from botocore.client import Config

# --- CẤU HÌNH ---
BUCKET_NAME = "music-app-datalake"
NUM_USERS = 1000
NUM_ARTISTS = 100
NUM_SONGS_PER_ARTIST = 5
NUM_EVENTS = 10000

fake = Faker()

# Khởi tạo kết nối tới MinIO (Local S3)
s3_client = boto3.client('s3',
    endpoint_url='http://host.docker.internal:9000', # Trỏ tới MinIO trên máy host
    aws_access_key_id='admin',
    aws_secret_access_key='password123',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Tự động tạo Bucket nếu chưa tồn tại
try:
    s3_client.head_bucket(Bucket=BUCKET_NAME)
except:
    print(f"✨ Đang tạo Bucket mới: {BUCKET_NAME}...")
    s3_client.create_bucket(Bucket=BUCKET_NAME)

def upload_to_minio(local_file_name, s3_folder, s3_file_name):
    s3_path = f"{s3_folder}/{s3_file_name}"
    try:
        print(f"  ⬆️ Đang upload {local_file_name} lên MinIO (s3://{BUCKET_NAME}/{s3_path})...")
        s3_client.upload_file(local_file_name, BUCKET_NAME, s3_path)
        os.remove(local_file_name) 
    except Exception as e:
        print(f"❌ Lỗi khi upload {local_file_name}: {e}")

def get_current_date_path():
    now = datetime.now()
    return f"year={now.year}/month={now.strftime('%m')}/day={now.strftime('%d')}"

def generate_and_upload_master_data():
    print("⏳ Bước 1: Tạo và Upload Master Data lên MinIO...")
    users = [{"user_id": fake.uuid4(), "name": fake.name(), "email": fake.email(), "country": fake.country_code(), "subscription_tier": random.choice(['Free', 'Premium']), "created_at": fake.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")} for _ in range(NUM_USERS)]
    pd.DataFrame(users).to_csv("users.csv", index=False)
    upload_to_minio("users.csv", "bronze/master_data/users", "users.csv")
    
    artists = [{"artist_id": fake.uuid4(), "name": fake.name(), "genre": random.choice(['Pop', 'Rock', 'Hip Hop', 'Jazz', 'EDM'])} for _ in range(NUM_ARTISTS)]
    pd.DataFrame(artists).to_csv("artists.csv", index=False)
    upload_to_minio("artists.csv", "bronze/master_data/artists", "artists.csv")
    
    songs = [{"song_id": fake.uuid4(), "artist_id": artist["artist_id"], "title": fake.sentence(nb_words=3).replace('.', ''), "duration_seconds": random.randint(120, 360), "release_year": random.randint(2010, 2023)} for artist in artists for _ in range(random.randint(1, NUM_SONGS_PER_ARTIST))]
    pd.DataFrame(songs).to_csv("songs.csv", index=False)
    upload_to_minio("songs.csv", "bronze/master_data/songs", "songs.csv")
    
    return users, songs

def generate_and_upload_event_logs(users, songs):
    print("\n⏳ Bước 2: Tạo và Upload Event Logs lên MinIO...")
    user_ids = [u["user_id"] for u in users]
    song_ids = [s["song_id"] for s in songs]
    local_event_file = "event_logs.jsonl"
    
    with open(local_event_file, "w", encoding="utf-8") as f:
        for _ in range(NUM_EVENTS):
            event_type = random.choices(['play_song', 'like_song', 'skip_song'], weights=[0.7, 0.1, 0.2])[0]
            event = {"event_id": fake.uuid4(), "user_id": random.choice(user_ids), "event_type": event_type, "timestamp": fake.date_time_between(start_date='-1d', end_date='now').isoformat(), "platform": random.choice(['iOS', 'Android', 'Web'])}
            if event_type == 'play_song':
                event["song_id"] = random.choice(song_ids)
                event["listen_duration"] = random.randint(10, 360)
            elif event_type in ['like_song', 'skip_song']:
                event["song_id"] = random.choice(song_ids)
            f.write(json.dumps(event) + "\n")
            
    date_path = get_current_date_path()
    gcs_event_folder = f"bronze/event_logs/{date_path}"
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    gcs_event_file_name = f"events_{timestamp_str}.jsonl"
    upload_to_minio(local_event_file, gcs_event_folder, gcs_event_file_name)

if __name__ == "__main__":
    print(f"🚀 Bắt đầu quy trình Ingestion cho Local Data Lake (MinIO)...\n")
    users_data, songs_data = generate_and_upload_master_data()
    generate_and_upload_event_logs(users_data, songs_data)
    print("\n🎉 Hoàn thành! Mở http://localhost:9001 để xem dữ liệu.")