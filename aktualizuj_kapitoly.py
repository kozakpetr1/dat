#!/usr/bin/env python3
"""
Aktualizace seznamu kapitol pro rozcestník (index.html).

Použití: ve složce s index.html spusť
    python aktualizuj_kapitoly.py

Skript projde podsložky ročníků (2r, 3r, 4r …), najde v nich soubory
ve tvaru  <číslo>_<název>.html  a z jejich <title> a <meta name="description">
vytvoří soubor kapitoly.js. Pořadí kapitol určuje číslo na začátku názvu souboru.

Nová kapitola = ulož HTML soubor do složky ročníku (např. 3r/5_sql-pohledy.html)
a spusť tento skript znovu.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = re.compile(r"\s+[—–-]\s+VOŠ, SPŠ a SOŠ Varnsdorf\s*$")
# Volitelné podtituly ročníků; ročník, který tu není, se zobrazí bez podtitulu.
PODTITULY = {
    "2r": "Úvod do databází, konceptuální návrh a SQL DML",
    "3r": "Pokročilá práce s databází",
}


def meta(text, pattern):
    m = re.search(pattern, text, re.S | re.I)
    return html.unescape(m.group(1).strip()) if m else ""


def main():
    rocniky = []
    for d in sorted((p for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r"\d+r", p.name)),
                    key=lambda p: int(p.name[:-1])):
        kapitoly = []
        for f in d.glob("*.html"):
            m = re.match(r"(\d+)_", f.name)
            if not m:
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            title = SUFFIX.sub("", meta(text, r"<title>(.*?)</title>")) or f.stem
            desc = meta(text, r'<meta\s+name="description"\s+content="([^"]*)"')
            kapitoly.append({"cislo": int(m.group(1)), "soubor": f"{d.name}/{f.name}",
                             "nazev": title, "popis": desc})
        kapitoly.sort(key=lambda k: k["cislo"])
        if kapitoly:
            rocniky.append({"id": d.name, "nazev": f"{d.name[:-1]}. ročník",
                            "podtitul": PODTITULY.get(d.name, ""), "kapitoly": kapitoly})

    js = ("// Vygenerováno skriptem aktualizuj_kapitoly.py – lze upravit i ručně.\n"
          "// Pořadí kapitol = číslo na začátku názvu souboru.\n"
          "window.ROCNIKY = " + json.dumps(rocniky, ensure_ascii=False, indent=2) + ";\n")
    (ROOT / "kapitoly.js").write_text(js, encoding="utf-8")
    n = sum(len(r["kapitoly"]) for r in rocniky)
    print(f"kapitoly.js: {len(rocniky)} ročníky, {n} kapitol")
    for r in rocniky:
        for k in r["kapitoly"]:
            print(f"  {r['id']}  {k['cislo']:>2}. {k['nazev']}")


if __name__ == "__main__":
    main()
