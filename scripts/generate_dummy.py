"""Genererer et fiktivt medlemsdatasæt med samme kolonner som Superset-deltagerlisten."""
import random, datetime as dt
import pandas as pd

random.seed(42)

# --- De 98 kommuner med officielle kommunekoder (bruges senere til at matche GeoJSON) ---
KOMMUNER = {
 "101":"København","147":"Frederiksberg","151":"Ballerup","153":"Brøndby","155":"Dragør","157":"Gentofte",
 "159":"Gladsaxe","161":"Glostrup","163":"Herlev","165":"Albertslund","167":"Hvidovre","169":"Høje-Taastrup",
 "173":"Lyngby-Taarbæk","175":"Rødovre","183":"Ishøj","185":"Tårnby","187":"Vallensbæk","190":"Furesø",
 "201":"Allerød","210":"Fredensborg","217":"Helsingør","219":"Hillerød","223":"Hørsholm","230":"Rudersdal",
 "240":"Egedal","250":"Frederikssund","253":"Greve","259":"Køge","260":"Halsnæs","265":"Roskilde",
 "269":"Solrød","270":"Gribskov","306":"Odsherred","316":"Holbæk","320":"Faxe","326":"Kalundborg",
 "329":"Ringsted","330":"Slagelse","336":"Stevns","340":"Sorø","350":"Lejre","360":"Lolland",
 "370":"Næstved","376":"Guldborgsund","390":"Vordingborg","400":"Bornholm","410":"Middelfart","420":"Assens",
 "430":"Faaborg-Midtfyn","440":"Kerteminde","450":"Nyborg","461":"Odense","479":"Svendborg","480":"Nordfyns",
 "482":"Langeland","492":"Ærø","510":"Haderslev","530":"Billund","540":"Sønderborg","550":"Tønder",
 "561":"Esbjerg","563":"Fanø","573":"Varde","575":"Vejen","580":"Aabenraa","607":"Fredericia",
 "615":"Horsens","621":"Kolding","630":"Vejle","657":"Herning","661":"Holstebro","665":"Lemvig",
 "671":"Struer","706":"Syddjurs","707":"Norddjurs","710":"Favrskov","727":"Odder","730":"Randers",
 "740":"Silkeborg","741":"Samsø","746":"Skanderborg","751":"Aarhus","756":"Ikast-Brande","760":"Ringkøbing-Skjern",
 "766":"Hedensted","773":"Morsø","779":"Skive","787":"Thisted","791":"Viborg","810":"Brønderslev",
 "813":"Frederikshavn","820":"Vesthimmerland","825":"Læsø","840":"Rebild","846":"Mariagerfjord","849":"Jammerbugt",
 "851":"Aalborg","860":"Hjørring",
}
NAVN2KODE = {v: k for k, v in KOMMUNER.items()}
assert len(KOMMUNER) == 98

