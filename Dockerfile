# --- Base Stage (Shared OS dependencies) ---
FROM python:3.13-slim AS base
WORKDIR /app
RUN mkdir output
COPY requirements.txt .
RUN  pip install  --no-cache-dir -r requirements.txt
COPY modules . 
COPY scripts .
# Install anything both environments absolutely need

# --- Framework Stage (Heavy Computation) ---
FROM base AS framework_mcs
CMD ["python", "script/Optimization_mcs.py"]

# --- Framework Stage (Heavy Computation) ---
FROM base AS framework_baseline
CMD ["python", "script/Optimization_baseline.py"]

# --- Plotting Stage (Visualization) ---
FROM base AS plotting
# Install LaTeX for high-quality plot fonts, plus plotting libs
COPY plot_scripts .
copy output

# Command reads from /app/results and saves plots to /app/figures
CMD ["python", "src/plots/generate_all_figures.py", "--data_dir", "/app/results", "--out_dir", "/app/figures"]