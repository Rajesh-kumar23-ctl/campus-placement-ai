import json
import urllib.request
import re
import time

with open("data/extracted_drive_structure.json", "r", encoding="utf-8") as f:
    structure = json.load(f)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

nested_folders = []
for cat, data in structure.items():
    for itm in data.get("items", []):
        if itm.get("type") == "folder" and itm.get("id"):
            nested_folders.append({
                "parent_cat": cat,
                "name": itm["name"],
                "id": itm["id"]
            })

print(f"Found {len(nested_folders)} nested subfolders to inspect.")
nested_results = {}

for nf in nested_folders:
    url = f"https://drive.google.com/drive/folders/{nf['id']}"
    print(f"Fetching nested: {nf['parent_cat']} -> {nf['name']} ({nf['id']})...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        decoded = html.encode('utf-8').decode('unicode_escape', errors='ignore')

        pattern = r'\["([a-zA-Z0-9_-]{25,})",\s*\["' + re.escape(nf['id']) + r'"\]\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"'
        items = re.findall(pattern, decoded)

        seen = set()
        sub_items = []
        for item_id, name, mime in items:
            clean = name.replace('\\u0026', '&').replace('\\/', '/')
            if clean not in seen:
                seen.add(clean)
                sub_items.append({"id": item_id, "name": clean, "type": "folder" if "folder" in mime else "file", "mime": mime})

        nested_results[nf["id"]] = {
            "parent_cat": nf["parent_cat"],
            "folder_name": nf["name"],
            "count": len(sub_items),
            "items": sub_items
        }
        print(f" -> Found {len(sub_items)} items in {nf['name']}")
    except Exception as e:
        print(f" -> Error: {e}")
    time.sleep(0.5)

with open("data/extracted_nested_drive.json", "w", encoding="utf-8") as out:
    json.dump(nested_results, out, indent=2)

print("\nSaved nested results to data/extracted_nested_drive.json!")
