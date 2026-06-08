#!/usr/bin/env python3
"""Genera index.html (standalone) per il Torneo dei Rioni 3vs3 a partire da dati_torneo.json.

Flusso single-source-of-truth: dati_torneo.json -> genera.py -> index.html

Uso:
    python3 genera.py                      # rigenera index.html
    python3 genera.py --input-dir <dir>    # legge dati_torneo.json da <dir>
    python3 genera.py --output-dir <dir>   # scrive index.html in <dir>

Nessuna dipendenza esterna: l'HTML prodotto è autosufficiente (CSS+JS inline) e funziona offline.
"""

import argparse
import html
import json
from pathlib import Path

# ════════════════════════════════════════════════════════════════════════════
#  CARICAMENTO DATI
# ════════════════════════════════════════════════════════════════════════════

def load_data(input_dir: Path) -> dict:
    with open(input_dir / "dati_torneo.json", encoding="utf-8") as f:
        return json.load(f)


def squadre_per_nome(dati: dict) -> dict:
    return {s["nome"]: s for s in dati.get("squadre", [])}


def colore_rione(dati: dict, rione: str) -> str:
    for r in dati.get("rioni", []):
        if r["nome"] == rione:
            return r.get("colore", "#888888")
    return "#888888"


# ════════════════════════════════════════════════════════════════════════════
#  CLASSIFICA (regole FIBA 3x3: vittoria 2 pti, sconfitta 0)
# ════════════════════════════════════════════════════════════════════════════

def calcola_classifica(dati: dict, girone_code: str) -> list:
    """Classifica di un girone iterando sulle partite con fase == f'Girone {girone_code}'
    e giocata == True. Ritorna lista di dict ordinata."""
    squadre = [s for s in dati.get("squadre", []) if s.get("girone") == girone_code]
    stats = {
        s["nome"]: {"nome": s["nome"], "rione": s["rione"], "G": 0, "V": 0, "P": 0,
                    "PF": 0, "PS": 0, "Pti": 0}
        for s in squadre
    }

    for p in dati.get("partite", []):
        if p.get("fase") != f"Girone {girone_code}" or not p.get("giocata"):
            continue
        s1, s2 = p.get("squadra1"), p.get("squadra2")
        if s1 not in stats or s2 not in stats:
            continue
        pt1, pt2 = p.get("punti1", 0), p.get("punti2", 0)
        for s, pf, ps in ((s1, pt1, pt2), (s2, pt2, pt1)):
            stats[s]["G"] += 1
            stats[s]["PF"] += pf
            stats[s]["PS"] += ps
        if pt1 > pt2:
            stats[s1]["V"] += 1; stats[s1]["Pti"] += 2; stats[s2]["P"] += 1
        elif pt2 > pt1:
            stats[s2]["V"] += 1; stats[s2]["Pti"] += 2; stats[s1]["P"] += 1

    classifica = list(stats.values())
    classifica.sort(key=lambda r: (r["Pti"], r["PF"] - r["PS"], r["PF"]), reverse=True)
    return classifica


def gironi_disponibili(dati: dict) -> list:
    codici = sorted({s["girone"] for s in dati.get("squadre", []) if s.get("girone")})
    return codici


# ════════════════════════════════════════════════════════════════════════════
#  HTML
# ════════════════════════════════════════════════════════════════════════════

def esc(s) -> str:
    return html.escape(str(s), quote=True)


def render_hero(t: dict) -> str:
    return f"""
  <header class="hero">
    <div class="hero-bg"></div>
    <div class="hero-inner">
      <p class="hero-kicker">{esc(t.get('manifestazione', ''))}</p>
      <h1 class="hero-title">{esc(t['nome'])}</h1>
      <div class="hero-3v3">{esc(t.get('sottotitolo', '3 vs 3'))}</div>
      <p class="hero-place">{esc(t['luogo'])}</p>
      <p class="hero-dates">{esc(t['date'])}</p>
      <p class="hero-edition">{esc(t['edizione'])}ª edizione</p>
    </div>
  </header>"""


def render_nav() -> str:
    voci = [
        ("squadre", "Squadre"),
        ("gironi", "Gironi"),
        ("calendario", "Calendario"),
        ("finali", "Finali"),
        ("info", "Info"),
    ]
    links = "".join(f'<a href="#{a}">{esc(t)}</a>' for a, t in voci)
    return f'<nav class="nav"><div class="nav-inner">{links}</div></nav>'


