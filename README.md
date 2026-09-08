# Todo (devcontainer + Postgres/pgAdmin + testcontainers + GHCR/Watchtower demo)

A minimal FastAPI Todo app (show / add / complete). The point of this repo isn't the app — it's
the workflow around it:

- **Local dev** happens inside a VS Code [devcontainer](.devcontainer/devcontainer.json). VS Code
  attaches to a single `app` container (the official `mcr.microsoft.com/devcontainers/python`
  image, unrelated to the repo's own [`Dockerfile`](Dockerfile)); a sidecar `db` (Postgres)
  container starts alongside it via
  [`.devcontainer/docker-compose.yml`](.devcontainer/docker-compose.yml), reachable at `db:5432`.
  Docker access (via `docker-outside-of-docker`) lets tests spin up real containers too.
- **Dependencies** are managed with [`uv`](https://docs.astral.sh/uv/).
- **Tests** spin up a real Postgres via [testcontainers](https://testcontainers-python.readthedocs.io/),
  both on your laptop and in CI.
- **CI/CD**: GitHub Actions runs tests on every push/PR; on a green build on `main`, it builds and
  pushes an image to GHCR. Watchtower, running next to the app on a Portainer host, notices the
  new image and redeploys automatically — see [`deploy/README.md`](deploy/README.md).

## Quick start (devcontainer)

VS Code opens a single `app` container; a `db` (Postgres) container starts alongside it
automatically — no manual steps or `.env` needed. `postCreateCommand` runs `uv sync` for you.

1. Open this folder in VS Code, "Reopen in Container" when prompted.
2. Start the app:
   ```
   uv run fastapi dev app/main.py --host 0.0.0.0
   ```
3. Open http://localhost:8000 for the UI, http://localhost:8000/docs for the API.

Migrations run automatically on app startup (see the `lifespan` handler in
[`app/main.py`](app/main.py)), so there's no separate migrate step to remember.

## Quick start (without VS Code)

```
docker compose up --build
```

Runs the full stack (`app` + `db` + `pgadmin`): http://localhost:8000 for the UI,
http://localhost:8000/docs for the API, http://localhost:5050 for pgAdmin (login
`admin@example.com` / `admin`; add a server connecting to host `db`, user/password/db `todo`).
The `app` service bind-mounts the repo so this doubles as a live-reload dev loop.

## Running tests

Inside the devcontainer (or anywhere with Docker + `uv`):

```
uv run pytest
```

[`tests/conftest.py`](tests/conftest.py) starts a real `postgres:18-alpine` container via
testcontainers, runs Alembic migrations against it, and points the app's `get_db` dependency at
it — no mocking, same code path as production. The same tests run in
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) since Docker is available on GitHub-hosted
runners out of the box.

## Project layout

```
app/            FastAPI app: routers (JSON API + HTML), models, schemas, crud
alembic/        DB migrations (async SQLAlchemy)
tests/          pytest + testcontainers
deploy/         Portainer stack file + setup notes
.devcontainer/  devcontainer.json + its own docker-compose.yml (app + db, no pgAdmin)
.github/        CI: test -> build & push to GHCR on green
```

## Database migrations

```
uv run alembic revision -m "describe your change"
uv run alembic upgrade head
```

The app also runs `alembic upgrade head` itself on startup (see `app/main.py`), so migrations
never need a manual step in dev, CI, or on Portainer.
