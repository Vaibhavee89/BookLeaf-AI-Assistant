# Docker Setup Guide

This guide explains how to run the BookLeaf AI Assistant using Docker.

## Prerequisites

- **Docker**: Install from https://www.docker.com/get-started
- **Docker Compose**: Usually included with Docker Desktop
- **API Keys**: OpenAI API key and Supabase credentials (already configured in `.env`)

## Quick Start

### Production Mode (Optimized Build)

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Development Mode (Hot Reload)

For development with file watching and hot reload:

```bash
# Build and start in development mode
docker-compose -f docker-compose.dev.yml up --build

# Or run in detached mode
docker-compose -f docker-compose.dev.yml up -d --build

# Stop development services
docker-compose -f docker-compose.dev.yml down
```

## Accessing the Application

Once running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

## Useful Commands

### View Running Containers
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Execute Commands in Containers
```bash
# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Run database seeding
docker-compose exec backend python scripts/seed_data.py

# Run knowledge base preparation
docker-compose exec backend python scripts/prepare_knowledge_base.py
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers, volumes, and images
docker-compose down -v --rmi all

# Remove unused Docker resources
docker system prune -a
```

## Database Seeding

Once Supabase is back online, seed the database:

```bash
# Start the containers
docker-compose up -d

# Wait for services to be healthy (about 30 seconds)

# Seed mock authors (select 'n' when asked to clear existing data)
docker-compose exec backend bash -c "echo 'n' | python scripts/seed_data.py"

# Generate knowledge base embeddings
docker-compose exec backend python scripts/prepare_knowledge_base.py
```

## Environment Variables

The `.env` file at the root contains all required API keys. Docker Compose automatically loads this file.

To modify environment variables:
1. Edit `.env` file
2. Restart the containers: `docker-compose restart`

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use:

```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Container Won't Start
```bash
# View logs for errors
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Database Connection Issues
If Supabase is still experiencing issues:
1. Check https://status.supabase.com
2. Verify your project is not paused in Supabase dashboard
3. Test connection: `curl -I https://frpjbfuslgsirqdjdczy.supabase.co/rest/v1/`

### Permission Denied Errors
```bash
# Linux/Mac: Fix file permissions
sudo chown -R $USER:$USER .
```

### Out of Disk Space
```bash
# Clean up Docker resources
docker system prune -a --volumes
```

## Development Workflow

### Making Code Changes

**Backend Changes:**
- In dev mode: Changes auto-reload
- In production mode: Rebuild with `docker-compose up --build`

**Frontend Changes:**
- In dev mode: Changes auto-reload
- In production mode: Rebuild with `docker-compose up --build`

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=app
```

### Adding New Dependencies

**Backend:**
1. Add package to `backend/requirements.txt`
2. Rebuild: `docker-compose build backend`

**Frontend:**
1. Add package: `docker-compose exec frontend npm install <package>`
2. Or rebuild: `docker-compose build frontend`

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Docker Host                       │
│                                                       │
│  ┌─────────────────┐         ┌──────────────────┐  │
│  │   Frontend      │         │    Backend        │  │
│  │   (Next.js)     │────────▶│   (FastAPI)      │  │
│  │   Port 3000     │         │   Port 8000      │  │
│  └─────────────────┘         └──────────────────┘  │
│                                        │             │
│                                        ▼             │
│                              ┌──────────────────┐   │
│                              │   Supabase       │   │
│                              │   (External)     │   │
│                              └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Production Deployment

For production deployment (AWS, GCP, Azure, etc.):

1. **Build images:**
   ```bash
   docker-compose build
   ```

2. **Tag images:**
   ```bash
   docker tag bookleaf-backend:latest your-registry/bookleaf-backend:latest
   docker tag bookleaf-frontend:latest your-registry/bookleaf-frontend:latest
   ```

3. **Push to registry:**
   ```bash
   docker push your-registry/bookleaf-backend:latest
   docker push your-registry/bookleaf-frontend:latest
   ```

4. **Deploy using your cloud provider's container service**

## Security Notes

- Never commit `.env` file with real API keys to version control
- Use secrets management in production (AWS Secrets Manager, etc.)
- The `.env` file is gitignored by default
- Backend runs as non-root user inside container

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Check Supabase status: https://status.supabase.com
4. Report issues in project repository
