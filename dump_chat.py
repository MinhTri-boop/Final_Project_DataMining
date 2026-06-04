import json

with open(r'C:\Users\Acer\.gemini\antigravity\brain\76fb2b56-cf9e-4533-8b31-0da11a62329f\.system_generated\logs\transcript.jsonl', encoding='utf-8') as f:
    lines = f.readlines()

output = []
for l in lines:
    data = json.loads(l)
    if data.get('type') in ('USER_INPUT', 'PLANNER_RESPONSE', 'TEXT_OUTPUT'):
        output.append(f"[{data.get('type')}] {data.get('content', '')}")

with open('temp_full_chat.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n====================\n\n'.join(output))
