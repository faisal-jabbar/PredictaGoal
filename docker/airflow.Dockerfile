FROM apache/airflow:2.8.4-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends gcc git && rm -rf /var/lib/apt/lists/*
USER airflow

# Install project requirements (without airflow itself)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir $(grep -v "apache-airflow" /tmp/requirements.txt | grep -v "^#" | grep -v "^$")

# Copy project source
COPY --chown=airflow:root src/ /opt/airflow/src/
COPY --chown=airflow:root airflow/dags/ /opt/airflow/dags/

ENV PYTHONPATH="/opt/airflow:${PYTHONPATH}"
