# =============================================================================
# yasched — container image. Multi-stage: build the SPA, then a slim runtime.
#
# NOTE: `docker build` pulls base images and installs packages, so it needs
# network access ONCE at build time. The running container makes no outbound
# calls and binds only to the port you map. For a fully offline path after
# initial setup, use `./run.sh` instead.
#
#   docker build -t yasched .
#   docker run --rm -p 8000:8000 -v "$PWD/data:/data" yasched
# =============================================================================

# ---- Stage 1: build the React frontend --------------------------------------
FROM node:20-alpine AS web
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

# ---- Stage 2: python runtime ------------------------------------------------
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install the package (core deps include fastapi + uvicorn).
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

# Resources (personal template) + the built SPA from stage 1.
COPY resources ./resources
COPY --from=web /web/dist ./apps/web/dist

ENV YASCHED_AGENDA=/data/agenda.yaml \
    YASCHED_WEB_DIST=/app/apps/web/dist
EXPOSE 8000

# On first run create the agenda from the template, then serve on all
# interfaces (so the mapped host port works). Still local to your machine.
CMD ["sh", "-c", "[ -f \"$YASCHED_AGENDA\" ] || yasched init --agenda \"$YASCHED_AGENDA\"; exec yasched serve --agenda \"$YASCHED_AGENDA\" --host 0.0.0.0 --port 8000"]
