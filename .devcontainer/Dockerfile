FROM python:3.13.2-slim

# Set up a working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (latest version)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# Install Python dependencies
RUN pip install --upgrade pip

# Default command
CMD ["sleep", "infinity"]