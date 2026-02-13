# FROM python:3.10-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # نصب curl
# RUN apt-get update && apt-get install -y curl

# COPY . .

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.10-slim

# WORKDIR /app

# # نصب پیش‌نیازهای native برای psycopg2 و ابزارهای مفید مثل curl و netcat
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libpq-dev \
#     python3-dev \
#     curl \
#     netcat-openbsd \
#  && rm -rf /var/lib/apt/lists/*


# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# # RUN pip freeze > requirements.lock.txt


# COPY . .

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



FROM python:3.10-slim

WORKDIR /app

# نصب پیش‌نیازهای لازم برای psycopg2 + OpenCV + Zeep + ابزارهای مفید
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    curl \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
