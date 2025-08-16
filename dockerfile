FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY cookies.txt .   # <-- YE LINE HAMESHA RAHE (order matter nahi, but . ke sath)

CMD ["python", "app.py"]
