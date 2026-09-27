"""
build_data.py – læser medlemsarket og skriver de JSON-filer, siden bruger.

Kør:  python build_data.py Affaldsviden_medlemmer_FIKTIV.xlsx
Output: data/members.json, data/orgs.json

Princip: WHITELIST. Kun de felter der står i FELTER nedenfor kommer med ud.
Alt andet (kodeord, brugernavn, interne noter, orienteringsstatus...) forlader
aldrig din maskine – også selvom der senere kommer nye kolonner i arket.
"""
import json, sys
from pathlib import Path
import pandas as pd

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "Affaldsviden_medlemmer_FIKTIV.xlsx")
OUT = Path("data"); OUT.mkdir(exist_ok=True)

# Excel-kolonne -> nøgle i JSON. Det er KUN disse der eksporteres.
FELTER = {
    "Fornavn": "fornavn",
    "Efternavn": "efternavn",
    "Kommune eller forsyning": "org",
    "Titel": "titel",
    "Titel2": "fagomraade",
    "E-mail": "email",
    "Telefon": "telefon",
}

def clean(v):
    """Tomme celler -> None, så UI'et kan skjule feltet.
    'xxxx' bevares bevidst: demoen skal vise, hvor kontaktinfo kommer til at stå."""
    if pd.isna(v): return None
    s = str(v).strip()
    if s.endswith(".0"): s = s[:-2]          # telefonnumre læst som float
    return None if s in ("", "nan") else s

# --- Organisationer: navn -> type + liste af kommunekoder ---
org_df = pd.read_excel(SRC, sheet_name="Organisationer", dtype=str)
orgs = {}
for _, r in org_df.iterrows():
    koder = [k.strip() for k in str(r["Kommunekoder"]).split(",") if k.strip() and k != "nan"]
    orgs[r["Organisation"]] = {"type": r["Type"], "kommuner": koder}

# --- Medlemmer ---
df = pd.read_excel(SRC, sheet_name="Superset brugerinformation")
df = df.dropna(subset=["Fornavn"])

members, ukendte = [], set()
for i, r in df.iterrows():
    m = {key: clean(r.get(col)) for col, key in FELTER.items()}
    if m["org"] not in orgs:                  # fanger stavefejl/varianter i org-navne
        ukendte.add(m["org"]); continue
    m["id"] = len(members)
    members.append(m)

if ukendte:
    print("ADVARSEL – organisationer uden mapping (sprunget over):", *sorted(ukendte), sep="\n  ")

# separators uden mellemrum = mindre fil
(OUT / "members.json").write_text(json.dumps(members, ensure_ascii=False, separators=(",", ":")), "utf-8")
(OUT / "orgs.json").write_text(json.dumps(orgs, ensure_ascii=False, separators=(",", ":")), "utf-8")

# --- Sanity checks ---
dækket = {k for o in orgs.values() for k in o["kommuner"]}
print(f"{len(members)} medlemmer, {len(orgs)} organisationer, {len(dækket)}/98 kommuner dækket")
print(f"members.json: {(OUT/'members.json').stat().st_size/1024:.0f} KB")