def render_squadre(dati: dict) -> str:
    sqs = dati.get("squadre", [])
    rioni_ordine = [r["nome"] for r in dati.get("rioni", [])]
    by_rione = {}
    for s in sqs:
        by_rione.setdefault(s["rione"], []).append(s)

    cards = []
    for rione in rioni_ordine:
        col = colore_rione(dati, rione)
        squadre_rione = by_rione.get(rione, [])
        if not squadre_rione:
            cards.append(f"""
      <article class="rione-card vuoto" style="--c:{col}">
        <div class="rione-head"><span class="rione-dot"></span><h3>{esc(rione)}</h3></div>
        <p class="rione-todo">Roster da comunicare</p>
      </article>""")
            continue
        squadre_html = ""
        for s in sorted(squadre_rione, key=lambda x: x.get("lettera", "")):
            giocatori = "".join(f"<li>{esc(g)}</li>" for g in s.get("giocatori", []))
            girone_badge = (f'<span class="g-badge">Girone {esc(s["girone"])}</span>'
                            if s.get("girone") else "")
            squadre_html += f"""
        <div class="squadra">
          <div class="squadra-head"><h4>{esc(s['nome'])}</h4>{girone_badge}</div>
          <ol class="roster">{giocatori}</ol>
        </div>"""
        cards.append(f"""
      <article class="rione-card" style="--c:{col}">
        <div class="rione-head"><span class="rione-dot"></span><h3>{esc(rione)}</h3></div>
        {squadre_html}
      </article>""")

    n_sq = len(sqs)
    return f"""
  <section id="squadre" class="section">
    <h2 class="section-title">Squadre &amp; Rioni</h2>
    <p class="section-sub">{n_sq} squadre iscritte · {len(rioni_ordine)} rioni</p>
    <div class="rioni-grid">{''.join(cards)}</div>
  </section>"""


def render_gironi(dati: dict) -> str:
    codici = gironi_disponibili(dati)
    if not codici:
        return """
  <section id="gironi" class="section">
    <h2 class="section-title">Gironi &amp; Classifica</h2>
    <div class="placeholder">
      <p>🎲 Sorteggio dei gironi non ancora effettuato.</p>
      <p class="muted">2 gironi da 4 squadre. Le squadre A e B dello stesso rione finiranno in gironi diversi.</p>
    </div>
  </section>"""

    blocchi = []
    for code in codici:
        classifica = calcola_classifica(dati, code)
        righe = ""
        for i, r in enumerate(classifica, 1):
            col = colore_rione(dati, r["rione"])
            dc = r["PF"] - r["PS"]
            dc_str = f"+{dc}" if dc > 0 else str(dc)
            pos = i if r["G"] > 0 else "–"
            righe += f"""
          <tr>
            <td class="pos">{pos}</td>
            <td class="team"><span class="dot" style="background:{col}"></span>{esc(r['nome'])}</td>
            <td>{r['G']}</td><td>{r['V']}</td><td>{r['P']}</td>
            <td>{r['PF']}</td><td>{r['PS']}</td><td>{dc_str}</td>
            <td class="pti">{r['Pti']}</td>
          </tr>"""
        blocchi.append(f"""
      <div class="girone-block">
        <h3 class="girone-title">Girone {esc(code)}</h3>
        <table class="classifica">
          <thead><tr>
            <th>#</th><th>Squadra</th><th>G</th><th>V</th><th>P</th>
            <th>PF</th><th>PS</th><th>±</th><th>Pti</th>
          </tr></thead>
          <tbody>{righe}</tbody>
        </table>
      </div>""")

    return f"""
  <section id="gironi" class="section">
    <h2 class="section-title">Gironi &amp; Classifica</h2>
    <div class="gironi-grid">{''.join(blocchi)}</div>
  </section>"""


