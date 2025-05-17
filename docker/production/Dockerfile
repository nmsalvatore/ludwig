FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# install system dependencies required for psycopg
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy dependency specifications
COPY pyproject.toml uv.lock /app/

# install dependencies without installing project
RUN uv sync --locked --extras production --no-install-project

# copy the rest of the project
COPY . /app/

# install the project
RUN uv sync --locked --extras production

# expose the port
EXPOSE 8000

# run gunicorn
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
