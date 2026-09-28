import re
import json

path = r"C:\Users\rajes\.gemini\antigravity-ide\brain\ee177d13-3eb4-495f-97ba-d81b4e12d3a0\.system_generated\steps\443\content.md"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("File size:", len(text))

# In Google Drive public folder HTML, item lists are often embedded inside JavaScript data arrays:
# e.g., window['_DRIVE_ivd'] = ... or DS_data or similar JSON blobs.
# Let's search for filenames with common extensions
files = set(re.findall(r'[\w\s\-\.\(\)\[\]]+\.(?:pdf|docx|doc|zip|rar|pptx|xlsx|txt|py|java|cpp|html)', text, re.IGNORECASE))
print("Found potential files:", len(files))
for f in sorted(files)[:50]:
    if len(f.strip()) > 3:
        print("  -", f.strip())

# Let's check for folder names or item lists in JavaScript arrays
# Typically: [null, "folder_or_file_id", "Name", ...]
blobs = re.findall(r'\["[a-zA-Z0-9_-]{25,}",\s*"([^"]+)"', text)
print("\nID-Name matches:", len(blobs))
for b in set(blobs):
    print("  - Item:", b)

# Search for any occurrences of company names or placement subjects
keywords = ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini", "Amazon", "Google", "Microsoft", "Deloitte", "Aptitude", "Reasoning", "Verbal", "Quant", "Coding", "DSA", "DBMS", "OS", "CN", "OOPs", "Resume", "Interview", "Cheat", "Operating System", "Computer Networks"]
print("\nKeyword mentions in HTML:")
for kw in keywords:
    count = len(re.findall(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE))
    if count > 0:
        print(f"  {kw}: {count} occurrences")
