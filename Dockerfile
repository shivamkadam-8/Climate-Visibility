FROM python:3.8.5-slim-buster

# Prevent Python buffering issues
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only requirements first (better caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the project
COPY . .

# Expose Flask port
EXPOSE 5001

# Run Flask app
CMD ["python", "app.py"]
