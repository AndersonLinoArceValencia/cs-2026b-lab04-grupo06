#!/bin/sh
# Uso: sh evaluar.sh <criterios|pruebas|seguridad>
cd "$(dirname "$0")/$1" || exit 1
export PROMPTFOO_DISABLE_TELEMETRY=1
export PYTHONIOENCODING=utf-8
npx --yes promptfoo@0.118.0 eval --no-cache -o resultados.json
