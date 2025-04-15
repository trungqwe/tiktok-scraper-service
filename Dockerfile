FROM python:3.10-slim

WORKDIR /app

# Cài đặt Git và các gói phụ thuộc
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    gnupg \
    libgconf-2-4 \
    libxss1 \
    libnss3 \
    libnspr4 \
    libdbus-glib-1-2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Sao chép requirements.txt
COPY requirements.txt .

# Cài đặt các dependencies Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cài đặt Playwright và các trình duyệt
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Sao chép mã nguồn
COPY . .

# Thiết lập biến môi trường mặc định
ENV PORT=8000
ENV DEBUG=True

# Mở cổng
EXPOSE 8000

# Khởi động ứng dụng
CMD ["python", "app.py"]
