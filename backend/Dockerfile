FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
	postgresql-client \
	gcc \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies directly
RUN pip install --no-cache-dir \
	fastapi==0.104.1 \
	uvicorn[standard]==0.24.0 \
	pydantic==2.5.0 \
	pydantic-settings==2.1.0 \
	sqlalchemy==2.0.23 \
	psycopg2-binary==2.9.9 \
	alembic==1.13.0 \
	bleach==6.1.0 \
	python-jose[cryptography]==3.3.0 \
	passlib[bcrypt]==1.7.4 \
	python-multipart==0.0.6

# Copy application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
