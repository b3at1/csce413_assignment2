FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends iptables iproute2 \
    && rm -rf /var/lib/apt/lists/*

# There is literally no point in this dockerfile. 
# The secret_ssh container is the one who implements port knocking, so that docker file reflects the knock_server.py requirements. This file is just here to satisfy the docker-compose structure.
