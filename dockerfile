FROM python:3.10-slim

# Installiere Systemtools
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Setze Arbeitsverzeichnis
WORKDIR /workspace

# Projektdateien kopieren
COPY requirements.txt .
COPY Tests/lstm-dbscan-test.ipynb /workspace/

# Python-Abhängigkeiten + Jupyter installieren
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install notebook

# Containerstart: Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token="]

