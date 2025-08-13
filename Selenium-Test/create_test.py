import json
from datetime import datetime
from events import clean_logs

def add_label_and_split_logs(normal_file, attack_file, output_train, output_val, output_test):
    # Normale Logs laden (Liste von Dicts)
    with open(normal_file, 'r', encoding='utf-8') as f:
        normal_lines = [json.loads(line) for line in f]

    # Attack-Logs laden
    with open(attack_file, 'r', encoding='utf-8') as f:
        attack_lines = [json.loads(line) for line in f]

    # Normal Logs sortieren nach Zeit (so wird Reihenfolge erhalten)
    normal_lines.sort(key=lambda x: x['time'])

    n = len(normal_lines)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)  # 70% + 15%

    # Trainingsdaten: 70% normale Logs, Label 0
    train_logs = normal_lines[:train_end]
    for log in train_logs:
        log['label'] = 0

    # Validierungsdaten: nächste 15% normale Logs, Label 0
    val_logs = normal_lines[train_end:val_end]
    for log in val_logs:
        log['label'] = 0

    # Testdaten: letzte 15% normale Logs + alle Attack-Logs
    test_logs = normal_lines[val_end:]
    for log in test_logs:
        log['label'] = 0
    for log in attack_lines:
        log['label'] = 1

    combined_test_logs = test_logs + attack_lines

    # Logs säubern und sortieren (optional, aber empfohlen)
    cleaned_train = clean_logs(train_logs)
    cleaned_val = clean_logs(val_logs)
    cleaned_test = clean_logs(combined_test_logs)

    cleaned_train.sort(key=lambda x: x['time'])
    cleaned_val.sort(key=lambda x: x['time'])
    cleaned_test.sort(key=lambda x: x['time'])

    # Dateien schreiben
    def write_logs(logs, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for obj in logs:
                f.write(json.dumps(obj) + '\n')

    write_logs(cleaned_train, output_train)
    write_logs(cleaned_val, output_val)
    write_logs(cleaned_test, output_test)

    print(f'Trainingsdaten: {len(cleaned_train)} Logs')
    print(f'Validierungsdaten: {len(cleaned_val)} Logs')
    print(f'Testdaten: {len(cleaned_test)} Logs (inkl. Attacken: {len(attack_lines)})')

# Beispiel-Aufruf:
add_label_and_split_logs('getted_normallogs.jsonl', 'attacks_original.jsonl',
                         'train_logs.jsonl', 'val_logs.jsonl', 'test_logs.jsonl')
