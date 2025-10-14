#!/usr/bin/env python3
"""
Script to run the StyleText API server.
"""
import uvicorn
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)