#!/usr/bin/env bash
# Ask the local LLM (Ollama) a question. Prompt from arguments or stdin.
# Usage: scripts/ask-local.sh "prompt"   |   echo "prompt" | scripts/ask-local.sh
# Do NOT run while Gazebo is running (shares the GPU).
set -euo pipefail

MODEL="${ASK_LOCAL_MODEL:-qwen2.5-coder:3b}"

if [ $# -gt 0 ]; then
  prompt="$*"
elif [ ! -t 0 ]; then
  prompt="$(cat)"
else
  echo "usage: $0 \"prompt\"  (or pipe the prompt on stdin)" >&2
  exit 1
fi

if pgrep -f "^gz sim" >/dev/null; then
  echo "refusing: Gazebo is running and shares the GPU. Stop the sim first." >&2
  exit 1
fi

# stdin from /dev/null and stderr captured: keeps ollama's spinner out of the output
err="$(mktemp)"
trap 'rm -f "$err"' EXIT
ollama run "$MODEL" "$prompt" </dev/null 2>"$err" || { cat "$err" >&2; exit 1; }