def render_calendario(dati: dict) -> str:
    partite = dati.get("partite", [])
    if not partite:
        return """
  <section id="calendario" class="section">
    <h2 class="section-title">Calendario</h2>
    <div class="placeholder">
      <p>📅 Calendario in preparazione.</p>
      <p class="muted">12 partite di girone su 10–11–12 giugno · semifinali 13 giugno · finali 14 giugno.</p>
    </div>
  </section>"""

    giorni = dati.get("giorni", {})
    by_giorno = {}
    for p in partite:
        by_giorno.setdefault(p.get("giorno"), []).append(p)

    blocchi = []
    for gcode in sorted(by_giorno):
        rows = ""
        for p in sorted(by_giorno[gcode], key=lambda x: x.get("ora", "")):
            s1, s2 = esc(p.get("squadra1", "—")), esc(p.get("squadra2", "—"))
            if p.get("giocata"):
                ris = f'<span class="ris">{p.get("punti1", 0)} - {p.get("punti2", 0)}</span>'
            else:
                ris = '<span class="ris vs">vs</span>'
            rows += f"""
          <tr>
            <td class="ora">{esc(p.get('ora', ''))}</td>
            <td class="match"><span>{s1}</span>{ris}<span>{s2}</span></td>
            <td class="fase">{esc(p.get('fase', ''))}</td>
          </tr>"""
        blocchi.append(f"""
      <div class="giorno-block">
        <h3 class="giorno-title">{esc(giorni.get(gcode, gcode))}</h3>
        <table class="calendario"><tbody>{rows}</tbody></table>
      </div>""")

    return f"""
  <section id="calendario" class="section">
    <h2 class="section-title">Calendario</h2>
    {''.join(blocchi)}
  </section>"""


def render_finali(dati: dict) -> str:
    fasi_finali = ["Semifinale 1", "Semifinale 2", "Finale 3°/4°", "Finalissima 1°/2°"]
    partite = {p.get("fase"): p for p in dati.get("partite", [])
               if p.get("fase") in fasi_finali}
    if not partite:
        return """
  <section id="finali" class="section">
    <h2 class="section-title">Tabellone Finale</h2>
    <div class="placeholder">
      <p>🏆 Tabellone delle finali.</p>
      <p class="muted">Semifinali (13 giu): 1°A–2°B e 1°B–2°A · Finali (14 giu): 3°/4° e finalissima 1°/2°.</p>
    </div>
  </section>"""

    def slot(fase, label):
        p = partite.get(fase)
        if not p:
            return f'<div class="bracket-match"><span class="bm-label">{esc(label)}</span><span class="bm-team">da definire</span></div>'
        s1, s2 = esc(p.get("squadra1", "—")), esc(p.get("squadra2", "—"))
        if p.get("giocata"):
            res = f'{p.get("punti1",0)}-{p.get("punti2",0)}'
        else:
            res = p.get("ora", "")
        return f'<div class="bracket-match"><span class="bm-label">{esc(label)}</span><span class="bm-team">{s1} <em>{esc(res)}</em> {s2}</span></div>'

    return f"""
  <section id="finali" class="section">
    <h2 class="section-title">Tabellone Finale</h2>
    <div class="bracket">
      {slot('Semifinale 1', 'Semifinale · 1°A – 2°B')}
      {slot('Semifinale 2', 'Semifinale · 1°B – 2°A')}
      {slot('Finale 3°/4°', '🥉 Finale 3°/4°')}
      {slot('Finalissima 1°/2°', '🏆 Finalissima 1°/2°')}
    </div>
  </section>"""


def render_info(dati: dict) -> str:
    imp = dati.get("impianto", {})
    reg = dati.get("regole", {})
    t = dati.get("torneo", {})
    regole_items = "".join(
        f"<li><strong>{esc(k.replace('_',' ').capitalize())}:</strong> {esc(v)}</li>"
        for k, v in reg.items()
    )
    return f"""
  <section id="info" class="section">
    <h2 class="section-title">Info</h2>
    <div class="info-grid">
      <div class="info-card">
        <h3>📍 Dove si gioca</h3>
        <p class="big">{esc(imp.get('nome',''))}</p>
        <p>{esc(imp.get('tipo',''))}</p>
        <p class="muted">{esc(imp.get('indirizzo',''))}</p>
        <p>{esc(imp.get('descrizione',''))}</p>
        <a class="maps-btn" href="{esc(imp.get('maps_url','#'))}" target="_blank" rel="noopener">Apri su Google Maps →</a>
      </div>
      <div class="info-card">
        <h3>📋 Regole</h3>
        <ul class="regole">{regole_items}</ul>
      </div>
    </div>
    <p class="org">Organizzato da <strong>{esc(t.get('organizzatore',''))}</strong> · in collaborazione con <strong>{esc(t.get('in_collaborazione_con',''))}</strong></p>
  </section>"""


