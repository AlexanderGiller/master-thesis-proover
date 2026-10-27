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
- [Projektstruktur](#projektstruktur)
- [CLI-Nutzung](#cli-nutzung)
- [Ausgaben und Ergebnisse](#ausgaben-und-ergebnisse)
- [Skripte (scripts/)](#skripte-scripts)
- [Ergebnisse der Thesis reproduzieren](#ergebnisse-der-thesis-reproduzieren)
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

## Projektstruktur

```
main.py                 Einstiegspunkt: CLI, Dispatch der Schritte, Verdikt
src/
  parser/               Lark-Grammatik (tptp_grammar.lark), Parser, AST-Klassen
  checker/              Regel-Checker (strukturell, propositional, Quantoren, Junktoren,
                        Klauseln/Gleichheit, Skolemisierung), Provenienz, Abhaengigkeiten,
                        Alpha-Aequivalenz, ATP-Anbindung (external_atp_checker.py)
  scoring/              Erwartete Ergebnisse (PRV/TST/EXT_expected.csv) und ProoVer-Scoring
  performance/          Laufzeitmessung fuer den Batch-Modus von main.py
  deep_recursion.py     Thread mit grossem Stack fuer tief verschachtelte Formeln
scripts/                Experimente und Generatoren fuer die Thesis (siehe unten)
tests/                  pytest-Testsuite
ProoVer2026/            Beweise und Probleme (PRV, Deprecated, Test, Extra)
results/eval/           Rohdaten der Evaluation der Thesis (von scripts/eval_all.py)
thesis/                 LaTeX-Quellen der Thesis; thesis/generated/ wird von den Skripten erzeugt
```

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

### 5) Ausgabe steuern

```bash
python main.py ProoVer2026/PRV/PRV010+1.s --quiet          # nur die SZS-Zeile
python main.py --quiet                                     # Batch: eine SZS-Zeile pro Proof
python main.py ProoVer2026/PRV/PRV097+1.s --debug          # zeigt, welcher Checker welchen Schritt prueft
python main.py --binary-verdict                            # Unknown wird als VerifiedBad ausgegeben
```

### 6) Alle Optionen

| Option | Modus | Bedeutung |
|---|---|---|
| `proof` | Einzel | Proof-Datei (`.s`); ohne Angabe Batch-Modus |
| `-p`, `--problem` | Einzel | Problemdatei, Default `Problems/<Name>.p` neben dem Proof |
| `-t`, `--timeout` | beide | Wall-Clock-Limit pro Proof in Sekunden (Default 30) |
| `-d`, `--dir` | Batch | Verzeichnis mit `*.s` und `Problems/` (Default `ProoVer2026/PRV`) |
| `-e`, `--expected` | Batch | CSV mit erwarteten Ergebnissen (Default nach Verzeichnisname) |
| `--prefix` | Batch | Nur Proofs, deren Dateiname so beginnt |
| `--binary-verdict` | beide | `VerifiedBad` statt `Unknown` (zweiwertige Ausgabe) |
| `--quiet` | beide | Nur die SZS-Zeile pro Proof; Fehler gehen nach stderr, CSVs werden trotzdem geschrieben |
| `--debug` | beide | Setzt `DEBUG_PROOF_FLOW`: Dispatch jedes Schritts und ATP-Aufrufe mit `[DBG]` |

### 7) CLI-Hilfe anzeigen

```bash
python main.py -h
```

## Ausgaben und Ergebnisse

Beim Lauf von `main.py` bekommst du:

- SZS-nahe Status je Proof (`VerifiedGood`, `VerifiedBad`, `Unknown`, `Timeout`)
  - `Unknown` (dreiwertiges Verdikt): kein Fehler gefunden, aber mindestens ein Schritt blieb unentscheidbar (Prover-Timeout/keine Antwort oder keine Pruefregel). Das Tool enthaelt sich (0 Punkte).
  - `--binary-verdict` gibt stattdessen `VerifiedBad` aus (zweiwertige Ausgabe).
- Zusammenfassung ueber alle Proofs
- Performance-Report (Wall-Clock pro Proof; ohne Start des Interpreters, die CPU-Zeit bezieht sich nur auf den Elternprozess)
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

## Skripte (scripts/)

Die Skripte gehoeren zur Thesis und werden fuer die normale Nutzung des Verifiers nicht gebraucht.
Alle werden vom Projekt-Root aus gestartet; Skripte, die Vampire brauchen, nutzen dieselben
Variablen `EXTERNAL_ATP_BINARY` / `EXTERNAL_ATP_COMMAND` wie der Verifier (unter Windows in WSL starten).

| Skript | Zweck | Braucht Vampire | Ergebnis in der Thesis |
|---|---|---|---|
| `eval_all.py` | Treiber der gesamten Evaluation | ja (ausser `noatp`, `coverage`, `inputs`, `tables`) | alle Tabellen, Zahlen und Abbildungen von Kapitel 7 |
| `_eval_worker.py` | prueft einen Proof in einem frischen Prozess (wird von `eval_all.py` aufgerufen) | indirekt | Laufzeit- und Speicherwerte |
| `gen_extra_tests.py` | erzeugt das Extra-Set (Regeltests) | nein | Abschnitt 7.2 |
| `exp_extra_tests.py` | prueft das Extra-Set und vergleicht mit der Erwartung | ja | Abschnitt 7.2 |
| `run_vampire_all.sh` | laesst Vampire auf allen Problemen laufen | ja | Fallstudie in 8.3 |
| `exp_vampire_compat.py` | gibt die Vampire-Beweise an den Verifier | optional | Tabelle zu unveraenderten Vampire-Beweisen (8.3) |
| `exp_skolem_mutants.py` | vergleicht den Skolem-Check mit einem Entailment-Orakel | optional | Tabelle Skolem-Check vs. Orakel (8.3) |
| `gen_dag_figure.py` | zeichnet den Abhaengigkeitsgraphen eines Proofs | nein (Graphviz) | Abbildung zu `PRV089` (Design) |
| `gen_appendix_tables.py` | Tabellen pro Proof (Status, Laufzeit) | nein | nicht mehr in der Thesis, Uebersicht fuer das Repo |

### eval_all.py

Fuehrt alle Experimente der Evaluation aus und schreibt
Rohdaten nach `results/eval/` sowie LaTeX-Tabellen und `\providecommand`-Makros nach `thesis/generated/`.
Dadurch wird keine Zahl im Evaluationskapitel von Hand eingetragen.

```bash
python scripts/eval_all.py --parts all --reps 3      # alles (dauert, braucht Vampire)
python scripts/eval_all.py --parts runs,tables       # nur die Laeufe und daraus die Tabellen
python scripts/eval_all.py --parts tables            # nur Tabellen/Makros/Abbildungen aus vorhandenen Rohdaten (Sekunden)
```

| Part | Inhalt | Rohdaten |
|---|---|---|
| `runs` | Jeder Proof (PRV, Deprecated, Test, Extra) `--reps`-mal in einem frischen Prozess: Verdikt, Schritte, ATP-Aufrufe, Laufzeit, Speicher | `runs.json`, `per_proof.csv` |
| `noatp` | Dieselben Laeufe mit einem nicht existierenden Prover (Fail-closed-Test) | `noatp.json` |
| `internal` | Stichprobe intern gepruefter Schritte, jeweils zusaetzlich von Vampire geprueft | `internal.json` |
| `mutation` | Mutationen gueltiger Proofs; akzeptierte Mutanten werden mit Vampire klassifiziert | `mutation.json`, `mutation_misses.json` |
| `inputs` | Zehn kaputte Eingaben auf Basis von `PRV010+1.s` | `inputs.json` |
| `extra` | Extra-Set (Regeltests) | Teil von `runs.json` |
| `coverage` | Testabdeckung mit pytest-cov und Zeilen pro Modul | `coverage.json` |
| `tables` | Erzeugt Tabellen, Makros und die Abbildungen `rule_coverage`, `runtime_scatter`, `mutation_outcomes` neu | - |

Hinweise:
- Die Statistiken der Thesis beziehen sich auf die 91 offiziellen PRV-Paare; die 9 Proofs aus `Deprecated/` gehen nur in die Gesamtzeile der Verdict-Matrix ein.
- Die gemessene Zeit eines Proofs reicht vom Start des Prozesses bis zum Verdikt, wie im Wettbewerb. Die Aufschluesselung nach Phasen (Parsen, Checks, ATP) wird nach dem Check separat gemessen und zaehlt nicht zur Gesamtzeit.
- Commit, Datum, CPU, Python- und Vampire-Version werden in `results/eval/env.json` festgehalten und erscheinen in der Thesis (`\EvalCommit` usw.).

### _eval_worker.py

Interner Helfer von `eval_all.py`. Startet den Verifier fuer genau einen Proof in einem neuen Python-Prozess,
schreibt das Debug-Protokoll in einen Puffer und gibt eine JSON-Zeile mit Verdikt, Schritten, ATP-Aufrufen,
Zeiten und Spitzenspeicher aus. Direkt aufrufbar zum Debuggen einzelner Messungen:

```bash
python scripts/_eval_worker.py ProoVer2026/PRV/PRV010+1.s ProoVer2026/PRV/Problems/PRV010+1.p
```

### gen_extra_tests.py und exp_extra_tests.py

`gen_extra_tests.py` erzeugt fuer die Regeln, die das TST-Set kaum abdeckt (Resolution, Paramodulation,
Rewrite, Transitivitaet, Reflexivitaet, Junktoren-, Quantoren- und Strukturregeln), je einen korrekten Basis-Proof
und mehrere Varianten mit bekanntem Fehler sowie einige Edge Cases. Ergebnis: `ProoVer2026/Extra/` mit
`EXTnnn+1.s`, `Problems/EXTnnn+1.p` und `EXT_expected.csv`.

`exp_extra_tests.py` prueft dieses Set und hält zusaetzlich fest, ob der Fehler vom Checker der Regel selbst
gemeldet wird oder nur vom letzten `consequence`-Schritt. Ergebnis: `results/extra/results.csv` und `summary.json`.

```bash
python scripts/gen_extra_tests.py                 # Extra-Set neu erzeugen (ueberschreibt ProoVer2026/Extra)
python scripts/exp_extra_tests.py --timeout 60    # Extra-Set auswerten
```

Nuetzlich, wenn ein neuer Regel-Checker hinzukommt: Generator erweitern, Set neu erzeugen, auswerten.

### run_vampire_all.sh

Laesst Vampire im CASC-Modus auf allen 176 Problemen aus `ProoVer2026/PRV/Problems`, `ProoVer2026/Deprecated/Problems`
und `ProoVer2026/Test/Problems` laufen und legt die SZS-Ergebnisse und die Beweise unter `results/vampire/` ab
(`summary.csv`, `raw/`, `proofs/`). Grundlage fuer die Fallstudie zur Uebertragbarkeit (Kapitel 8.3).
Die deprecated Paare sind bewusst dabei, damit die Zahlen der Thesis (176 Probleme) reproduziert werden.

```bash
bash scripts/run_vampire_all.sh                      # alle Probleme
bash scripts/run_vampire_all.sh PRV000+1 PRV010+1    # nur ausgewaehlte
TIMEOUT=30 JOBS=4 VAMPIRE=~/vampire/vampire bash scripts/run_vampire_all.sh
```

### exp_vampire_compat.py

Wertet die von `run_vampire_all.sh` erzeugten Beweise aus: ob ein Beweis (und keine Saturierung) vorliegt,
ob der Parser die Datei akzeptiert, welche Inferenzregeln vorkommen und wie viele davon zum ProoVer-Vokabular gehoeren,
die Groesse der Beweise und mit `--verify` das Verdikt des Verifiers.
Ergebnis: `results/vampire/compat.csv` und `compat_summary.json`.

```bash
python scripts/exp_vampire_compat.py --verify --timeout 60
```

### exp_skolem_mutants.py

Nimmt die Skolemisierungsschritte der Referenzbeweise, erzeugt Mutanten mit bekanntem Fehler
(`drop_arg`, `universal`, `negate_atom`, `drop_conjunct`) und vergleicht den internen Skolem-Check mit einem
Entailment-Orakel (Vampire prueft, ob die Konklusion die Praemisse impliziert). Zeigt, welche Fehler eine reine
Entailment-Pruefung uebersieht. Ohne `--vampire` wird nur der Checker ausgewertet. Die erwarteten Ergebnisse der Proofs liest das Skript aus
`results/PRV_results.csv`, `results/Deprecated_results.csv` und `results/Test_results.csv`, also vorher
`python main.py -d ProoVer2026/PRV`, `-d ProoVer2026/Deprecated` und `-d ProoVer2026/Test` ausfuehren.
Ergebnis: `results/skolem_mutants.csv` und `skolem_mutants_summary.json`.

```bash
python scripts/exp_skolem_mutants.py --vampire ~/vampire/vampire --max-per-proof 10 --timeout 10
```

### gen_dag_figure.py

Zeichnet den Abhaengigkeitsgraphen eines TSTP-Proofs mit Graphviz (`dot` muss installiert sein).
Knoten sind die Formeln, Kanten fuehren vom Parent zum abgeleiteten Schritt, und die Farbe zeigt,
welcher Check den Knoten prueft (Provenienz, negierte Konjektur, Skolem, interner Checker, Shortcut, ATP).
Nuetzlich, um einzelne Proofs zu verstehen oder zu debuggen.

```bash
python scripts/gen_dag_figure.py ProoVer2026/PRV/PRV089+1.s thesis/diagrams/dag_prv089
```

### gen_appendix_tables.py

Erzeugt aus `results/eval/runs.json` Tabellen mit Status, Bewertung und Laufzeit jedes Proofs
(`thesis/generated/tab_app_prv.tex`, `tab_app_tst.tex`, `tab_app_ext.tex`, als `longtable`).
In der gekuerzten Thesis werden sie nicht mehr eingebunden, sind aber eine kompakte Uebersicht pro Proof.

```bash
python scripts/gen_appendix_tables.py
```

## Ergebnisse der Thesis reproduzieren

1. Installation wie oben, Vampire 5.0.1 im `PATH` oder ueber `EXTERNAL_ATP_BINARY`.
2. Tests: `pytest` (291 Tests laufen ohne Prover, 2 brauchen Vampire).
3. Evaluation: `python scripts/eval_all.py --parts all --reps 3` (mehrere Minuten; Rechner moeglichst nicht anderweitig belasten).
4. Optional die Fallstudie aus Kapitel 8.3:
   `bash scripts/run_vampire_all.sh`, danach `python scripts/exp_vampire_compat.py --verify` und `python scripts/exp_skolem_mutants.py --vampire <pfad>`.
5. Thesis bauen (in `thesis/`): `latexmk -pdf main.tex`. Vorher `main.aux` und `main.bbl` loeschen, wenn sich die Literatur geaendert hat.

Die Rohdaten des Laufs, der in der Thesis steht, liegen in `results/eval/` (Commit siehe `env.json`).

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
