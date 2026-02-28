#!/bin/bash

# Cloudflare Worker Setup Script
# This script helps you deploy the Supabase proxy worker

set -e

echo "=========================================="
echo "Cloudflare Worker Setup"
echo "=========================================="
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI not found!"
    echo ""
    echo "Installing wrangler..."
    npm install -g wrangler
    echo "✅ Wrangler installed!"
    echo ""
fi

# Check if logged in
echo "Checking Cloudflare login status..."
if ! wrangler whoami &> /dev/null; then
    echo "❌ Not logged in to Cloudflare"
    echo ""
    echo "Opening browser for authentication..."
    wrangler login
    echo "✅ Logged in successfully!"
    echo ""
fi

echo "Current Cloudflare account:"
wrangler whoami
echo ""

# Deploy the worker
echo "Deploying Supabase proxy worker..."
echo ""
wrangler deploy
echo ""

echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your worker is now deployed!"
echo ""
echo "Next steps:"
echo "1. Copy the worker URL from above"
echo "2. Update backend/.env:"
echo "   SUPABASE_URL=<your-worker-url>"
echo "3. Restart your Docker containers:"
echo "   docker-compose restart backend"
echo ""
echo "Test your worker:"
echo "curl <your-worker-url>/health"
echo ""