# --- Forsyninger/selskaber og hvilke kommuner de dækker (UDKAST – skal verificeres internt) ---
FORSYNINGER = {
 "AffaldPlus": ["Faxe","Næstved","Slagelse","Sorø","Vordingborg"],
 "AFLD": ["Hedensted","Varde","Billund","Herning","Ikast-Brande"],
 "ARC": ["København","Frederiksberg","Dragør","Tårnby","Hvidovre"],
 "Argo": ["Roskilde","Lejre","Egedal","Frederikssund","Greve","Solrød","Høje-Taastrup","Holbæk","Stevns","Køge"],
 "Arwos": ["Aabenraa"],
 "Assens Forsyning": ["Assens"],
 "Billund Vand & Energi": ["Billund"],
 "BOFA": ["Bornholm"],
 "DIN Forsyning": ["Esbjerg","Varde"],
 "Favrskov Forsyning": ["Favrskov"],
 "Fors": ["Holbæk","Lejre","Roskilde"],
 "Forsyning Helsingør": ["Helsingør"],
 "Forsyningen Frederikshavn": ["Frederikshavn"],
 "Fredensborg Forsyning": ["Fredensborg"],
 "Glostrup Forsyning": ["Glostrup"],
 "Gribskov Forsyning": ["Gribskov"],
 "Halsnæs Forsyning": ["Halsnæs"],
 "Hillerød Forsyning": ["Hillerød"],
 "HTK Forsyning": ["Høje-Taastrup"],
 "Kerteminde Forsyning": ["Kerteminde"],
 "KLAR Forsyning": ["Greve","Solrød","Køge"],
 "Kredsløb": ["Aarhus"],
 "Langeland Forsyning": ["Langeland"],
 "Lyngby-Taarbæk Forsyning": ["Lyngby-Taarbæk"],
 "Mariagerfjord Ren Forsyning": ["Mariagerfjord"],
 "Middelfart Affald og Genbrug": ["Middelfart"],
 "Nomi4s": ["Holstebro","Lemvig","Skive","Struer"],
 "Nordværk": ["Aalborg","Brønderslev","Hjørring","Jammerbugt","Rebild"],
 "Nyborg Forsyning & Service": ["Nyborg"],
 "Odense Renovation": ["Odense"],
 "Provas": ["Haderslev"],
 "REFA": ["Guldborgsund","Lolland"],
 "Reno Djurs": ["Norddjurs","Syddjurs"],
 "Renosyd": ["Skanderborg","Odder"],
 "Revas": ["Viborg"],
 "Rødovre Affald og Genbrug": ["Rødovre"],
 "Silkeborg Forsyning": ["Silkeborg"],
 "Sonfor": ["Sønderborg"],
 "Svendborg Vand & Affald": ["Svendborg"],
 "Thy Recycle": ["Thisted"],
 "Tønder Forsyning": ["Tønder"],
 "Vesthimmerland Forsyning": ["Vesthimmerland"],
 "Vestforbrænding": ["Albertslund","Allerød","Ballerup","Brøndby","Furesø","Gentofte","Gladsaxe",
                     "Glostrup","Herlev","Ishøj","Lyngby-Taarbæk","Rudersdal","Rødovre","Vallensbæk"],
 "Ærø Forsyning": ["Ærø"],
}
UDEN_GEOGRAFI = ["KL", "DAKOFA", "Brancheforeningen Cirkulær", "JHN Processor"]

# --- Organisationstabel: én række pr. organisation ---
orgs = []
for k in KOMMUNER.values():
    navn = "Københavns Kommune" if k == "København" else f"{k} Kommune"
    orgs.append((navn, "Kommune", [k]))
for navn, dk in FORSYNINGER.items():
    for k in dk: assert k in NAVN2KODE, k
    orgs.append((navn, "Forsyning/selskab", dk))
for navn in UDEN_GEOGRAFI:
    orgs.append((navn, "Organisation (landsdækkende)", []))

# --- Fiktive navne og titler ---
FORNAVNE = ("Anders Anne Mette Lars Hanne Jens Susanne Peter Kirsten Søren Lene Morten Camilla Rasmus Louise "
            "Mads Julie Thomas Sofie Martin Ida Jesper Maria Henrik Line Niels Emma Kasper Signe Jakob Pernille "
            "Christian Rikke Frederik Katrine Mikkel Tina Simon Helle Nikolaj Maja Ole Birgitte Troels Astrid "
            "Kristian Nanna Bo Charlotte Esben Marianne Anders Laura Jonas Trine Bjarke Malene Lasse Dorthe").split()
EFTERNAVNE = ("Jensen Nielsen Hansen Pedersen Andersen Christensen Larsen Sørensen Rasmussen Jørgensen Petersen "
              "Madsen Kristensen Olsen Thomsen Poulsen Johansen Møller Mortensen Knudsen Holm Lund Østergaard "
              "Dahl Bach Friis Kjær Vestergaard Skov Mikkelsen Frederiksen Lauridsen Damgaard Bruun Winther "
              "Kirkegaard Nørgaard Toft Brandt Ravn Juhl Iversen Bak Lindberg").split()
TITLER = {
 "Kommune": ["Miljømedarbejder","Affaldsplanlægger","Specialkonsulent","Miljøkoordinator","Teamleder, Affald",
             "Fagchef, Natur og Miljø","Projektleder","Miljøsagsbehandler","Data- og analysekonsulent","Affaldskonsulent"],
 "Forsyning/selskab": ["Udviklingskonsulent","Driftsleder","Kommunikationskonsulent","Teamleder genbrugsplads",
             "Dataanalytiker","Projektleder, Cirkulær økonomi","Affaldsrådgiver","Kundeservicechef",
             "Controller","Direktør","Driftsplanlægger","Formidling og udvikling"],
 "Organisation (landsdækkende)": ["Chefkonsulent","Seniorkonsulent","Analytiker","Sekretariatsleder","Studentermedhjælper"],
}
FAGOMRAADER = ["Husholdningsaffald","Genbrugspladser","Erhvervsaffald","Data og statistik","Kommunikation",
               "Affaldsplanlægning","Indsamling og ordninger","Tekstiler","Farligt affald","Cirkulær økonomi"]
