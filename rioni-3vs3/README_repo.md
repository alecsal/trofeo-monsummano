# Torneo dei Rioni 3vs3 — 2026

Sito statico per il **3º Torneo dei Rioni 3vs3** di Monsummano Terme.
📍 Parco Orzali · 🗓️ 10–14 giugno 2026 · nell'ambito di «Sportiva — Festa dello Sport».

## Come funziona

Single source of truth: **`dati_torneo.json` → `genera.py` → `index.html`** (standalone, offline).

```bash
python3 genera.py                  # rigenera index.html
```

Nessuna dipendenza esterna: l'HTML prodotto ha CSS inline e funziona aperto da file o via GitHub Pages.

## Inserire un risultato

In `dati_torneo.json` trova la partita per numero (`"n"`) e aggiorna:

```json
"punti1": 17, "punti2": 14, "giocata": true
```

poi rilancia `python3 genera.py`. La classifica del girone si ricalcola da sola
(regole FIBA 3x3: vittoria 2 pti, sconfitta 0; ordinamento Pti → differenza canestri → canestri fatti).

## Squadre e gironi

| Girone A | Girone B |
|---|---|
| Centro A | Bizzarrino B |
| Grotta Parlanti A | Cintolese A |
| Vergine dei Pini A | Grotta Parlanti B |
| Bizzarrino A | Centro B |

Le squadre A e B dello stesso rione sono in gironi diversi.

## Pubblicazione

Il sito è pubblicato via **GitHub Pages** (Settings → Pages → Deploy from a branch → `master` / `root`).
