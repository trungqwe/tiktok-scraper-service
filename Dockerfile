FROM python:3.10-slim

# Cài đặt dependencies hệ thống
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir git+https://github.com/davidteather/TikTok-Api.git

# Cài đặt Playwright và trình duyệt
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Khởi động application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
