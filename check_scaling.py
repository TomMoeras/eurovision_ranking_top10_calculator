import json

# Read the log file
with open('logs/fixed_scaling.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the JSON part
json_start = content.find('```json') + 7
json_end = content.find('```', json_start)
json_data = content[json_start:json_end]

# Parse the JSON
data = json.loads(json_data)

print("Checking scaling factors in JSON data:")
for participant in data['participants']:
    print(f"\nParticipant: {participant['name']}")
    for system, breakdown in participant['breakdowns'].items():
        scaling_factor = breakdown.get("odds_scaling_factor", "Not found")
        print(f"  System: {system}, odds_scaling_factor: {scaling_factor}")

print("\nChecking country details for first participant:")
for system, breakdown in data['participants'][0]['breakdowns'].items():
    print(f"\nSystem: {system}")
    for detail in breakdown.get('country_details', [])[:2]:  # Show first 2 entries
        if 'explanation' in detail:
            print(f"  Position {detail.get('position')}: {detail.get('explanation')}") 