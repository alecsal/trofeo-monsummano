# Torneo dei Rioni 3vs3 — 2026

Sito statico per il 3º Torneo dei Rioni 3vs3 di Monsummano Terme (Parco Orzali, 10–14 giugno 2026).

## Flusso

`dati_torneo.json` → `genera.py` → `index.html` (standalone, offline).

```bash
python3 genera.py                  # rigenera index.html
python3 genera.py --output-dir .   # idem
```

Nessuna dipendenza esterna. L'HTML prodotto ha CSS/JS inline e funziona aperto da file.

> Repo di staging: sviluppato qui dentro `trofeo-monsummano/rioni-3vs3/`, destinazione finale repo dedicato `trofeo-rioni-3vs3`.
