# Stage 1 – build dependencies with uv
FROM docker.abrha.net/python:3.13-slim-bookworm AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
# Force uv to copy files instead of hardlinking to avoid cross-device issues in Docker
ENV UV_LINK_MODE=copy 

# Install uv using pip since we aren't using the official uv image
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev


# Stage 2 – production runtime
FROM docker.abrha.net/python:3.13-slim-bookworm


# RUN rm -f /etc/apt/sources.list.d/* /etc/apt/sources.list && \
#     echo "deb http://mirror.shatel.ir/debian/ bookworm main" > /etc/apt/sources.list && \
#     echo "deb http://mirror.shatel.ir/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
#     echo "deb http://mirror.shatel.ir/debian-security bookworm-security main" >> /etc/apt/sources.list

    # echo "deb https://repo.abrha.net/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    # echo "deb https://repo.abrha.net/debian bookworm-updates main contrib non-free" > /etc/apt/sources.list && \
    # echo "deb https://repo.abrha.net/debian bookworm-backports main contrib non-free" > /etc/apt/sources.list && \
    # echo "deb https://repo.abrha.net/debian-security bookworm-security main contrib non-free" > /etc/apt/sources.list

RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash django
WORKDIR /app

COPY --from=builder --chown=django:django /app/.venv /app/.venv
COPY --chown=django:django . /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY --chown=django:django entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER django

ENTRYPOINT ["/app/entrypoint.sh"]