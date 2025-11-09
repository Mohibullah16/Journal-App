# Complete EC2 Deployment Guide - GitHub Clone Method

This guide walks you through deploying your Journal App on AWS EC2 by:
1. Pushing your code to GitHub
2. Cloning the repository on EC2
3. Creating Docker files directly on EC2
4. Running the containerized application

---

## Part 1: Push Your Code to GitHub

### Step 1: Initialize Git Repository (if not already done)

```powershell
# Navigate to your project directory
cd "c:\Users\mohib\OneDrive - Higher Education Commission\Semester 7\DevOps\Note App\Note App"

# Initialize git (skip if already initialized)
git init

# Check status
git status
```

### Step 2: Create GitHub Repository

1. Go to https://github.com
2. Click the **+** icon → **New repository**
3. **Repository name**: `journal-app` (or any name you prefer)
4. **Visibility**: Public or Private
5. **DO NOT** initialize with README (we already have one)
6. Click **Create repository**

### Step 3: Add Files and Push to GitHub

```powershell
# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Journal App with FastAPI and MongoDB"

# Add GitHub remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/journal-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

If prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (PAT) instead of password
  - Generate PAT: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
  - Select scopes: `repo` (full control)
  - Copy the token and use it as password

**Your code is now on GitHub!** 🎉

---

## Part 2: Setup AWS EC2 Instance

### Step 1: Launch EC2 Instance

1. **Login to AWS Console**: https://console.aws.amazon.com/
2. **Navigate to EC2**: Services → EC2 → Instances → Launch Instance

3. **Configure Instance**:
   - **Name**: `journal-app-server`
   - **AMI**: Ubuntu Server 22.04 LTS (64-bit x86)
   - **Instance type**: t2.micro (Free tier) or t2.small
   - **Key pair**: Create new or select existing
     - If creating new: Download the `.pem` file and save it securely
   
4. **Configure Security Group**:
   - Click "Edit" next to Network settings
   - Add these inbound rules:
   
   | Type       | Protocol | Port | Source    | Description |
   |------------|----------|------|-----------|-------------|
   | SSH        | TCP      | 22   | My IP     | SSH access  |
   | Custom TCP | TCP      | 8000 | 0.0.0.0/0 | App access  |
   | HTTP       | TCP      | 80   | 0.0.0.0/0 | Optional    |

5. **Storage**: 20 GB (recommended)

6. **Launch Instance**

### Step 2: Connect to EC2

```powershell
# From your Windows machine
ssh -i "C:\path\to\your-key.pem" ubuntu@your-ec2-public-ip

# Example:
ssh -i "C:\Users\mohib\Downloads\journal-key.pem" ubuntu@54.123.45.67
```

**Note**: If you get permission error on Windows, you may need to use Git Bash or WSL, or set permissions:
```powershell
icacls "C:\path\to\your-key.pem" /inheritance:r
icacls "C:\path\to\your-key.pem" /grant:r "$($env:USERNAME):(R)"
```

---

## Part 3: Setup EC2 Environment

### All commands below are run on EC2 after SSH connection

### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Docker

```bash
# Install prerequisites
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Verify installation
docker --version

# Add user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER
newgrp docker

# Test Docker
docker run hello-world
```

### Step 3: Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Step 4: Install Git (if not already installed)

```bash
sudo apt-get install -y git
git --version
```

---

## Part 4: Clone Repository and Create Docker Files

### Step 1: Clone Your Repository

```bash
# Clone from GitHub (replace with your repository URL)
git clone https://github.com/yourusername/journal-app.git

# Navigate to project directory
cd journal-app

# List files to verify
ls -la
```

If your repository is private, you'll need to authenticate:
```bash
# Option 1: Use HTTPS with Personal Access Token
git clone https://YOUR_PAT_TOKEN@github.com/yourusername/journal-app.git

# Option 2: Set up SSH key (recommended for repeated access)
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Then clone with SSH
git clone git@github.com:yourusername/journal-app.git
```

### Step 2: Create Dockerfile

```bash
# Create Dockerfile
nano Dockerfile
```

**Paste this content**:

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

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Create docker-compose.yml

```bash
# Create docker-compose.yml
nano docker-compose.yml
```

**Paste this content**:

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

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Create .dockerignore (Optional but Recommended)

```bash
nano .dockerignore
```

**Paste this content**:

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv
.git/
.gitignore
*.md
.env
.env.*
tests/
*.log
.DS_Store
Thumbs.db
```

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

---

## Part 5: Build and Run the Application

### Step 1: Build Docker Images

```bash
# Build the Docker image
docker-compose build

# This will:
# - Pull Python base image
# - Install dependencies
# - Create the application image
```

### Step 2: Start the Application

```bash
# Start all services in detached mode
docker-compose up -d

# Check if containers are running
docker-compose ps
```

Expected output:
```
NAME                 STATUS
journal-mongodb      Up (healthy)
journal-web-app      Up
```

### Step 3: View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f mongodb

# Press Ctrl+C to exit logs
```

---

## Part 6: Test Your Application

### From EC2 (Internal Test)
```bash
# Test if the app responds
curl http://localhost:8000

