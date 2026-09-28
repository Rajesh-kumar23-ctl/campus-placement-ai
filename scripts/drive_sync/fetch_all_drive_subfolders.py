import urllib.request
import re
import json
import time

folders = [
    {"name": "ACCENTURE", "id": "14KY-N173ZGD3P-1PsceLAAl6mf0xplk_"},
    {"name": "AMCAT", "id": "16gkza8e294gPXdmejStqU7F_GwTsx76S"},
    {"name": "Audi Time", "id": "1mLyy6XOAYzHAIwZW32INBeYie8iBc6Hj"},
    {"name": "C & DSA Note", "id": "1s1aOqUgvLBq7FgteB-JAWM6-hypigIa1"},
    {"name": "CAPGEMINI", "id": "1Dge7E_VsA6RtnQDJ7gcJGhnPHvLm6DOj"},
    {"name": "COCUBES", "id": "1jOYtJntH5pAZyLk7jI1EBoFbz-q5hUKE"},
    {"name": "COGNIZANT", "id": "1d5I1KTBJETIPBNBGc8rG1innZCeDG7VI"},
    {"name": "Dell", "id": "1OcqUjgTUCCczyv8xRBNZbofb5rp_B-ce"},
    {"name": "Delloite", "id": "1SbFKmZcr6Xl6b_uSkVof3Qp4Jhl1dK8y"},
    {"name": "ELITMUS", "id": "1A-62aD5UyXv11Dw5vjQ2yXifIJpnG-by"},
    {"name": "EPAM", "id": "1QmZkLXI4uZjGu7kOhjBuIFQGwBlsIPfx"},
    {"name": "HCL", "id": "1PJCcLt4D9Oq4ynap6T5rO2s7_gegiOA2"},
    {"name": "Hexaware", "id": "159wsJZI-xGNEU4dYatZ3_4XxUEIMNbsa"},
    {"name": "HUAWEI TECH", "id": "1Uc83IsPFsouJlgxTTnZEKokAU76qZvwT"},
    {"name": "IBM", "id": "1Abvu_pE7IvLWPhvctLagolCeNkIRLiGj"},
    {"name": "INFOSYS", "id": "16WWF8fq86ERYh7f4npFTGFVaxYM-ZFjh"},
]

results = {}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for fld in folders:
    url = f"https://drive.google.com/drive/folders/{fld['id']}"
    print(f"Fetching {fld['name']} ({url})...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        decoded = html.encode('utf-8').decode('unicode_escape', errors='ignore')

        # Find items parented to this folder: ["<ITEM_ID>",["<fld['id']>"],"<NAME>","<MIME>"
        pattern = r'\["([a-zA-Z0-9_-]{25,})",\s*\["' + re.escape(fld['id']) + r'"\]\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"'
        items = re.findall(pattern, decoded)

        # Also extract aria-labels: aria-label="<NAME> (Shared folder|PDF|Document|etc.)"
        aria_items = re.findall(r'aria-label="([^"]+?)\s+(?:Shared folder|Google Drive (?:PDF|Document|Spreadsheet|Presentation|File)|PDF|Document)"', html)

        sub_items = []
        seen = set()
        for item_id, name, mime in items:
            clean_name = name.replace('\\u0026', '&').replace('\\/', '/')
            if clean_name not in seen:
                seen.add(clean_name)
                sub_items.append({"id": item_id, "name": clean_name, "type": "folder" if "folder" in mime else "file", "mime": mime})

        for a_name in aria_items:
            clean_name = a_name.replace('&amp;', '&').strip()
            if clean_name and clean_name not in seen and not any(k in clean_name for k in ["More actions", "Download", "Grid view", "List view"]):
                seen.add(clean_name)
                sub_items.append({"id": "", "name": clean_name, "type": "resource", "mime": "auto"})

        results[fld['name']] = {
            "id": fld['id'],
            "items_count": len(sub_items),
            "items": sub_items
        }
        print(f" -> Found {len(sub_items)} items in {fld['name']}")
    except Exception as e:
        print(f" -> Error fetching {fld['name']}: {e}")
        results[fld['name']] = {"id": fld['id'], "error": str(e), "items": []}

    time.sleep(0.5)

with open("data/extracted_drive_structure.json", "w", encoding="utf-8") as out:
    json.dump(results, out, indent=2)

print("\nSaved structure to data/extracted_drive_structure.json!")
