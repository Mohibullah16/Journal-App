# Journal App

A simple and beautiful note-taking journal application built with FastAPI, MongoDB, HTML, and CSS. Fully containerized with Docker for easy deployment on AWS EC2.

## Features

- 🔐 User Authentication (Login/Signup)
- 📝 Create, Read, Update, Delete journal entries
- 🎨 Modern and responsive UI
- 💾 MongoDB for data persistence
- 🔒 JWT-based authentication
- 🐳 Docker & Docker Compose ready
- ☁️ AWS EC2 deployment ready

## Prerequisites

### For Docker Deployment (Recommended)
- Docker (20.10 or higher)
- Docker Compose (1.29 or higher)
- Docker Hub account (for pushing images)
- AWS EC2 instance (for cloud deployment)

### For Local Development
- Python 3.8 or higher
- MongoDB installed and running locally (or a MongoDB connection string)

## Deployment with Docker on AWS EC2

This application is designed to be deployed on AWS EC2 using Docker. The recommended workflow is:

1. **Push code to GitHub**
2. **Launch AWS EC2 instance**
3. **Clone repository on EC2**
4. **Create Docker files on EC2**
5. **Build and run with Docker Compose**

### Complete Deployment Guide

See **`GITHUB_EC2_DEPLOYMENT.md`** for detailed step-by-step instructions including:
- Pushing your code to GitHub
- Setting up AWS EC2 instance
- Installing Docker and Docker Compose on EC2
- Creating Dockerfile and docker-compose.yml on EC2
- Building and running the containerized application
- Testing and troubleshooting

### Quick Overview

```bash
# On EC2 (after cloning from GitHub):
# 1. Create Dockerfile and docker-compose.yml
# 2. Build and start containers
docker-compose build
docker-compose up -d

# 3. Access application
# Open browser: http://your-ec2-public-ip:8000
```



## Local Development (Without Docker)

### Installation

1. **Install MongoDB** (if not already installed):
   - Download from https://www.mongodb.com/try/download/community
   - Follow installation instructions for your OS
   - Start MongoDB service

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The application is configured to connect to MongoDB using the `MONGODB_URL` environment variable.

**Important Security Note**: 
- Change the `SECRET_KEY` in `app/main.py` before deploying to production
- Current key is for development only

### Running the Application

1. **Start MongoDB** (if not running):
   - Windows: MongoDB should start automatically as a service
   - Mac: `brew services start mongodb-community`
   - Linux: `sudo systemctl start mongod`

2. **Set environment variable**:
   ```bash
   # Linux/Mac
   export MONGODB_URL="mongodb://localhost:27017/journal_app"
   
   # Windows PowerShell
   $env:MONGODB_URL="mongodb://localhost:27017/journal_app"
   ```

3. **Run the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload
   ```

   Or simply:
   ```bash
   python -m app.main
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## Usage

1. **Sign Up**: Create a new account with your email, username, and password
2. **Login**: Sign in with your credentials
3. **Create Journals**: Click "New Journal" to add a journal entry
4. **Edit Journals**: Click "Edit" on any journal card to modify it
5. **Delete Journals**: Click "Delete" to remove a journal (with confirmation)
6. **Logout**: Click the logout button in the navigation bar

## API Endpoints

### Authentication
- `POST /api/signup` - Create a new user account
- `POST /api/login` - Login and receive JWT token

### Journals (Protected)
- `GET /api/journals` - Get all journals for authenticated user
- `POST /api/journals` - Create a new journal entry
- `PUT /api/journals/{journal_id}` - Update a journal entry
- `DELETE /api/journals/{journal_id}` - Delete a journal entry

### Web Pages
- `GET /` - Login page (redirect)
- `GET /login` - Login page
- `GET /signup` - Signup page
- `GET /main` - Main dashboard (requires authentication)

## Project Structure

