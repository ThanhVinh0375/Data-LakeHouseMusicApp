# Sử dụng Python 3.11 bản nhẹ (slim) trên nền Linux
FROM python:3.11-slim

# Cài đặt các công cụ biên dịch cơ bản của Linux (để tránh lỗi tương tự như trên Windows)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code dự án vào
COPY . .

# Lệnh mặc định (có thể thay đổi tùy việc bạn muốn chạy Airflow hay dbt)
CMD ["dbt", "--version"]