# Journal App - Quick Start Guide

## 🚀 Quick Start (3 Simple Steps)

### Option 1: Automated Setup (Easiest)

```bash
# 1. Clone the repository
git clone https://github.com/Mohibullah16/Journal-App.git
cd Journal-App

# 2. Run the setup script
./setup.sh
```

That's it! The app will be running at http://localhost:8000 🎉

---

### Option 2: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/Mohibullah16/Journal-App.git
cd Journal-App

# 2. (Optional) Create .env file for custom configuration
cp .env.example .env
# Edit .env if you want to customize settings

# 3. Start with Docker Compose
docker compose up -d
```

Access at: http://localhost:8000

---

### Option 3: Pull from Docker Hub

```bash
# Pull the pre-built image
docker pull mohibullah16/journal-app:latest

# Run with docker-compose
docker compose up -d
```

Or run standalone:
```bash
docker run -d \
  -p 8000:8000 \
  -e MONGODB_URL=mongodb://your-mongodb-url:27017 \
  mohibullah16/journal-app:latest
```

---

## 📦 What You Need

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

**No `.env` file required!** The app works out of the box with sensible defaults.

---

## 🔧 Configuration (Optional)

The app works immediately with default settings. To customize:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update:
   - `SECRET_KEY`: Use a secure random key for production
   - `MONGODB_URL`: Your MongoDB connection string
   - `MONGO_INITDB_ROOT_PASSWORD`: Change the default password

3. Restart the services:
   ```bash
   docker compose restart
   ```

---

## 📝 Useful Commands

```bash
# View logs
docker compose logs -f

# View app logs only
docker compose logs -f journal-app

# Stop services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v

# Restart services
docker compose restart

# Check status
docker compose ps

# Rebuild after code changes
docker compose up -d --build
```

---

## 🌐 Docker Hub

**Image:** `mohibullah16/journal-app:latest`

Pull and run anywhere:
```bash
docker pull mohibullah16/journal-app:latest
```

---

## 🛠️ Default Configuration

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `MONGODB_URL` | `mongodb://admin:admin123@mongodb:27017` | MongoDB connection |
| `SECRET_KEY` | `change-this-secret-key-in-production` | JWT secret key |
| `PORT` | `8000` | Application port |
| `MONGO_INITDB_ROOT_USERNAME` | `admin` | MongoDB admin user |
| `MONGO_INITDB_ROOT_PASSWORD` | `admin123` | MongoDB admin password |

⚠️ **For production:** Change the `SECRET_KEY` and MongoDB password!

---

## 🔒 Security Note

The default credentials are for **development only**. For production:

1. Generate a secure secret key:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Update your `.env` file with the new key

3. Change MongoDB credentials

---

## 📚 Documentation

- **Installation Guide:** See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed setup instructions
- **Environment Variables:** See [.env.example](.env.example) for all available options

---

## 🐛 Troubleshooting

### Port 8000 already in use
```bash
# Change the port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Can't connect to MongoDB
```bash
# Check MongoDB logs
docker compose logs mongodb

# Restart MongoDB
docker compose restart mongodb
```

### Container won't start
```bash
# View detailed logs
docker compose logs -f

# Rebuild without cache
docker compose build --no-cache
docker compose up -d
```

---

## 📧 Support

For issues or questions:
- GitHub Issues: [Journal-App Issues](https://github.com/Mohibullah16/Journal-App/issues)
- Docker Hub: [mohibullah16/journal-app](https://hub.docker.com/r/mohibullah16/journal-app)

---

**Made with ❤️ using FastAPI, MongoDB, and Docker**
