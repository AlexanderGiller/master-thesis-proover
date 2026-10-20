#!/usr/bin/env bash
# Laeuft Vampire ueber alle Probleme in ProoVer2026/PRV/Problems und ProoVer2026/Test/Problems.
# Nutzung (in WSL, im Projekt-Root):
#   bash scripts/run_vampire_all.sh                  # alle Probleme
#   bash scripts/run_vampire_all.sh PRV000+1 PRV010+1 # nur ausgewaehlte
# Umgebungsvariablen:
#   VAMPIRE=...       Binary/Pfad (Default: vampire im PATH, sonst ~/vampire/vampire)
#   TIMEOUT=30        Sekunden pro Problem
#   JOBS=4            parallele Laeufe
#   VAMPIRE_ARGS=""   zusaetzliche Vampire-Optionen
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Wie src/checker/external_atp_checker.py: erst PATH, dann ~/vampire/vampire
if [ -z "${VAMPIRE:-}" ]; then
  if command -v vampire >/dev/null 2>&1; then VAMPIRE="vampire"
  elif [ -x "$HOME/vampire/vampire" ]; then VAMPIRE="$HOME/vampire/vampire"
  else VAMPIRE="vampire"; fi
fi
export VAMPIRE
export TIMEOUT="${TIMEOUT:-30}"
export VAMPIRE_ARGS="${VAMPIRE_ARGS:-}"
JOBS="${JOBS:-1}"
export OUT_DIR="$ROOT/results/vampire"

command -v "$VAMPIRE" >/dev/null 2>&1 || { echo "Vampire nicht gefunden: $VAMPIRE" >&2; exit 1; }

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"/{raw,proofs,rows}

# Jedes Problem wird im Ordner seiner Gruppe (PRV oder Test) aufgerufen, damit file('Problems/X.p',...)
# in den Vampire-Beweisen denselben Pfad hat wie in den Referenz-.s-Dateien.
export ROOT
cd "$ROOT/ProoVer2026" || exit 1

run_one() {
  local entry="$1" grp p name out start end secs szs rc has
  grp="${entry%%/*}"; p="${entry#*/}"
  name="$(basename "$p" .p)"
  out="$OUT_DIR/raw/$name.out"
  start=$(date +%s.%N)
  # shellcheck disable=SC2086
  (cd "$ROOT/ProoVer2026/$grp" && timeout -k 5 $((TIMEOUT + 5)) "$VAMPIRE" --mode casc -t "$TIMEOUT" $VAMPIRE_ARGS "$p") >"$out" 2>&1
  rc=$?
  end=$(date +%s.%N)
  secs=$(awk -v s="$start" -v e="$end" 'BEGIN{printf "%.2f", e-s}')
  szs=$(grep -m1 '^% SZS status' "$out" | awk '{print $4}')
  [ -z "$szs" ] && szs="NoStatus"
  has="no"
  if grep -q '^% SZS output start' "$out"; then
    sed -n '/^% SZS output start/,/^% SZS output end/p' "$out" >"$OUT_DIR/proofs/$name.s"
    has="yes"
  fi
  echo "$name,$szs,$rc,$secs,$has" >"$OUT_DIR/rows/$name.csv"
  echo "$name: $szs (${secs}s)"
}
export -f run_one

if [ "$#" -gt 0 ]; then
  files=()
  for n in "$@"; do
    n="${n%.p}"
    case "$n" in TST*) grp=Test ;; *) grp=PRV ;; esac
    files+=("$grp/Problems/$n.p")
  done
else
  files=(PRV/Problems/*.p Test/Problems/*.p)
fi

printf '%s\0' "${files[@]}" | xargs -0 -n1 -P "$JOBS" bash -c 'run_one "$1"' _

{
  echo "Problem,SZS_Status,ExitCode,WallSeconds,ProofExtracted"
  cat "$OUT_DIR"/rows/*.csv | sort
} >"$OUT_DIR/summary.csv"

echo
echo "== Zusammenfassung (SZS-Status) =="
tail -n +2 "$OUT_DIR/summary.csv" | cut -d, -f2 | sort | uniq -c | sort -rn
echo
echo "Details: $OUT_DIR/summary.csv | Rohausgabe: $OUT_DIR/raw/ | Beweise (.s): $OUT_DIR/proofs/"
