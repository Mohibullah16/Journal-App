# Quick Commands - Journal App Deployment

## 📋 Summary: GitHub → EC2 → Docker Workflow

This file contains all the essential commands you'll need for deploying your Journal App.

---

## Step 1: Push to GitHub (Local Windows Machine)

```powershell
# Navigate to project
cd "c:\Users\mohib\OneDrive - Higher Education Commission\Semester 7\DevOps\Note App\Note App"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Journal App"

# Add remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/journal-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**✅ Your code is now on GitHub!**

---

## Step 2: Launch EC2 and Connect (AWS Console + Local Machine)

### Launch EC2:
- AMI: Ubuntu 22.04 LTS
- Instance Type: t2.micro
- Security Group: Allow SSH (22) and Custom TCP (8000)
- Download key pair (.pem file)

### Connect from Windows:
```powershell
ssh -i "C:\path\to\your-key.pem" ubuntu@your-ec2-public-ip
```

**✅ You're now connected to EC2!**

---

## Step 3: Install Docker on EC2 (Run on EC2)

Copy and paste these commands one section at a time:

```bash
# Update system
sudo apt-get update

# Install prerequisites
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installations
docker --version
docker-compose --version
```

**✅ Docker installed!**

---

## Step 4: Clone and Setup (Run on EC2)

```bash
# Clone your repository (replace with your GitHub username)
git clone https://github.com/yourusername/journal-app.git

# Navigate to project
cd journal-app

# List files
ls -la
```

**✅ Code cloned to EC2!**

---

## Step 5: Create Dockerfile (Run on EC2)

```bash
nano Dockerfile
```

**Paste this (Ctrl+Shift+V in terminal):**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Save:** `Ctrl+X` → `Y` → `Enter`

---

## Step 6: Create docker-compose.yml (Run on EC2)

```bash
nano docker-compose.yml
```

**Paste this:**

```yaml
version: '3.8'

services:
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
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
    networks:
      - journal-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: journal-web-app
    restart: always
    ports:
      - "8000:8000"
    environment:
      MONGODB_URL: mongodb://admin:adminpassword123@mongodb:27017/journal_app?authSource=admin
    depends_on:
      mongodb:
        condition: service_healthy
    networks:
      - journal-network

volumes:
  mongodb_data:
    driver: local
  mongodb_config:
    driver: local

networks:
  journal-network:
    driver: bridge
```

**Save:** `Ctrl+X` → `Y` → `Enter`

---

## Step 7: Build and Run (Run on EC2)

```bash
# Build the Docker image
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**✅ Application is running!**

---

## Step 8: Access Your App

Open browser and go to:
```
http://your-ec2-public-ip:8000
```

**✅ You should see the Journal App login page!**

---

## Essential Management Commands

### Check Status
```bash
docker-compose ps
docker ps
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f mongodb
```

### Stop Application
```bash
docker-compose down
```

### Start Application
```bash
docker-compose up -d
```

### Restart Application
```bash
docker-compose restart
```

### Rebuild After Changes
```bash
docker-compose build
docker-compose up -d
```

### Check Volumes (Data Persistence)
```bash
docker volume ls
docker volume inspect journal-app_mongodb_data
```

### Monitor Resources
```bash
docker stats
```

---

## Troubleshooting Commands

### Port Already in Use
```bash
sudo lsof -i :8000
sudo lsof -i :27017
```

### Check Disk Space
```bash
df -h
```

### Clean Up Docker
```bash
docker system prune -a
docker volume prune
```

### View Container Details
```bash
docker inspect journal-web-app
docker inspect journal-mongodb
```

### Access Container Shell
```bash
# Web app container
docker exec -it journal-web-app bash

# MongoDB container
docker exec -it journal-mongodb mongosh
```

---

## Verification Checklist

Run these commands to verify everything:

```bash
# 1. Check if containers are running
docker-compose ps

# 2. Check if volumes exist (for data persistence)
docker volume ls | grep journal-app

# 3. Test internal connectivity
curl http://localhost:8000

# 4. Check MongoDB health
docker exec journal-mongodb mongosh --eval "db.adminCommand('ping')"

# 5. View recent logs
docker-compose logs --tail=50
```

---

## Screenshot Commands (For Assignment Submission)

Run these and take screenshots:

```bash
# 1. Show running containers
docker-compose ps

# 2. Show volumes
docker volume ls

# 3. Show container stats
docker stats --no-stream

# 4. Show logs
docker-compose logs --tail=20

# 5. Show Dockerfile content
cat Dockerfile

# 6. Show docker-compose.yml content
cat docker-compose.yml
```

---

## Data Persistence Test

```bash
# 1. Create some journal entries in the app

# 2. Stop containers
docker-compose down

# 3. Start containers again
docker-compose up -d

# 4. Refresh browser - your data should still be there!
```

---

## Update Application (After Code Changes)

```bash
# On local machine: push changes
git add .
git commit -m "Updated application"
git push origin main

# On EC2: pull and rebuild
cd journal-app
git pull origin main
docker-compose build
docker-compose up -d
```

---

## Clean Slate (Start Fresh)

```bash
# WARNING: This deletes everything including data!
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

**Quick Reference Complete!** 🎉

For detailed explanations, see `GITHUB_EC2_DEPLOYMENT.md`
