# Deployment

## Render Blueprint

The root `render.yaml` uses the multi-stage `Dockerfile`, which performs four build steps:

1. Install Python dependencies.
2. Install locked frontend dependencies.
3. Build the React bundle.
4. Refresh the seven-page knowledge snapshot.

FastAPI serves the generated `frontend/dist` directory and the `/api` routes from one public service.

Required production secret: `DEEPSEEK_API_KEY`. Render generates `REFRESH_TOKEN` from the Blueprint. Never commit either value.

## Docker

The root `Dockerfile` uses a Node build stage and copies only the compiled frontend into the Python runtime image.

