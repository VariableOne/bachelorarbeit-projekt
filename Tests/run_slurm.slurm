#!/bin/bash
#
#SBATCH --job-name=exec_nb
#SBATCH --output=exec_nb.out
#SBATCH --error=exec_nb.err
#SBATCH --partition=debug
#SBATCH --ntasks=1                   # nur 1 Task
#SBATCH --cpus-per-task=4            # z.B. 4 CPU-Kerne
#SBATCH --mem=16G                    # z.B. 16 GB RAM
#SBATCH --time=04:00:00              # 2 Stunden Laufzeit
# (Passe die Ressourcen je nach Notebook-Anforderungen an)

# ─────────────────────────────────────────────────────────────────
# 1. (Falls nötig) Modul/Conda initialisieren und env aktivieren
# ─────────────────────────────────────────────────────────────────

# Stelle sicher, dass du conda verwenden kannst. Beispiel:
# (Sollte zu eurer lokalen Installation passen; evtl. anpassen, falls Conda anders liegt)
source ~/miniconda3/etc/profile.d/conda.sh

# Aktiviere deine Umgebung namens „env“
conda activate env


# ─────────────────────────────────────────────────────────────────
# 2. Notebook per nbconvert ausführen und in neue Datei schreiben
# ─────────────────────────────────────────────────────────────────

# Hier nehmen wir an, dass dein Notebook „models_isolated.ipynb“ im selben
# Verzeichnis liegt wie dieses Skript. Das Ergebnis landet in „models_executed.ipynb“.

  jupyter nbconvert \
  --to notebook \
  --execute \
  --ExecutePreprocessor.timeout=-1 \
  lstm-dbscan-test.ipynb
# ─────────────────────────────────────────────────────────────────
# Ende des Skripts
# ─────────────────────────────────────────────────────────────────
