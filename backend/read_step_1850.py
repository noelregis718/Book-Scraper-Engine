import json

log_path = r"C:\Users\noelr\.gemini\antigravity\brain\44d2a176-1b47-4fe7-b08b-b7ba0d341193\.system_generated\logs\transcript.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        idx = data.get('step_index')
        if idx in range(1850, 1860) and data.get('source') == 'MODEL' and data.get('content'):
            print(f"STEP {idx}:\n{data.get('content')}\n" + "="*50)
