FROM python:3.14-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy


FROM base AS runtime

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

EXPOSE 8000
CMD ["uv", "run", "--no-sync", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
