import json
import random
from datetime import datetime
from events import clean_logs

def parse_time(ts):
    return datetime.fromtimestamp(ts / 1000)  # Wenn Timestamp in ms vorliegt

def add_label_and_filter_normal_logs(normal_file, attack_file, output_file):
    # Normale Logs laden (als Liste von Dicts)
    with open(normal_file, 'r', encoding='utf-8') as f:
        normal_lines = [json.loads(line) for line in f]

    # Letzte 30% der normalen Logs nehmen
    split_idx = int(len(normal_lines) * 0.8)
    normal_sampled = normal_lines[split_idx:]

    # Label hinzufügen (0 für normal)
    for log in normal_sampled:
        log['label'] = 0

    # Attack-Logs laden und labeln (1 für Attack)
    with open(attack_file, 'r', encoding='utf-8') as f:
        attack_lines = [json.loads(line) for line in f]
    for log in attack_lines:
        log['label'] = 1

    # Kombinieren und sortieren nach Zeit
    combined = normal_sampled + attack_lines
    cleaned_combined = clean_logs(combined)
    cleaned_combined.sort(key=lambda x: x['time'])

    # In Datei schreiben
    with open(output_file, 'w', encoding='utf-8') as f:
        for obj in cleaned_combined:
            f.write(json.dumps(obj) + '\n')

    print(f'Fertig! Datei "{output_file}" mit {len(cleaned_combined)} Zeilen erstellt.')

# Beispiel-Aufruf
add_label_and_filter_normal_logs('normallogs_original.jsonl', 'attacks_original.jsonl', 'combined_logs.jsonl')