TILBAGEMELDING = ["Leveret","Leveret","Leveret","Afventer svar","Kan ikke leveres","Ny kontaktperson oplyst"]

def n_medlemmer(orgtype, n_kommuner):
    if orgtype == "Kommune": return random.randint(1, 5)
    if orgtype.startswith("Organisation"): return random.randint(2, 6)
    return min(18, random.randint(3, 7) + n_kommuner)  # større selskaber = flere brugere

rows, brugt = [], set()
for orgnavn, orgtype, dk in orgs:
    for _ in range(n_medlemmer(orgtype, len(dk))):
        while True:  # undgå dubletnavne på tværs af datasættet
            fn, en = random.choice(FORNAVNE), random.choice(EFTERNAVNE)
            if random.random() < 0.2: en = f"{random.choice(EFTERNAVNE)} {en}"
            if (fn, en) not in brugt: brugt.add((fn, en)); break
        oprettet = dt.date(2019, 6, 1) + dt.timedelta(days=random.randint(0, 2350))
        orienteret = random.random() < 0.8
        roller = "Deltagende Kommuner" + (", " + ", ".join(dk) if dk and orgtype != "Kommune" else
                                          (f", {dk[0]}" if dk else ""))
        rows.append({
            "Antal": None,
            "Kommune eller forsyning": orgnavn,
            "Fornavn": fn, "Efternavn": en,
            "Brugernavn": "xxxx", "Kodeord": "xxxx", "E-mail": "xxxx",
            "Tilbagemeldinger (SGT, nov 2025)": random.choice(TILBAGEMELDING),
            "Titel": random.choice(TITLER[orgtype]),
            "Telefon": "xxxx",
            "Orienteret 1 ud af 2": "X" if orienteret else None,
            "Orienteret 2 ud af 2": "X" if orienteret and random.random() < 0.9 else None,
            "Oprettet dato": oprettet,
            "Roller": roller,
            "Titel2": random.choice(FAGOMRAADER),
            "Kolonne1": oprettet.strftime("%d.%m.%Y"),
        })

df = pd.DataFrame(rows).sort_values(["Kommune eller forsyning", "Fornavn", "Efternavn"]).reset_index(drop=True)
df["Antal"] = range(1, len(df) + 1)

org_df = pd.DataFrame([{
    "Organisation": o, "Type": t,
    "Kommuner": ", ".join(dk),
    "Kommunekoder": ", ".join(NAVN2KODE[k] for k in dk),
    "Antal medlemmer": int((df["Kommune eller forsyning"] == o).sum()),
} for o, t, dk in orgs]).sort_values(["Type", "Organisation"])

kom_df = pd.DataFrame([{"Kommunekode": k, "Kommune": v} for k, v in KOMMUNER.items()])

out = "Affaldsviden_medlemmer_FIKTIV.xlsx"
with pd.ExcelWriter(out, engine="openpyxl", date_format="YYYY-MM-DD") as xw:
    df.to_excel(xw, sheet_name="Superset brugerinformation", index=False)
    org_df.to_excel(xw, sheet_name="Organisationer", index=False)
    kom_df.to_excel(xw, sheet_name="Kommuner", index=False)

# --- Formatering: Arial, fed header, frys øverste række, autofilter, kolonnebredder ---
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
wb = load_workbook(out)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row: c.font = Font(name="Arial", size=10, bold=(c.row == 1),
                                    color="FFFFFF" if c.row == 1 else "000000")
    for c in ws[1]: c.fill = PatternFill("solid", fgColor="5B8C3A")
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    for col in ws.columns:
        w = max(len(str(c.value or "")) for c in col[:200])
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 8), 60)
wb.save(out)

print(len(df), "medlemmer,", len(orgs), "organisationer")
print(org_df["Type"].value_counts().to_string())
# Tjek: har alle 98 kommuner mindst ét medlem?
dækket = set(k for dk in [o[2] for o in orgs] for k in dk)
print("Kommuner dækket:", len(dækket), "/ 98")
