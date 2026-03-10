FROM mambaorg/micromamba:1.5

WORKDIR /app

# Copy environment file
COPY environment.yml .

# Create environment
RUN micromamba create -y -n simulation-env -f environment.yml

# Copy source code
COPY src /app/src

VOLUME ["/results"]

# Copy entrypoint
COPY --chmod=755 entrypoint.sh /app/entrypoint.sh

ENTRYPOINT ["micromamba", "run", "-n", "simulation-env", "/app/entrypoint.sh"]