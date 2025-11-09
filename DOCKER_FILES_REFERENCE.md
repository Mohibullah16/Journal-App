# Docker Files Reference - To Create on EC2

## These files will be created DIRECTLY on your EC2 instance after cloning from GitHub

---

## File 1: Dockerfile

**Command to create:**
```bash
nano Dockerfile
```

**Content to paste:**
```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## File 2: docker-compose.yml

**Command to create:**
```bash
nano docker-compose.yml
```

**Content to paste:**
```yaml
version: '3.8'

services:
  # MongoDB Database Service
  mongodb:
    image: mongo:7.0
    container_name: journal-mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: adminpassword123
      MONGO_INITDB_DATABASE: journal_app
    ports:
      - "27017:27017"
    volumes:
      # Persistent volume for MongoDB data
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
    networks:
      - journal-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Web Application Service
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: journal-web-app
    restart: always
    ports:
      - "8000:8000"
    environment:
      # MongoDB connection string
      MONGODB_URL: mongodb://admin:adminpassword123@mongodb:27017/journal_app?authSource=admin
    depends_on:
      mongodb:
        condition: service_healthy
    networks:
      - journal-network

# Named volumes for data persistence
volumes:
  mongodb_data:
    driver: local
  mongodb_config:
    driver: local

# Network for container communication
networks:
  journal-network:
    driver: bridge
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## File 3: .dockerignore (Optional but Recommended)

**Command to create:**
```bash
nano .dockerignore
```

**Content to paste:**
```
# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/
.venv

# IDE specific files
.vscode/
.idea/
*.swp
*.swo
*~

# Git files
.git/
.gitignore
.gitattributes

# Documentation
*.md

# Environment files
.env
.env.*

# Logs
*.log

# OS files
.DS_Store
Thumbs.db

# Elastic Beanstalk
.ebextensions/
.ebignore
*.zip
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## Explanation of Key Configuration

### Dockerfile Explained:
- **FROM python:3.11-slim** - Lightweight Python base image
- **WORKDIR /app** - Sets working directory inside container
- **ENV PYTHONDONTWRITEBYTECODE=1** - Prevents Python from writing .pyc files
- **ENV PYTHONUNBUFFERED=1** - Ensures Python output is sent straight to terminal
- **RUN apt-get install gcc** - Installs compiler needed for some Python packages
- **COPY requirements.txt** - Copies dependencies file
- **RUN pip install** - Installs all Python dependencies
- **COPY . .** - Copies entire application code
- **EXPOSE 8000** - Documents that container listens on port 8000
- **CMD ["uvicorn"...]** - Command to start FastAPI application

### docker-compose.yml Explained:

#### MongoDB Service:
- **image: mongo:7.0** - Uses official MongoDB 7.0 image
- **MONGO_INITDB_ROOT_USERNAME/PASSWORD** - Sets admin credentials
- **ports: 27017:27017** - Exposes MongoDB port
- **volumes: mongodb_data:/data/db** - ⭐ **PERSISTENT STORAGE** - Data survives container restarts
- **networks: journal-network** - Connects to custom network
- **healthcheck** - Ensures MongoDB is ready before starting web app

#### Web Service:
- **build: context: .** - Builds from Dockerfile in current directory
- **ports: 8000:8000** - Maps port 8000 from container to host
- **MONGODB_URL** - Connection string to MongoDB
- **depends_on: mongodb** - Waits for MongoDB to be healthy before starting
- **networks: journal-network** - Connects to same network as MongoDB

#### Volumes:
- **mongodb_data** - ⭐ **PERSISTENT VOLUME** - Stores actual database data
- **mongodb_config** - Stores MongoDB configuration

#### Networks:
- **journal-network** - Private network for containers to communicate

---

## Why This Setup Meets Assignment Requirements

✅ **Dockerfile**: Creates container image for web application  
✅ **docker-compose.yml**: Orchestrates multi-container application  
✅ **Persistent Volume**: `mongodb_data` volume attached to database container  
✅ **Data Persistence**: Data survives container stops/starts/restarts  
✅ **Network Isolation**: Containers communicate on private network  
✅ **Health Checks**: Ensures database is ready before app starts  
✅ **Environment Variables**: Configuration separated from code  
✅ **Restart Policy**: Containers automatically restart on failure  

---

## Testing Data Persistence

After deployment, test that data persists:

```bash
# 1. Create some journal entries in the app

# 2. Stop all containers
docker-compose down

# 3. Verify volumes still exist
docker volume ls

# 4. Start containers again
docker-compose up -d

# 5. Refresh browser - your data should still be there!
```

---

## Customization Options

### Change MongoDB Password:
In docker-compose.yml, change:
```yaml
MONGO_INITDB_ROOT_PASSWORD: your-secure-password-here
```

And in MONGODB_URL:
```yaml
MONGODB_URL: mongodb://admin:your-secure-password-here@mongodb:27017/...
```

### Change Application Port:
In docker-compose.yml web service:
```yaml
ports:
  - "8080:8000"  # Access on port 8080 instead of 8000
```

### Add More Memory to MongoDB:
```yaml
mongodb:
  # ... existing config ...
  command: --wiredTigerCacheSizeGB 0.5
```

---

## File Locations After Creation

```
/home/ubuntu/journal-app/
├── Dockerfile                 ← You create this on EC2
├── docker-compose.yml         ← You create this on EC2
├── .dockerignore             ← You create this on EC2 (optional)
├── app/                      ← From GitHub
├── static/                   ← From GitHub
├── templates/                ← From GitHub
├── requirements.txt          ← From GitHub
├── application.py            ← From GitHub
└── README.md                 ← From GitHub
```

---

## Quick Reference: File Creation on EC2

```bash
# After cloning repository
cd journal-app

# Create all Docker files
nano Dockerfile           # Copy content from above
nano docker-compose.yml   # Copy content from above
nano .dockerignore        # Copy content from above (optional)

# Build and run
docker-compose build
docker-compose up -d

# Verify
docker-compose ps
```

---

**Keep this file open as reference when creating files on EC2!**
