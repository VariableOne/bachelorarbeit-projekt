import json
import random

def add_label_and_filter_normal_logs(normal_file, attack_file, output_file):
    # normallogs.jsonl: nur letzte 20% Zeilen lesen
    with open(normal_file, 'r', encoding='utf-8') as f:
        normal_lines = f.readlines()
    cutoff = int(len(normal_lines) * 0.9)
    normal_last_20 = normal_lines[cutoff:]

    # normallogs: label 0 hinzufügen
    normal_labeled = []
    for line in normal_last_20:
        obj = json.loads(line)
        obj['label'] = 0
        normal_labeled.append(obj)

    # attack.jsonl: ganze Datei, label 1 hinzufügen
    with open(attack_file, 'r', encoding='utf-8') as f:
        attack_lines = f.readlines()
    attack_labeled = []
    for line in attack_lines:
        obj = json.loads(line)
        obj['label'] = 1
        attack_labeled.append(obj)

    # Beide Listen mischen
    combined = normal_labeled + attack_labeled
    random.shuffle(combined)

    # In output_file speichern
    with open(output_file, 'w', encoding='utf-8') as f:
        for obj in combined:
            f.write(json.dumps(obj) + '\n')

    print(f'Fertig! Datei "{output_file}" mit {len(combined)} Zeilen erstellt.')

# Beispiel-Aufruf
add_label_and_filter_normal_logs('normallogs.jsonl', 'attacks.jsonl', 'combined_logs.jsonl')
