FROM mambaorg/micromamba:1.5

WORKDIR /app

# Copy environment
COPY environment.yml .

# Create conda environment
RUN micromamba create -y -n simulation-env -f environment.yml

# Copy source code
COPY src /app/src

# Create results directory
VOLUME [ "/results" ]

# Run python directly
ENTRYPOINT ["micromamba", "run", "-n", "simulation-env", "python", "/app/src/main.py"]