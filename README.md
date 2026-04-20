# Trofeo Città di Monsummano Terme 2026

Repository del sito pubblico del torneo giovanile U13/U14 organizzato da Shoemakers Basket Monsummano.

## 🌐 Sito live

👉 **https://TUO_USERNAME.github.io/trofeo-monsummano/**

Il file `index.html` è autocontenuto (loghi inline in base64, funziona anche offline).

## 📁 Struttura del repository

```
trofeo-monsummano/
├── dati_torneo.json        ← ⭐ IL FILE DA MODIFICARE per aggiornamenti
├── logos_b64.json          ← loghi squadre in base64 (raramente modificato)
├── genera.py               ← script che genera HTML + Excel dal JSON
├── index.html              ← generato automaticamente, NON modificare a mano
├── torneo_programma.xlsx   ← generato automaticamente, NON modificare a mano
└── README.md               ← questo file
```

## 🚀 Come aggiornare il torneo

**Regola d'oro**: modifichi solo `dati_torneo.json`, poi rigeneri.

### 1️⃣ Aggiornare un risultato

Apri `dati_torneo.json`, trova la partita da aggiornare (cerca per `"n": NUMERO`) e modifica:

```json
{"n": 2, "giorno": "G1", "ora": "10:00", ..., "punti1": 48, "punti2": 42, "giocata": true}
```

Imposta:
- `punti1`: punti della prima squadra
- `punti2`: punti della seconda squadra
- `giocata`: metti `true` (importante! altrimenti non conta per la classifica)

### 2️⃣ Rigenerare HTML + Excel

```bash
python3 genera.py
```

Output:
```
📂 Caricati 40 partite, 16 squadre, 16 loghi
✅ index.html (1123 KB)
✅ torneo_programma.xlsx (14 KB)
```

### 3️⃣ Pubblicare le modifiche su GitHub

```bash
git add dati_torneo.json index.html torneo_programma.xlsx
git commit -m "Aggiornati risultati del venerdì mattina"
git push
```

In 1-2 minuti GitHub Pages aggiorna il sito pubblico.

## 🤖 Prompt pronti per Claude Code

Claude Code può gestire l'intero flusso con comandi in linguaggio naturale:

### Aggiornare un singolo risultato
> *"Shoemakers ha battuto Endas 48-42 nella partita #2. Aggiorna il JSON, rigenera HTML ed Excel, fai commit e push."*

### Aggiornare più risultati
> *"Aggiorna questi risultati: partita #2 Shoe-Endas 48-42, partita #6 Marsciano-TissIttiri 55-50. Rigenera e fai push con messaggio 'Risultati primo turno venerdì'."*

### Cambiare un orario
> *"La partita #13 è spostata dalle 18:00 alle 18:30. Aggiorna il JSON, rigenera e fai push."*

### Aggiungere una squadra sostitutiva
> *"Al posto di Massa e Cozzile nel girone A14 subentra 'Libertas Livorno' (Livorno, LI, Toscana, non fuori regione). Aggiorna tutte le partite del girone, rigenera e pusha."*

### Verificare stato torneo
> *"Quante partite sono state giocate finora? Mostra la classifica aggiornata di ogni girone."*

## 📋 Struttura del JSON

### `torneo`
Metadati generali (nome, anno, organizzatore).

### `giorni`
Mappatura codici giorno → etichette leggibili.

### `impianti`
Elenco strutture + punto ristoro, con indirizzi e link Google Maps.

### `squadre`
4 gironi (`A13`, `B13`, `A14`, `B14`), ognuno con 4 squadre. Campi chiave per ogni squadra:
- `slot`: codice posizione (es. `A1`, `B2`)
- `nome_breve`: usato nelle partite (deve combaciare!)
- `nome_esteso`: nome ufficiale mostrato nelle classifiche
- `logo_key`: chiave nel file `logos_b64.json`
- `fuori_regione`: `true` per le squadre non toscane

### `partite`
Array di 40 partite. Campi chiave:
- `n`: numero progressivo partita (1-40)
- `giocata`: `false` di default, mettere `true` quando aggiorni il risultato
- `punti1`, `punti2`: i punteggi (inizialmente 0)
- `placeholder`: `true` per partite con squadre da determinare (semi/finali)

### `cerimonie`
Apertura (ven 15:00) e chiusura (dom 17:00).

## 🏀 Regole di calcolo classifica (FIP)

- Vittoria = **2 punti**
- Sconfitta = **1 punto** (anche dopo overtime)
- Ordinamento: Pti → Differenza punti → Punti fatti → ordine originale

Le partite con `giocata: false` o `placeholder: true` vengono escluse dal calcolo.

## 🛠️ Requisiti

- Python 3.8+
- `pip install openpyxl`

## 🆘 Troubleshooting

**"KeyError" quando rigenero**: probabilmente hai scritto un nome squadra in `partite` che non esiste in `squadre`. I nomi devono combaciare esattamente (`nome_breve`).

**Loghi mancanti nel sito**: verifica che la `logo_key` in `dati_torneo.json` corrisponda a una chiave presente in `logos_b64.json`.

**Classifica non aggiornata**: controlla che `"giocata": true` sia stato messo sulla partita.

---

**Organizzato da ASD Shoemakers Basket Monsummano** 🔵🔴
