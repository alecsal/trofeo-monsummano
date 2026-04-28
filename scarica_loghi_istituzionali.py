#!/usr/bin/env python3
"""
scarica_loghi_istituzionali.py — Scarica i 6 loghi istituzionali (FIP, Comune,
Regione Toscana, CONI, Provincia, Minibasket) dal sito ufficiale del Trofeo
e li aggiunge a `logos_b64.json` come data URI base64.

Uso (dalla root del repo, dove network è disponibile):
    python3 scarica_loghi_istituzionali.py

Risultato:
    - aggiorna `logos_b64.json` aggiungendo 6 chiavi: inst_fip, inst_comune,
      inst_regione_toscana, inst_coni, inst_provincia_pistoia, inst_minibasket
    - salva anche le immagini originali in `loghi_istituzionali/` (per verifica)

Dopo l'esecuzione: `git add logos_b64.json loghi_istituzionali/ && git commit && git push`
"""
import base64
import json
import mimetypes
import sys
import urllib.request
from pathlib import Path

BASE_URL = 'https://www.trofeocittadimonsummanoterme.it/immagini'
OUT_DIR = Path('loghi_istituzionali')
JSON_PATH = Path('logos_b64.json')

# (chiave_logo, filename_su_server)
LOGHI = [
    ('inst_fip',                'FIP.jpg'),
    ('inst_comune',             'comune_monsummano.jpg'),
    ('inst_regione_toscana',    'regione-toscana.png'),
    ('inst_coni',               'Coni.jpg'),
    ('inst_provincia_pistoia',  'provincia-pistoia.png'),
    ('inst_minibasket',         'minibasket.jpg'),
]

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')


def scarica(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status != 200:
            raise RuntimeError(f'HTTP {r.status} per {url}')
        return r.read()


def to_data_uri(filename: str, raw: bytes) -> str:
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = 'image/jpeg'
    b64 = base64.b64encode(raw).decode('ascii')
    return f'data:{mime};base64,{b64}'


def main() -> int:
    if not JSON_PATH.exists():
        print(f'ERROR: {JSON_PATH} non trovato. '
              f'Esegui questo script dalla root del repo.', file=sys.stderr)
        return 1

    OUT_DIR.mkdir(exist_ok=True)
    loghi_db = json.loads(JSON_PATH.read_text(encoding='utf-8'))

    aggiunti, aggiornati = 0, 0
    for chiave, filename in LOGHI:
        url = f'{BASE_URL}/{filename}'
        print(f'  ↓ {chiave:30s}  {url}')
        try:
            raw = scarica(url)
        except Exception as e:
            print(f'    !! errore: {e}', file=sys.stderr)
            return 2

        # salva anche il file sorgente, per verifica
        (OUT_DIR / filename).write_bytes(raw)

        data_uri = to_data_uri(filename, raw)
        if chiave in loghi_db:
            aggiornati += 1
        else:
            aggiunti += 1
        loghi_db[chiave] = data_uri
        print(f'    ✓ {len(raw):>7} byte  →  {len(data_uri):>7} char base64')

    JSON_PATH.write_text(
        json.dumps(loghi_db, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print()
    print(f'OK  logos_b64.json aggiornato '
          f'(+{aggiunti} nuovi, {aggiornati} sovrascritti)')
    print(f'OK  immagini originali salvate in {OUT_DIR}/')
    print()
    print('Prossimo passo:')
    print('  git add logos_b64.json loghi_istituzionali/')
    print('  git commit -m "Aggiunge loghi istituzionali in base64"')
    print('  git push')
    return 0


if __name__ == '__main__':
    sys.exit(main())
