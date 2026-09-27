# Affaldsviden – Medlemskort

Interaktivt danmarkskort og søgbar kontaktliste over medlemmer af Affaldsviden.
Klik på en kommune for at se, hvilke kommuner og affaldsselskaber der dækker den,
eller søg efter personer, selskaber og fagområder.

> **Demoen kører på fiktive data.** Navne er opdigtede, og e-mail/telefon er `xxxx`.

## Struktur

```
medlemskort/
├── index.html               Siden (henter data fra data/-mappen)
├── data/
│   ├── members.json         Kontakter (kun offentlige felter)
│   ├── orgs.json            Organisation → type + kommunekoder
│   └── kommuner.geojson     Kommunegrænser (98 kommuner)
├── dist/
│   └── medlemskort.html     Samme side som ÉN fil med data indbygget (til deling/WordPress)
├── scripts/
│   ├── build_data.py        Excel → data/*.json
│   ├── bundle.py            index.html + data → dist/medlemskort.html
│   └── generate_dummy.py    Laver det fiktive Excel-ark
└── .gitignore               Sørger for at Excel-filer aldrig kommer på GitHub
```

## Se siden lokalt

- **Nemmest:** dobbeltklik på `dist/medlemskort.html`. Kræver internet (D3 og skrifttypen hentes online).
- **index.html** kan ikke åbnes med dobbeltklik, fordi browseren blokerer indlæsning af data fra disken.
  Kør i stedet i projektmappen:
  ```
  python -m http.server
  ```
  og åbn http://localhost:8000

## Opdatér data

1. Excel-arket skal have to ark: **Superset brugerinformation** (kontakterne) og
   **Organisationer** (kolonnerne Organisation, Type, Kommunekoder).
2. Kør fra projektmappen:
   ```
   python scripts/build_data.py sti/til/arket.xlsx
   python scripts/bundle.py
   ```
3. `build_data.py` udskriver en advarsel for organisationer, der ikke findes i
   Organisationer-arket. De skal rettes, ellers kommer personerne ikke med.

Kun felterne i `FELTER` i `build_data.py` eksporteres (whitelist). Kodeord,
brugernavne og interne noter forlader aldrig din computer.

## Læg den på GitHub Pages

1. Opret et repository og upload **indholdet** af mappen (ikke Excel-filer).
2. Settings → Pages → Source: *Deploy from a branch* → `main` / `(root)` → Save.
3. Efter et par minutter ligger siden på `https://<brugernavn>.github.io/<repo>/`.

Gratis GitHub Pages kræver et offentligt repository – brug derfor kun fiktive data dér.

## Indlejring i WordPress (til IT)

Upload `dist/medlemskort.html` til serveren og indlejr den med en iframe:

```html
<iframe src="/wp-content/uploads/medlemskort.html"
        title="Medlemmer af Affaldsviden"
        style="width:100%; height:85vh; border:0;"></iframe>
```

En iframe anbefales frem for at indsætte koden direkte i en HTML-blok, fordi
sidens CSS så ikke kolliderer med WordPress-temaets.

## Før rigtige data tages i brug

- Gennemgå mappingen organisation → kommuner (arket Organisationer). Den er et udkast.
- Siden skal ligge bag login ligesom den nuværende medlemsside. CSV-eksporten gør det
  let at hente alle kontakter på én gang.
