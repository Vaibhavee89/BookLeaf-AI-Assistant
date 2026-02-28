"""Vercel serverless function wrapper for FastAPI application."""

from fastapi import FastAPI
from mangum import Mangum
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the FastAPI app
from app.main import app

# Wrap with Mangum for serverless deployment
handler = Mangum(app)
