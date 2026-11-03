import json

log_path = r"C:\Users\noelr\.gemini\antigravity\brain\44d2a176-1b47-4fe7-b08b-b7ba0d341193\.system_generated\logs\transcript.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            content = data.get('content', '')
            print(f"STEP {data.get('step_index')}: {content[:150]}")

