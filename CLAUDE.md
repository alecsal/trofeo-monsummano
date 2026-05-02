# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandi principali

```bash
# Rigenera solo l'HTML (openpyxl non disponibile in questo ambiente)
python3 genera.py --only-html

# Rigenera tutto (richiede openpyxl installato)
python3 genera.py
```

## Architettura

Il flusso è: `dati_torneo.json` → `genera.py` → `index.html` (+ `torneo_programma.xlsx`).

**`dati_torneo.json`** è l'unica sorgente di verità. Contiene squadre, partite, impianti, cerimonie e dati mensa. Non modificare `index.html` a mano.

**`genera.py`** ha tre funzioni principali:
- `calcola_classifica(dati, girone_code)` — calcola la classifica di un girone dalle partite con `giocata: true`
- `genera_html(dati, loghi, output_path)` — genera l'HTML standalone con CSS e JS inline
- `genera_excel(...)` / `genera_griglia_pranzi(...)` — generano i file Excel (richiedono `openpyxl`)

**`logos_b64.json`** contiene i loghi delle squadre codificati in base64, referenziati tramite `logo_key` in `dati_torneo.json`.

## Inserire un risultato

Trovare la partita in `dati_torneo.json` per numero (`"n"`) o per nomi squadre, e aggiornare:

```json
"punti1": 54,
"punti2": 48,
"giocata": true
```

**Attenzione**: `squadra1`/`squadra2` nel JSON potrebbero essere in ordine inverso rispetto a come l'utente le cita. Verificare sempre prima di assegnare i punti.

## Regole classifica

- Vittoria = **2 punti**, Sconfitta = **0 punti**
- Ordinamento: punti classifica → differenza punti → punti fatti
- Le partite con `"giocata": false` o `"placeholder": true` sono escluse

## Gironi

| Codice | Categoria | Squadre |
|--------|-----------|---------|
| A13 | U13 | Shoemakers, Endas Pistoia, Basket Marsciano, TissIttiri |
| B13 | U13 | Mens Sana Siena, Prato Dragons, Codigoro Basket, Dany Basket |
| A14 | U14 | Shoemakers, Basket Loano, Basket Calcinaia, Massa e Cozzile |
| B14 | U14 | La T Gema, San Fr. Ittiri, Chiesina Basket, Fucecchio |

## Workflow git

Sviluppare sul branch `claude/add-match-score-yQwvi` e pushare sempre anche su `master`:

```bash
git fetch origin master && git rebase origin/master
git push origin HEAD:master
git push origin claude/add-match-score-yQwvi
```