# You should see HTML response
```

### From Your Browser (External Access)
1. Get your EC2 public IP from AWS Console
2. Open browser and navigate to:
   ```
   http://your-ec2-public-ip:8000
   ```

3. You should see the Journal App login page! 🎉

### Test the Application Features
1. Click "Sign Up" and create an account
2. Login with your credentials
3. Create a journal entry
4. Edit and delete entries
5. Logout and login again to verify data persistence

---

## Part 7: Verify Data Persistence

### Test 1: Restart Containers
```bash
# Stop containers
docker-compose down

# Start again
docker-compose up -d

# Login to your app - all your journals should still be there!
```

### Test 2: Check Volumes
```bash
# List volumes
docker volume ls

# Inspect MongoDB data volume
docker volume inspect journal-app_mongodb_data

# You should see the mount point and size
```

---

## Useful Management Commands

### View Container Status
```bash
docker-compose ps
docker ps
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs -f web
docker-compose logs -f mongodb
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web
```

### Stop Application
```bash
# Stop containers (keeps volumes)
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### Rebuild After Code Changes
```bash
# If you make code changes, rebuild and restart
docker-compose build
docker-compose up -d
```

### Check Resource Usage
```bash
docker stats
```

### Access Container Shell
```bash
# Access web app container
docker exec -it journal-web-app bash

# Access MongoDB container
docker exec -it journal-mongodb mongosh
```

---

## Troubleshooting

### Issue 1: Cannot access application from browser

**Solution**:
```bash
# Check if containers are running
docker-compose ps

# Check logs for errors
docker-compose logs

# Verify EC2 security group allows port 8000
# AWS Console → EC2 → Security Groups → Edit Inbound Rules
```

### Issue 2: Port 8000 already in use

**Solution**:
```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process or change port in docker-compose.yml
# Change: - "8080:8000" to use port 8080 instead
```

### Issue 3: MongoDB connection error

**Solution**:
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb

# Verify MongoDB is healthy
docker exec journal-mongodb mongosh --eval "db.adminCommand('ping')"
```

### Issue 4: Build fails

**Solution**:
```bash
# Check for syntax errors in Dockerfile
cat Dockerfile

# Try building with verbose output
docker-compose build --no-cache

# Check disk space
df -h
```

### Issue 5: Out of disk space

**Solution**:
```bash
# Check disk usage
df -h

# Clean up unused Docker resources
docker system prune -a
docker volume prune

# Remove old containers
docker container prune
```

---

## Backup and Restore

### Backup MongoDB Data

```bash
# Create backup directory
mkdir -p ~/backups

# Backup using mongodump
docker exec journal-mongodb mongodump --username admin --password adminpassword123 --authenticationDatabase admin --out /data/backup

# Copy to host
docker cp journal-mongodb:/data/backup ~/backups/mongodb-backup-$(date +%Y%m%d)

# Or backup entire volume
docker run --rm -v journal-app_mongodb_data:/data -v ~/backups:/backup ubuntu tar czf /backup/mongodb-volume-backup.tar.gz /data
```

### Restore MongoDB Data

```bash
# Copy backup to container
docker cp ~/backups/mongodb-backup-YYYYMMDD journal-mongodb:/data/restore

# Restore using mongorestore
docker exec journal-mongodb mongorestore --username admin --password adminpassword123 --authenticationDatabase admin /data/restore
```

---

## Updating Your Application

### Option 1: Pull Latest Changes from GitHub

```bash
# Stop containers
docker-compose down

# Pull latest code
git pull origin main

# Rebuild and start
docker-compose build
docker-compose up -d
```

### Option 2: Make Changes on EC2

```bash
# Edit files
nano app/main.py

# Rebuild and restart
docker-compose build
docker-compose up -d
```

---

## Assignment Checklist

- [ ] Code pushed to GitHub repository
- [ ] EC2 instance launched with Ubuntu
- [ ] Security group configured (port 8000 open)
- [ ] Docker installed on EC2
- [ ] Docker Compose installed on EC2
- [ ] Repository cloned on EC2
- [ ] Dockerfile created on EC2
- [ ] docker-compose.yml created with persistent volume
- [ ] Application built successfully
- [ ] Containers running (check with `docker-compose ps`)
- [ ] Application accessible via browser
- [ ] Data persistence verified (stop/start test)
- [ ] Screenshots taken:
  - [ ] GitHub repository with your code
  - [ ] EC2 instance running in AWS Console
  - [ ] SSH connection to EC2
  - [ ] `docker-compose ps` output showing running containers
  - [ ] `docker volume ls` showing persistent volumes
  - [ ] Application running in browser with your EC2 IP
  - [ ] Working features (signup, login, create journal)

---

## Quick Command Reference

### Push to GitHub (Local Machine)
```powershell
cd "your-project-path"
git add .
git commit -m "Update application"
git push origin main
```

### EC2 Management
```bash
# Connect to EC2
ssh -i "your-key.pem" ubuntu@ec2-ip

# Navigate to project
cd journal-app

# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Rebuild after changes
docker-compose build && docker-compose up -d
```

---

**You're all set! Your Journal App is now running on AWS EC2 with Docker!** 🚀

Access your app at: `http://your-ec2-public-ip:8000`
