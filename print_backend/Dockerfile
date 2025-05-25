# 1. Use an official Python base image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set work directory
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 5. Copy project files
COPY . /app/

# 6. Expose port (if needed for dev/debug)
EXPOSE 8000

# 7. Start the Django app (optional, usually handled in docker-compose)
CMD ["gunicorn", "print_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
