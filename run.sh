#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install the required packages
pip install -r requirements.txt

# Create .env file from .env.example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please edit it with your specific settings."
fi

echo "Setup complete. Activate the virtual environment with 'source venv/bin/activate'."