```
journal-app/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and routes
│   ├── database.py       # MongoDB connection
│   └── models.py         # Pydantic models
├── static/
│   └── css/
│       └── style.css     # Styling
├── templates/
│   ├── login.html        # Login page
│   ├── signup.html       # Signup page
│   └── main.html         # Main dashboard
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Multi-container Docker application
├── .dockerignore         # Files to exclude from Docker image
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Technologies Used

- **Backend**: FastAPI, Python
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens, bcrypt password hashing
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Templating**: Jinja2
- **Containerization**: Docker, Docker Compose
- **Cloud Platform**: AWS EC2

## Docker Configuration Details

### Dockerfile Features
- Multi-stage build with Python 3.11-slim base image
- Optimized layer caching for faster builds
- Non-root user for security (production ready)
- Health checks enabled
- Minimal image size

### Docker Compose Services
- **Web Application**: FastAPI application on port 8000
- **MongoDB Database**: MongoDB 7.0 with authentication
- **Persistent Volumes**: 
  - `mongodb_data`: Stores MongoDB database files
  - `mongodb_config`: Stores MongoDB configuration
- **Network**: Isolated bridge network for service communication
- **Health Checks**: Ensures MongoDB is ready before starting web app

### Volume Persistence
The MongoDB data is stored in a named Docker volume (`mongodb_data`), which means:
- Data persists even when containers are stopped or removed
- Can be backed up using `docker run --rm -v mongodb_data:/data -v $(pwd):/backup ubuntu tar czf /backup/mongodb-backup.tar.gz /data`
- Can be restored if needed

## Development

To run in development mode with auto-reload:

### With Docker:
```bash
docker-compose up
```

### Without Docker:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Protected API endpoints
- Client-side token storage
- XSS protection through HTML escaping
- MongoDB authentication enabled in Docker setup
- Isolated container network

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   # Linux/Mac
   lsof -i :8000
   # Windows
   netstat -ano | findstr :8000
   
   # Change port in docker-compose.yml
   ports:
     - "8080:8000"  # Use 8080 instead
   ```

2. **Container fails to start**
   ```bash
   # Check container logs
   docker-compose logs web
   docker-compose logs mongodb
   
   # Restart containers
   docker-compose restart
   ```

3. **MongoDB connection issues**
   - Ensure MongoDB container is running: `docker-compose ps`
   - Check MongoDB health: `docker-compose logs mongodb`
   - Verify connection string in environment variables

4. **Permission denied on EC2**
   ```bash
   # If you get permission errors, add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

5. **Cannot access application from browser (EC2)**
   - Check EC2 security group allows inbound traffic on port 8000
   - Verify application is running: `docker-compose ps`
   - Check if firewall is blocking: `sudo ufw status`

## Backup and Restore

### Backup MongoDB Data
```bash
# Create backup directory
mkdir -p backups

# Backup MongoDB volume
docker run --rm \
  -v mongodb_data:/data \
  -v $(pwd)/backups:/backup \
  ubuntu tar czf /backup/mongodb-backup-$(date +%Y%m%d-%H%M%S).tar.gz /data
```

### Restore MongoDB Data
```bash
# Stop containers
docker-compose down

# Restore from backup
docker run --rm \
  -v mongodb_data:/data \
  -v $(pwd)/backups:/backup \
  ubuntu bash -c "cd /data && tar xzf /backup/mongodb-backup-YYYYMMDD-HHMMSS.tar.gz --strip 1"

# Start containers
docker-compose up -d
```

## Monitoring

### Check Container Resource Usage
```bash
# View real-time stats
docker stats

# View specific container
docker stats journal-web-app journal-mongodb
```

### Check Container Health
```bash
# Check all containers
docker-compose ps

# Inspect specific container
docker inspect journal-mongodb | grep Health -A 10
```

## Updating the Application

1. **Make code changes**
2. **Rebuild and restart**:
   ```bash
   docker-compose up -d --build
   ```
3. **Or rebuild specific service**:
   ```bash
   docker-compose build web
   docker-compose up -d web
   ```

## Future Enhancements

- Search and filter journals
- Tags/categories for journals
- Rich text editor
- Export journals to PDF
- Dark mode toggle
- Mobile app version
- Kubernetes deployment
- CI/CD pipeline with GitHub Actions
- SSL/TLS certificate configuration
- Load balancing for multiple instances

## License

This project is open source and available for personal and educational use.

## Support

For issues or questions, please create an issue in the repository.

## Assignment Completion Checklist

- ✅ Dockerfile created for web application
- ✅ docker-compose.yml created with web app and database services
- ✅ Persistent volume attached to MongoDB container
- ✅ Docker image can be pushed to Docker Hub
- ✅ Application can be deployed on AWS EC2
- ✅ Complete deployment documentation provided

