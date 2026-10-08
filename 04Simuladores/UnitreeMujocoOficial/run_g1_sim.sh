#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
echo "[INFO] Iniciando gemelo digital (simulador MuJoCo G1) en macOS con mjpython..."
"$DIR/.venv/bin/mjpython" "$DIR/g1_teacher_sim.py"
