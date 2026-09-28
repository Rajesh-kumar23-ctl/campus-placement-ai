import re
import html

path = r"C:\Users\rajes\.gemini\antigravity-ide\brain\ee177d13-3eb4-495f-97ba-d81b4e12d3a0\.system_generated\steps\443\content.md"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Pattern 1: aria-label="... Shared folder" or aria-label="... Google Drive"
aria_labels = re.findall(r'aria-label="([^"]+)"', text)
print("=== All aria-labels ===")
for al in set(aria_labels):
    if any(k in al for k in ["folder", "File", "PDF", "Document", "Note", "TCS", "INFOSYS", "ACCENTURE", "COGNIZANT", "CAPGEMINI"]):
        print("Aria:", al)

# Pattern 2: decode \x5b, \x22, \/ etc.
# In Google Drive serialized payloads:
# ["<ITEM_ID>",["1NC5wLHUMUye5_5zHzSgTgXDUdVmh43ZU"],"<ITEM_NAME>","<MIME_TYPE>"
# Let's decode the escaped text first:
decoded = text.encode('utf-8').decode('unicode_escape', errors='ignore')

items = re.findall(r'\["([a-zA-Z0-9_-]{25,})",\s*\["1NC5wLHUMUye5_5zHzSgTgXDUdVmh43ZU"\]\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"', decoded)
print(f"\n=== Found {len(items)} items inside root folder ===")
for item_id, name, mime in items:
    print(f"- ID: {item_id} | Type: {mime} | Name: {name}")

# Also check for any other items in decoded
all_items = re.findall(r'\["([a-zA-Z0-9_-]{25,})",\s*\["[^"]+"\]\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"', decoded)
print(f"\n=== Found {len(all_items)} total items across all decoded payloads ===")
seen = set()
for item_id, name, mime in all_items:
    if name not in seen:
        seen.add(name)
        print(f"- ID: {item_id} | Type: {mime} | Name: {name}")
