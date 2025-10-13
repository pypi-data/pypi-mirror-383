FROM public.ecr.aws/docker/library/python:3.13-alpine@sha256:070342a0cc1011532c0e69972cce2bbc6cc633eba294bae1d12abea8bd05303b AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Prefer the system python
ENV UV_PYTHON_PREFERENCE=only-system

# Run without updating the uv.lock file like running with `--frozen`
ENV UV_FROZEN=true

# Python optimization and uv configuration
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and uv
RUN apk update && \
    apk add --no-cache --virtual .build-deps \
        build-base \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev && \
    pip install --no-cache-dir uv

# Copy the required files first
COPY pyproject.toml uv.lock ./

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --python 3.13 --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --python 3.13 --frozen --no-dev --no-editable

# Make the directory just in case it doesn't exist
RUN mkdir -p /root/.local

# Final stage
FROM public.ecr.aws/docker/library/python:3.13-alpine@sha256:070342a0cc1011532c0e69972cce2bbc6cc633eba294bae1d12abea8bd05303b

# Place executables in the environment at the front of the path and include other binaries
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Install runtime dependencies and create application user
RUN apk update && \
    apk add --no-cache ca-certificates && \
    update-ca-certificates && \
    addgroup -S app && \
    adduser -S app -G app -h /app

# Copy application artifacts from build stage (excluding .git for security)
COPY --from=uv --chown=app:app /app/.venv /app/.venv

WORKDIR /app

# Run as non-root
USER app

# Entrypoint for MCP server
ENTRYPOINT ["aws-blackbelt-mcp-server"]
