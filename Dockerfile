# Stage 1: Build virtual environment with uv
FROM python:3.14-slim AS builder

# Install uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy only the files needed for dependency installation to leverage Docker cache layers
COPY pyproject.toml uv.lock ./

# Synchronize dependencies without compiling the package itself (allows caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY src/ src/
COPY README.md README.md

# Install the project itself in the virtual environment without reinstalling dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-deps .


# Stage 2: Runtime Server Image (warlock-mcp)
FROM python:3.14-slim AS warlock-mcp

WORKDIR /app

# Copy the compiled virtual environment and source code
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Set path to use virtualenv binaries by default
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Default entrypoint starts the FastMCP server
ENTRYPOINT ["python", "-m", "worksbyworrell.warlock.main"]


# Stage 3: Standalone Syncer CLI Image (warlock-mcp-syncer)
FROM python:3.14-slim AS warlock-mcp-syncer

WORKDIR /app

# Copy the compiled virtual environment and source code
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Set path to use virtualenv binaries by default
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Default entrypoint executes the syncer CLI binary
ENTRYPOINT ["warlock-mcp-syncer"]
