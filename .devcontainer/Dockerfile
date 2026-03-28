# Dockerfile for the SystemsDevTeam4 Dev Container
#
# Base image: Microsoft's official Dev Container Python image.
# Using python-3.12 gives us a stable, recent Python with all common
# developer tools pre-installed (git, curl, sudo, etc.).
FROM mcr.microsoft.com/devcontainers/python:3.12

# Install any extra OS-level packages you need below.
# sqlite3 is already bundled with Python's standard library, but the CLI
# tool is handy for quick debugging inside the container.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the image and install dependencies.
# This layer is cached as long as requirements.txt does not change.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# The workspace is mounted at /workspaces/<repo-name> at runtime;
# no COPY of source code is needed here.
