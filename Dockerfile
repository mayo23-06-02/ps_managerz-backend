# Dockerfile
FROM python:3.13-slim

# Install system dependencies for pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    odbcinst \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 17 for SQL Server
RUN apt-get update && apt-get install -y curl gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY . .

# Run the app with uvicorn
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8080"]