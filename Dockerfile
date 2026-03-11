# --- Base Stage (Shared OS dependencies) ---
FROM python:3.13-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN  pip install  --no-cache-dir -r requirements.txt
COPY modules modules 
COPY input input 
COPY scripts scripts
RUN mkdir output

FROM base AS framework_mcs
RUN mkdir output/mcs
CMD ["python", "scripts/Optimization_mcs.py"]

# --- Framework Stage (Heavy Computation) ---
FROM base AS framework_baseline
RUN mkdir output/baseline
CMD ["python", "scripts/Optimization_baseline.py"]

