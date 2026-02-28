# 🚀 Quick Start with Docker

Get the BookLeaf AI Assistant running in **under 5 minutes** using Docker!

## Step 1: Prerequisites

Make sure you have Docker installed:
```bash
docker --version
docker-compose --version
```

If not installed, get Docker Desktop: https://www.docker.com/get-started

## Step 2: Start the Application

Choose one of these methods:

### Option A: Using Make (Easiest)

```bash
# Start everything with one command
make up

# Or use quickstart to build, start, and seed database
make quickstart
```

### Option B: Using Docker Compose

```bash
# Build and start all services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 3: Wait for Services to Start

The services take about 30-40 seconds to start. You can monitor with:

```bash
# Watch logs
docker-compose logs -f

# Or check status
make status
```

## Step 4: Access the Application

Once services are running:

- **🌐 Frontend (Chat Interface)**: http://localhost:3000
- **⚡ Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **📖 Alternative Docs**: http://localhost:8000/redoc

## Step 5: Seed the Database (When Supabase is Available)

Once Supabase is back online, seed the database:

```bash
# Using Make
make seed
make prepare-kb

# Or using Docker Compose
docker-compose exec backend bash -c "echo 'n' | python scripts/seed_data.py"
docker-compose exec backend python scripts/prepare_knowledge_base.py
```

## ✅ You're Ready!

The application is now running! Try:

1. Open http://localhost:3000 in your browser
2. Enter your identity (name, email, platform)
3. Ask a question like: "When will I receive my royalty payment?"
4. Watch the AI respond with confidence scoring

## Common Commands

```bash
# Stop services
make down
# or
docker-compose down

# Restart services
make restart

# View logs
make logs

# Clean up everything
make clean

# Development mode (hot reload)
make dev-up
```

## Troubleshooting

### Services won't start?
```bash
# Check logs for errors
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Port already in use?
```bash
# Find what's using port 3000 or 8000
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Database connection errors?
- Check if Supabase is operational: https://status.supabase.com
- Verify your Supabase project is not paused in the dashboard

## Next Steps

- Read [DOCKER_SETUP.md](./DOCKER_SETUP.md) for detailed documentation
- Check the [main README](./README.md) for project architecture
- Explore the API at http://localhost:8000/docs

## Getting Help

Run `make help` to see all available commands!
