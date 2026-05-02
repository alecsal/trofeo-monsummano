# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandi principali

```bash
# Rigenera tutto (richiede openpyxl): index.html + torneo_programma.xlsx + griglia_pranzi_torneo.xlsx
python3 genera.py

# Rigenera solo l'HTML (utile quando openpyxl non è installato)
python3 genera.py --only-html

# Rigenera solo i file Excel
python3 genera.py --only-xlsx

# Scarica i loghi istituzionali (FIP, Comune, Regione, ecc.) e li aggiunge a logos_b64.json
python3 scarica_loghi_istituzionali.py
```

Flag aggiuntivi di `genera.py`: `--input-dir <dir>` e `--output-dir <dir>` per leggere/scrivere altrove.

Dipendenze: Python 3.8+, `openpyxl` (solo per i file `.xlsx`). Non c'è test suite né linter configurati.

## Architettura

Flusso single-source-of-truth: `dati_torneo.json` → `genera.py` → `index.html` + `torneo_programma.xlsx` + `griglia_pranzi_torneo.xlsx`.

**`dati_torneo.json`** è l'unica sorgente di verità. Contiene `torneo`, `giorni`, `impianti`, `squadre` (4 gironi × 4 squadre), `partite` (40 partite, ognuna con `n`, `fase`, `squadra1`, `squadra2`, `punti1`, `punti2`, `giocata`, `placeholder`), `cerimonie` e dati mensa. **Non modificare mai `index.html` o gli `.xlsx` a mano** — vengono sovrascritti.

**`genera.py`** è un singolo file (~1300 righe) con sezioni delimitate da banner `═══`:
- `load_data()` / `get_logo()` — caricamento dati e lookup loghi
- `calcola_classifica(dati, girone_code)` — calcola la classifica di un girone iterando su `partite` con `fase == f"Girone {girone_code}"` e `giocata: true`, escludendo `placeholder`
- `genera_html(dati, loghi, output_path)` — genera HTML standalone con CSS e JS inline (loghi inclusi come data URI base64, quindi funziona offline)
- `genera_excel(...)` e `genera_griglia_pranzi(...)` — generano i due `.xlsx` (richiedono `openpyxl`)
- `main()` con `argparse` in coda

**`logos_b64.json`** mappa `logo_key` → data URI base64. Le squadre in `dati_torneo.json` referenziano questi loghi tramite il campo `logo_key`. I loghi istituzionali hanno prefisso `inst_`.

**CI (`.github/workflows/rigenera.yml`)**: ogni push su `master` che modifica `dati_torneo.json`, `genera.py` o `logos_b64.json` rigenera automaticamente i tre file di output e committa con `🤖 Rigenerazione automatica HTML ed Excel`. Il sito è pubblicato via GitHub Pages.

## Inserire un risultato

Trovare la partita in `dati_torneo.json` per numero (`"n"`) o per nomi squadre, e aggiornare:

```json
"punti1": 54,
"punti2": 48,
"giocata": true
```

**Attenzione**: `squadra1`/`squadra2` nel JSON potrebbero essere in ordine inverso rispetto a come l'utente le cita. Verificare sempre prima di assegnare i punti.

I `nome_breve` usati in `partite` devono combaciare esattamente con quelli definiti in `squadre` (errore `KeyError` se non corrispondono).

## Regole classifica (vedi `calcola_classifica`)

- Vittoria = **2 punti**, Sconfitta = **0 punti** (il README cita 1 punto FIP, ma il codice attuale usa 0)
- Ordinamento: `Pti` desc → differenza punti (`PF − PS`) desc → `PF` desc
- Le partite con `"giocata": false` o `"placeholder": true` sono escluse
- Se nessuna partita è stata giocata in un girone, le posizioni vengono mostrate come `–`

## Gironi

| Codice | Categoria | Squadre |
|--------|-----------|---------|
| A13 | U13 | Shoemakers, Endas Pistoia, Basket Marsciano, TissIttiri |
| B13 | U13 | Mens Sana Siena, Prato Dragons, Codigoro Basket, Dany Basket |
| A14 | U14 | Shoemakers, Basket Loano, Basket Calcinaia, Massa e Cozzile |
| B14 | U14 | La T Gema, San Fr. Ittiri, Chiesina Basket, Fucecchio |

Ogni squadra gioca 5 partite (3 di girone + 2 di fase finale). Le prime 2 di ogni girone vanno alle Semifinali Oro.

## Workflow git

Sviluppare sul branch `claude/*` indicato dalla sessione corrente e pushare anche su `master` (che è il branch di pubblicazione del sito):

```bash
git fetch origin master && git rebase origin/master
git push origin HEAD:master
git push origin <branch-corrente>
```

Modifiche ai soli `dati_torneo.json` / `genera.py` / `logos_b64.json` su `master` triggherano la CI che rigenera e committa gli output: in pratica basta committare il JSON, ma per coerenza locale conviene rigenerare e committare anche `index.html` e i due `.xlsx`.
