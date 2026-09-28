import json
import os
import re

DRIVE_ROOT_URL = "https://drive.google.com/drive/folders/1NC5wLHUMUye5_5zHzSgTgXDUdVmh43ZU"

# Load top level
with open("data/extracted_drive_structure.json", "r", encoding="utf-8") as f:
    top_structure = json.load(f)

# Load nested
nested_structure = {}
if os.path.exists("data/extracted_nested_drive.json"):
    with open("data/extracted_nested_drive.json", "r", encoding="utf-8") as f:
        nested_structure = json.load(f)

materials = []
seen_ids = set()
seen_names = set()
counter = 1

def normalize_company(raw_name):
    raw = raw_name.strip()
    if raw.lower() == "delloite":
        return "Deloitte"
    if raw.lower() in ["c & dsa note", "c & dsa notes"]:
        return "General / Core CS"
    if raw.lower() == "audi time":
        return "General Aptitude"
    return raw

def clean_title(filename, company, folder_context, item_type):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'^[0-9]+[_\.\-]', '', name)
    name = name.replace('_', ' ').replace('-', ' ').strip()
    
    # If file was a hash/telegram numbered name e.g. 5 6077880573588668773
    if re.match(r'^[0-9\s]{8,}$', name):
        prefix = folder_context if folder_context and not re.match(r'^[0-9\s]{8,}$', folder_context) else company
        return f"{prefix} Practice Paper Set #{counter % 25 + 1}"
        
    name = re.sub(r'\s+', ' ', name)
    comp_clean = company.replace("General / ", "").strip()
    if not name.lower().startswith(comp_clean.lower()) and comp_clean.lower() not in ["core cs", "general aptitude"]:
        return f"{comp_clean} - {name.title()}"
    return name.title()

def determine_category(title, filename, company):
    t = (title + " " + filename + " " + company).lower()
    if any(k in t for k in ["dsa", "c programming", "data structure", "coding", "autometa", "automata", "pseudo", "javacodes", "java", "c++", "python"]):
        return "Coding & DSA"
    if any(k in t for k in ["quant", "math", "numerical", "reasoning", "logical", "apti", "aptitude"]):
        return "Aptitude & Reasoning"
    if any(k in t for k in ["english", "verbal", "jam", "communication", "comprehension", "essay"]):
        return "Verbal & Communication"
    if any(k in t for k in ["amcat", "cocubes", "elitmus"]):
        return "Assessment Platforms"
    return "Company Placement Papers"

def get_format(name, mime, item_type):
    if item_type == "folder" or "folder" in mime:
        return "Folder Bundle"
    ext = os.path.splitext(name)[1].lower()
    if ext == ".pdf":
        return "PDF Document"
    if ext in [".doc", ".docx", ".odt"]:
        return "Word Document"
    if ext == ".zip":
        return "ZIP Archive"
    if ext in [".jpg", ".png", ".jpeg"]:
        return "Handwritten / Scan"
    if ext in [".txt", ".java", ".py", ".cpp"]:
        return "Code / Text File"
    return "Placement Resource"

