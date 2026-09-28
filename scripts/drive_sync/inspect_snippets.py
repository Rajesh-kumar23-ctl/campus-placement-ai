import re

path = r"C:\Users\rajes\.gemini\antigravity-ide\brain\ee177d13-3eb4-495f-97ba-d81b4e12d3a0\.system_generated\steps\443\content.md"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

for kw in ["Infosys", "Accenture", "Cognizant", "Capgemini", "DSA", "CN"]:
    print(f"\n=================== Matches for {kw} ===================")
    for m in re.finditer(r'(.{0,100}' + re.escape(kw) + r'.{0,100})', text, re.IGNORECASE):
        snippet = m.group(1).replace('\n', ' ')
        print("  ...", snippet, "...")
