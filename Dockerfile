# Python 3.12 tabanlı bir Docker image kullanıyoruz
FROM python:3.12-slim

# Uygulama çalışma dizinini belirliyoruz
WORKDIR /app

# Gereksinim dosyasını kopyalıyoruz
COPY requirements.txt .

# Gereksinimlerin yüklenmesi
RUN pip install --no-cache-dir -r requirements.txt

# Bot kodunu konteynıra kopyalıyoruz
COPY bot.py .

# Bot'u başlatıyoruz
CMD ["python", "bot.py"]