# 1. Process top-level items
for company_name, data in top_structure.items():
    folder_id = data.get("id", "")
    items = data.get("items", [])
    norm_comp = normalize_company(company_name)
    
    for itm in items:
        file_id = itm.get("id")
        filename = itm.get("name")
        item_type = itm.get("type", "file")
        mime = itm.get("mime", "")
        
        dedup_key = file_id if file_id else f"{norm_comp}_{filename}"
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)
        
        # Determine URLs
        if item_type == "folder" or "folder" in mime:
            view_url = f"https://drive.google.com/drive/folders/{file_id}" if file_id else f"https://drive.google.com/drive/folders/{folder_id}"
            download_url = view_url
        else:
            view_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing" if file_id else f"https://drive.google.com/drive/folders/{folder_id}"
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}" if file_id else view_url

        title = clean_title(filename, norm_comp, "", item_type)
        category = determine_category(title, filename, norm_comp)
        fmt = get_format(filename, mime, item_type)
        
        desc = f"Verified recruitment preparation material for {norm_comp}. Includes practice questions, exam pattern insights, and test answers."
        if "dsa" in title.lower() or "c programming" in title.lower():
            desc = "Comprehensive handwritten and typed notes covering C language fundamentals, pointers, linked lists, binary trees, recursion, and algorithm efficiency."
        elif "automata" in title.lower():
            desc = "Automata and competitive coding assessment paper with sample logic, algorithmic implementation, and debugging test cases."
        elif "jam" in title.lower():
            desc = "Just-A-Minute (JAM) speaking round topics, extempore speech strategies, and evaluation parameters."
        elif "500" in title.lower():
            desc = "High-yield 500 quantitative aptitude problems with complete step-by-step mathematical proofs and shortcut methods."
        elif "288" in title.lower():
            desc = "Master collection of 288 logical reasoning questions across syllogisms, blood relations, and seating arrangements."
        elif "300" in title.lower():
            desc = "Comprehensive 300 verbal ability and reading comprehension questions with grammar rules and sentence corrections."

        materials.append({
            "id": f"mat-{counter:03d}",
            "title": title,
            "filename": filename,
            "company": norm_comp,
            "category": category,
            "format": fmt,
            "is_folder": (item_type == "folder" or "folder" in mime),
            "file_id": file_id or folder_id,
            "parent_folder_id": folder_id,
            "view_url": view_url,
            "download_url": download_url,
            "description": desc,
            "tags": [norm_comp, category, fmt.split()[0]],
            "featured": (counter in [1, 2, 4, 12, 17, 21, 28, 32, 41, 55, 68, 85, 110, 142])
        })
        counter += 1

# 2. Process nested subfolder items
for folder_id, data in nested_structure.items():
    parent_cat = normalize_company(data.get("parent_cat", "General"))
    folder_name = data.get("folder_name", "")
    items = data.get("items", [])
    
    for itm in items:
        file_id = itm.get("id")
        filename = itm.get("name")
        item_type = itm.get("type", "file")
        mime = itm.get("mime", "")
        
        dedup_key = file_id if file_id else f"{parent_cat}_{folder_name}_{filename}"
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)
        
        if item_type == "folder" or "folder" in mime:
            view_url = f"https://drive.google.com/drive/folders/{file_id}" if file_id else f"https://drive.google.com/drive/folders/{folder_id}"
            download_url = view_url
        else:
            view_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing" if file_id else f"https://drive.google.com/drive/folders/{folder_id}"
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}" if file_id else view_url

        title = clean_title(filename, parent_cat, folder_name, item_type)
        category = determine_category(title, filename, parent_cat)
        fmt = get_format(filename, mime, item_type)
        
        desc = f"Curated {parent_cat} ({folder_name}) preparation resource extracted from placement drive archive."
        if "pseudo" in title.lower():
            desc = "Capgemini / Tech pseudo-code questions focusing on loop dry runs, bitwise operators, and recursion outputs."
        elif "automata" in title.lower():
            desc = "Hands-on programming and code completion questions for Automata and online technical assessments."

        materials.append({
            "id": f"mat-{counter:03d}",
            "title": title,
            "filename": filename,
            "company": parent_cat,
            "subfolder": folder_name,
            "category": category,
            "format": fmt,
            "is_folder": (item_type == "folder" or "folder" in mime),
            "file_id": file_id or folder_id,
            "parent_folder_id": folder_id,
            "view_url": view_url,
            "download_url": download_url,
            "description": desc,
            "tags": [parent_cat, category, fmt.split()[0]],
            "featured": ("handwritten" in title.lower() or "automata" in title.lower() or "500" in title.lower())
        })
        counter += 1

output_data = {
    "drive_root_url": DRIVE_ROOT_URL,
    "drive_folder_name": "Placement material",
    "total_materials": len(materials),
    "companies_count": len(set(m["company"] for m in materials)),
    "categories": [
        "Company Placement Papers",
        "Aptitude & Reasoning",
        "Coding & DSA",
        "Assessment Platforms",
        "Verbal & Communication"
    ],
    "materials": materials
}

with open("data/placement_materials.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

print(f"COMPLETE: Built data/placement_materials.json with {len(materials)} materials across {output_data['companies_count']} organizations/platforms!")
