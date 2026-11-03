import json

log_path = r"C:\Users\noelr\.gemini\antigravity\brain\44d2a176-1b47-4fe7-b08b-b7ba0d341193\.system_generated\logs\transcript.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        idx = data.get('step_index')
        if idx in range(1958, 1978):
            calls = data.get('tool_calls', [])
            for c in calls:
                print(f"STEP {idx} tool: {c.get('name')} -> {str(c.get('args'))[:200]}")
            if data.get('source') == 'MODEL' and data.get('type') == 'PLANNER_RESPONSE' and not calls:
                content = data.get('content', '')
                if content:
                    print(f"STEP {idx} MODEL:\n{content.encode('ascii', errors='replace').decode()[:500]}\n")
