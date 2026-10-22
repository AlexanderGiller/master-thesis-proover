# ProoVer Thesis Proof Checker

Dieses Projekt ist ein Proof-Checker fuer TPTP/TSTP-nahe Beweise aus dem ProoVer-2026-Setting.
Er verifiziert einzelne Inferenzschritte, kann bei Bedarf ein externes ATP (hier: Vampire) nutzen und erzeugt Ergebnis- und Scoring-Reports.

## Kontext

Dieses Projekt ist im Rahmen einer Masterarbeit an der Ludwig-Maximilians-Universitaet Muenchen (LMU) entstanden.
Entsprechend liegt der Fokus auf nachvollziehbarer Verifikation, reproduzierbaren Experimenten und einer klaren Trennung zwischen Proof-Suche und Proof-Checking.

## Inhalt

- [Voraussetzungen](#voraussetzungen)
- [Installation unter Linux](#installation-unter-linux)
- [Installation unter Windows-mit-wsl](#installation-unter-windows-mit-wsl)
- [Externe ATP-Integration-vampire](#externe-atp-integration-vampire)
- [CLI-Nutzung](#cli-nutzung)
- [Ausgaben und Ergebnisse](#ausgaben-und-ergebnisse)
- [Tests und Entwicklung](#tests-und-entwicklung)
- [Troubleshooting](#troubleshooting)

## Voraussetzungen

- Python 3.11+ (empfohlen: 3.12)
- `pip`
- Optional fuer Entwicklungs-Workflow: `pytest`, `black`, `isort`, `flake8` (ueber `requirements-dev.txt`)
- Fuer alle ATP-basierten Schrittpruefungen: **Vampire** als externes ATP

Wichtig:

- Ohne externes ATP laufen nur die rein internen Regelpruefungen vollstaendig.
- Fuer manche Schritte (z. B. allgemeine `thm`/`cth`-Validierung) wird ein ATP-Aufruf benoetigt.

## Installation unter Linux

Im Projekt-Root (`master-thesis-proover`) ausfuehren:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Installation unter Windows mit WSL

Fuer dieses Projekt ist auf Windows aktuell **WSL noetig**, wenn du ATP-Checks mit Vampire nutzen willst.
Empfehlung: Das Projekt direkt in einer WSL-Shell (z. B. Ubuntu) ausfuehren.

### 1) WSL vorbereiten (einmalig)

PowerShell als Admin:

```powershell
wsl --install
```

Danach Windows neu starten und eine Distribution (z. B. Ubuntu) initial einrichten.

### 2) Projekt in WSL verwenden

In der WSL-Shell:

```bash
cd /mnt/c/Git/master-thesis-proover
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Hinweis zum Editor:

- Der Code kann in einem Windows-Editor bearbeitet werden.
- Die ATP-relevanten Runs solltest du aber im WSL-Terminal starten, nicht als reinen nativen Windows-Run.

## Externe ATP-Integration (Vampire)

Der Checker sucht standardmaessig nach `vampire` im `PATH`.
Optional koennen folgende Variablen gesetzt werden:

- `EXTERNAL_ATP_BINARY` (nur Binary-Name/Pfad)
- `EXTERNAL_ATP_COMMAND` (vollstaendiger Aufruf als Kommando)

Beispiele:

```bash
export EXTERNAL_ATP_BINARY=/usr/local/bin/vampire
```

oder:

```bash
export EXTERNAL_ATP_COMMAND="/pfad/zu/vampire"   # --mode casc und --time_limit haengt der Verifier selbst an
```

Falls du Python aus Windows startest und Vampire in WSL liegt, kann ein WSL-Wrapper genutzt werden:

```powershell
$env:EXTERNAL_ATP_COMMAND = "wsl vampire"
```

Empfehlung bleibt trotzdem: alles direkt in WSL laufen lassen.

## CLI-Nutzung

Alle Beispiele vom Projekt-Root aus.

### 1) Verzeichnisstruktur und Kommandos

```
ProoVer2026/
  PRV/          offizielle ProoVer-Beweise (91) + Problems/
  Deprecated/   9 fruehere Beispielbeweise (PRV005, ...) + Problems/
  Test/         eigene Testbeweise (TST) + Problems/
  Extra/        generierte Regeltests (EXT) + Problems/
```

| Ziel | Kommando |
|---|---|
| Einen Proof pruefen | `python main.py PROOF [-p PROBLEM]` |
| Alle Proofs eines Verzeichnisses pruefen und bewerten | `python main.py -d VERZEICHNIS` |
| Experimente der Thesis (Laufzeit, Ablation, Mutation, Abdeckung, Tabellen) | `python scripts/eval_all.py --parts all` |
| Vorhandene Ergebnis-CSV neu bewerten | `python src/scoring/score_proofs.py` |

`main.py` ist das Werkzeug zum Pruefen und Bewerten; `scripts/eval_all.py` ist das Experiment-Skript der Thesis und fuer die normale Nutzung nicht noetig.

### 2) Alle Proofs eines Verzeichnisses pruefen (Batch)

Ohne Proof-Argument durchsucht `main.py` das Verzeichnis nach `*.s`, mappt auf `Problems/*.p`, prueft alles und erzeugt Summary und Scoring-CSV.
Die erwarteten Ergebnisse werden aus dem Verzeichnisnamen gewaehlt (`src/scoring/`); mit `-e` kann eine andere CSV angegeben werden.

```bash
python main.py                        # Standard: ProoVer2026/PRV (offizielle Beweise)
python main.py -d ProoVer2026/Test    # eigene Testbeweise (TST_expected.csv)
python main.py -d ProoVer2026/Extra   # generierte Regeltests (EXT_expected.csv)
python main.py -d ProoVer2026/Deprecated   # fruehere Beispielbeweise
python main.py -d ProoVer2026/PRV --prefix PRV01   # nur Dateien mit diesem Praefix
```

Die Ergebnisse stehen in `results/<Verzeichnisname>_results.csv` (z. B. `PRV_results.csv`, `Test_results.csv`, `Extra_results.csv`), die Laufzeiten in `results/<Verzeichnisname>_performance.csv`.

### 3) Einzelnen Proof pruefen

```bash
python main.py ProoVer2026/PRV/PRV000+1.s
```

Die Problemdatei wird dann automatisch als `ProoVer2026/PRV/Problems/PRV000+1.p` angenommen.
Mit expliziter Problemdatei:

```bash
python main.py ProoVer2026/PRV/PRV000+1.s -p ProoVer2026/PRV/Problems/PRV000+1.p
```

### 4) Timeout pro Proof erhoehen

Default ist aktuell `30` Sekunden pro Proof (Wall-Clock).

Alle Proofs mit hoeherem Limit:

```bash
python main.py -t 120
```

Einzelproof mit hoeherem Limit:

```bash
python main.py ProoVer2026/PRV/PRV010+1.s -t 90
```

### 5) CLI-Hilfe anzeigen

```bash
python main.py -h
```

## Ausgaben und Ergebnisse

Beim Lauf von `main.py` bekommst du:

- SZS-nahe Status je Proof (`VerifiedGood`, `VerifiedBad`, `Unknown`, `Timeout`)
  - `Unknown` (dreiwertiges Verdikt): kein Fehler gefunden, aber mindestens ein Schritt blieb unentscheidbar (Prover-Timeout/keine Antwort oder keine Pruefregel). Das Tool enthaelt sich (0 Punkte).
  - `--binary-verdict` gibt stattdessen `VerifiedBad` aus (zweiwertige Ausgabe).
- Zusammenfassung ueber alle Proofs
- Performance-Report (Wall-Clock/CPU)
- Scoring-Zusammenfassung

Datei-Ausgaben:

- `results/<Verzeichnisname>_results.csv` (Scoring/Ergebnisse, z. B. `PRV_results.csv`)
- `results/<Verzeichnisname>_performance.csv` (Performance pro Proof)

Zusaetzliches Scoring-Skript:

```bash
python src/scoring/score_proofs.py
```

Mit Optionen:

```bash
python src/scoring/score_proofs.py -h
```

## Tests und Entwicklung

Tests aus dem Projekt-Root:

```bash
pytest
```

Format/Lint (optional):

```bash
black .
isort .
flake8
```

## Troubleshooting

- `ATP executable not found`: Vampire nicht installiert oder nicht im `PATH`.
- ATP-Aufrufe schlagen unter Windows fehl: Run im WSL-Terminal starten.
- `Proof file not found` oder `Problem file not found`: Pfade pruefen, vom Projekt-Root starten.
- Viele Timeouts: `-t` erhoehen (z. B. `-t 120`) und pruefen, ob Vampire korrekt erreichbar ist.
