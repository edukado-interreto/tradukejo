FROM python:3.11-slim-bookworm AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/app \
    PYTHONPATH=/ \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# gettext: to generate Django l10n files
# git: pre-commit checks during testing
# less: Python help() use it
# make: Use of make with Makefile
# vim: for local debugging of packages
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
default-libmysqlclient-dev \
gettext \
git \
less \
make \
vim \
    && apt-get autoremove -y \
    && apt-get clean autoclean \
    && rm -rf /var/lib/apt/lists/*


### STAGE builder-base is used to build dependencies
FROM python-base AS builder-base

# pkg-config: for mysqlclient to compile
RUN apt-get update && apt-get install -y --no-install-recommends \
curl \
build-essential \
pkg-config \
python3-pip

COPY ./requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt


# Stage 3: Development and Testing
FROM python-base AS development

# Copy installed packages from the builder stage
COPY --from=builder-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder-base /usr/local/bin /usr/local/bin
COPY --from=ghcr.io/astral-sh/uv:0.8.24 /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app


# Stage 4: Production
FROM python-base AS production

# Copy installed packages from the builder stage
COPY --from=builder-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder-base /usr/local/bin /usr/local/bin

USER 1030:33

# Copy the project
COPY --chown=1030:33 ./ /app

# Set working directory
WORKDIR /app

RUN SECRET_KEY=_ ./manage.py compilemessages -v0
