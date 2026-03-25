# Sử dụng Python image bản nhẹ
FROM python:3.10-slim

WORKDIR /app

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ nội dung thư mục scripts vào container
COPY scripts/ /app/scripts/

# Lệnh chạy mặc định
CMD ["python", "scripts/data_generator.py"]