CSS = """
:root{
  --bg:#0d0e13; --bg2:#15161d; --card:#191b24; --card2:#1f212c;
  --red:#c01f33; --blue:#1c3a8f; --orange:#e8732a; --gold:#f1c40f;
  --txt:#f3f4f7; --muted:#9aa0ad; --line:#2a2d3a;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif;
  background:var(--bg);color:var(--txt);line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:inherit}
.section{max-width:1100px;margin:0 auto;padding:48px 18px}
.section-title{font-size:1.9rem;font-weight:900;letter-spacing:.5px;text-transform:uppercase;
  border-left:6px solid var(--red);padding-left:14px;margin-bottom:6px}
.section-sub{color:var(--muted);margin-bottom:24px;padding-left:20px}
.muted{color:var(--muted)}

/* HERO */
.hero{position:relative;min-height:78vh;display:flex;align-items:center;justify-content:center;
  text-align:center;overflow:hidden;
  background:radial-gradient(120% 90% at 70% 10%,rgba(28,58,143,.45),transparent 55%),
             radial-gradient(110% 90% at 20% 90%,rgba(192,31,51,.45),transparent 55%),
             linear-gradient(160deg,#0a0b10,#15161d)}
.hero-bg{position:absolute;inset:0;
  background-image:radial-gradient(circle,rgba(255,255,255,.05) 1.5px,transparent 1.6px);
  background-size:26px 26px;opacity:.6}
.hero-inner{position:relative;padding:24px}
.hero-kicker{text-transform:uppercase;letter-spacing:4px;color:var(--orange);font-weight:700;font-size:.85rem;margin-bottom:14px}
.hero-title{font-size:clamp(2.6rem,9vw,5.5rem);font-weight:900;line-height:.95;letter-spacing:2px;
  text-transform:uppercase;text-shadow:0 4px 30px rgba(0,0,0,.6)}
.hero-3v3{display:inline-block;margin:14px 0;font-size:clamp(1.6rem,6vw,3rem);font-weight:900;
  color:#fff;background:linear-gradient(135deg,var(--red),var(--blue));
  padding:4px 22px;border-radius:8px;transform:rotate(-2deg);box-shadow:0 8px 24px rgba(0,0,0,.5)}
.hero-place{font-size:1.05rem;color:var(--txt);margin-top:8px}
.hero-dates{font-size:1.5rem;font-weight:800;color:var(--gold);margin-top:6px}
.hero-edition{margin-top:10px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;font-size:.8rem}

/* NAV */
.nav{position:sticky;top:0;z-index:50;background:rgba(13,14,19,.92);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line)}
.nav-inner{max-width:1100px;margin:0 auto;display:flex;gap:6px;overflow-x:auto;padding:10px 12px}
.nav a{padding:8px 14px;border-radius:7px;font-weight:700;font-size:.9rem;text-decoration:none;
  white-space:nowrap;color:var(--muted)}
.nav a:hover{background:var(--card2);color:var(--txt)}

/* RIONI / SQUADRE */
.rioni-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.rione-card{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--c);
  border-radius:12px;padding:16px}
.rione-card.vuoto{opacity:.55}
.rione-head{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.rione-dot{width:14px;height:14px;border-radius:50%;background:var(--c);flex:none;box-shadow:0 0 10px var(--c)}
.rione-head h3{font-size:1.15rem;font-weight:800}
.rione-todo{color:var(--muted);font-style:italic;font-size:.9rem}
.squadra{background:var(--card2);border-radius:9px;padding:11px 12px;margin-bottom:10px}
.squadra:last-child{margin-bottom:0}
.squadra-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:7px}
.squadra-head h4{font-size:1rem;font-weight:800}
.g-badge{font-size:.7rem;font-weight:800;background:var(--blue);color:#fff;padding:2px 8px;border-radius:20px}
.roster{list-style:none;display:flex;flex-direction:column;gap:3px}
.roster li{font-size:.9rem;color:#d6d8df;padding-left:16px;position:relative}
.roster li:before{content:"•";position:absolute;left:2px;color:var(--c)}

/* CLASSIFICA */
.gironi-grid{display:grid;gap:22px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.girone-block{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;overflow-x:auto}
.girone-title{font-size:1.2rem;font-weight:800;margin-bottom:12px;color:var(--orange)}
table.classifica{width:100%;border-collapse:collapse;font-size:.88rem}
.classifica th{text-align:center;color:var(--muted);font-weight:700;padding:6px 4px;border-bottom:1px solid var(--line);font-size:.78rem}
.classifica td{text-align:center;padding:8px 4px;border-bottom:1px solid var(--line)}
.classifica .pos{font-weight:900;color:var(--gold);width:26px}
.classifica .team{text-align:left;font-weight:600;white-space:nowrap}
.classifica .team .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
.classifica .pti{font-weight:900;color:#fff}
.classifica tr:nth-child(-n+2) .pos{color:#fff;background:linear-gradient(var(--blue),var(--blue));border-radius:5px}

/* CALENDARIO */
.giorno-block{margin-bottom:24px}
.giorno-title{font-size:1.15rem;font-weight:800;color:var(--orange);margin-bottom:10px;
  border-bottom:1px solid var(--line);padding-bottom:6px}
table.calendario{width:100%;border-collapse:collapse}
.calendario td{padding:10px 6px;border-bottom:1px solid var(--line);vertical-align:middle}
.calendario .ora{font-weight:800;color:var(--gold);width:60px;font-size:.95rem}
.calendario .match{display:flex;align-items:center;gap:12px;font-weight:600}
.calendario .match span{flex:1}
.calendario .match span:last-of-type{text-align:right}
.calendario .ris{flex:none!important;min-width:54px;text-align:center;font-weight:900;
  background:var(--card2);border-radius:6px;padding:3px 8px}
.calendario .ris.vs{color:var(--muted);font-weight:700}
.calendario .fase{text-align:right;color:var(--muted);font-size:.8rem;white-space:nowrap}

/* BRACKET */
.bracket{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.bracket-match{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--gold);
  border-radius:10px;padding:14px}
.bm-label{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px;font-weight:700}
.bm-team{font-weight:800}
.bm-team em{color:var(--gold);font-style:normal;margin:0 6px}

/* PLACEHOLDER */
.placeholder{background:var(--card);border:1px dashed var(--line);border-radius:12px;padding:30px;text-align:center}
.placeholder p{margin:4px 0;font-size:1.05rem}

/* INFO */
.info-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.info-card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}
.info-card h3{margin-bottom:10px;font-size:1.1rem}
.info-card .big{font-size:1.3rem;font-weight:800;color:var(--orange)}
.regole{list-style:none;display:flex;flex-direction:column;gap:8px}
.regole li{font-size:.92rem;color:#d6d8df}
.maps-btn{display:inline-block;margin-top:12px;background:var(--blue);color:#fff;padding:8px 16px;
  border-radius:8px;text-decoration:none;font-weight:700;font-size:.9rem}
.org{text-align:center;margin-top:28px;color:var(--muted)}

footer{text-align:center;padding:30px 18px;color:var(--muted);border-top:1px solid var(--line);font-size:.85rem}
"""


