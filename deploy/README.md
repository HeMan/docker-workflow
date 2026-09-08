# Deploying to Portainer

This is the "last mile" of the workflow: GitHub Actions builds the image and
pushes it to GHCR on every green build on `main` (see
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml)); Watchtower, running
alongside the app on the Portainer host, notices the new image and redeploys.

## One-time setup

1. **Create the stack in Portainer**, using [`docker-compose.portainer.yml`](./docker-compose.portainer.yml):
   - Easiest: Portainer → Stacks → Add stack → "Repository", point it at this
     GitHub repo, compose path `deploy/docker-compose.portainer.yml`.
   - Or: Stacks → Add stack → "Web editor", paste the file contents.
2. **Set the stack environment variables** (Portainer → your stack → Editor →
   Environment variables):
   - `GHCR_OWNER` — your GitHub username/org (lowercase, must match the image
     CI pushed, e.g. the lowercased `github.repository` owner)
   - `GHCR_REPO` — the repo name (lowercase)
   - Optionally override `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`
     (defaults to `todo`/`todo`/`todo` — fine for a demo, change it for
     anything real).
3. **Registry access.** By default a GHCR package created by Actions is
   private. Either:
   - Make the package public (repo → Packages → the image → Package settings
     → Change visibility), which keeps this demo simple and needs no
     credentials on the Portainer host, **or**
   - Keep it private and add registry credentials: Portainer → Registries →
     Add registry (GHCR, with a GitHub PAT that has `read:packages`), and
     mount equivalent Docker credentials for Watchtower (`~/.docker/config.json`
     into the watchtower container) so it can pull too.
4. Deploy the stack. Portainer pulls the current `:latest` image and starts
   `db`, `app`, and `watchtower`.

## How updates flow after that

1. Push to `main` → CI runs tests → on green, builds & pushes
   `ghcr.io/<owner>/<repo>:latest` (and `:<sha>`).
2. Watchtower polls GHCR every 30s (see the `--interval 30` in the compose
   file). When the `latest` tag's digest changes, it pulls the new image,
   recreates the `app` container, and removes the old image (`--cleanup`).
3. No manual redeploy step, no Portainer webhook needed — this is intentionally
   the simplest version of "deploy on green". If you'd rather redeploy
   immediately instead of waiting up to 30s, you can swap this for a Portainer
   stack webhook called from the GitHub Actions job instead of Watchtower.

`pgAdmin` is intentionally **not** part of this stack — it's a devcontainer/dev
convenience only (see the root [`docker-compose.yml`](../docker-compose.yml)),
not something you'd expose in production.
