FROM python:3.9-slim

# Install system dependencies
# gcc/g++ for C++, default-jdk for Java
RUN apt-get update && apt-get install -y \
    build-essential \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