def genera_html(dati: dict, output_path: Path) -> None:
    t = dati["torneo"]
    titolo = f"{t['nome']} {t.get('sottotitolo','')} · {t['anno']}"
    body = "".join([
        render_hero(t),
        render_nav(),
        render_squadre(dati),
        render_gironi(dati),
        render_calendario(dati),
        render_finali(dati),
        render_info(dati),
    ])
    doc = f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(titolo)}</title>
  <meta name="description" content="{esc(t.get('nome_esteso',''))} · {esc(t['date'])} · {esc(t['luogo'])}">
  <style>{CSS}</style>
</head>
<body>
{body}
  <footer>
    {esc(t.get('nome_esteso',''))} · {esc(t['date'])}<br>
    Pagina generata automaticamente da <code>dati_torneo.json</code>
  </footer>
</body>
</html>"""
    output_path.write_text(doc, encoding="utf-8")
    print(f"✓ Generato {output_path} ({len(doc):,} byte)")


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="Genera index.html del Torneo dei Rioni 3vs3")
    ap.add_argument("--input-dir", default=".", help="Cartella con dati_torneo.json")
    ap.add_argument("--output-dir", default=".", help="Cartella di output per index.html")
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dati = load_data(input_dir)
    genera_html(dati, output_dir / "index.html")


if __name__ == "__main__":
    main()
