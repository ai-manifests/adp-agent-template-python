# Multi-stage Python 3.11 build for an ADP agent based on adp-agent.
# Stage 1: build wheels inside a builder image
# Stage 2: install wheels into a minimal runtime image and run non-root

FROM python:3.11-slim AS build
WORKDIR /build

# Copy only metadata first for better layer caching.
COPY pyproject.toml pip.conf ./
COPY src ./src

# Configure pip to read the Gitea PyPI index for @ai-manifests packages.
ENV PIP_CONFIG_FILE=/build/pip.conf

RUN pip install --upgrade pip build && \
    python -m build --wheel --outdir /build/dist

FROM python:3.11-slim AS runtime
WORKDIR /app

# Non-root user for defense in depth.
RUN useradd -u 10001 -m adpagent

COPY --from=build /build/dist/*.whl /tmp/
COPY --from=build /build/pip.conf /etc/pip.conf
ENV PIP_CONFIG_FILE=/etc/pip.conf

RUN pip install --no-cache-dir /tmp/*.whl && rm -f /tmp/*.whl

COPY --chown=10001:10001 agents /app/agents

USER 10001
EXPOSE 3000

ENTRYPOINT ["my-adp-agent", "/app/agents/example.json"]
