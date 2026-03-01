#!/usr/bin/env bash
set -euo pipefail

# Create a new research task folder with a standard scaffold.
# Usage:
#   ./scripts/new_task.sh my-task-name
#
# Notes:
# - This script does NOT create a git branch.
# - Recommended flow:
#   git checkout -b task/<my-task-name>
#   ./scripts/new_task.sh <my-task-name>
#   $EDITOR TASKS.md
#   git add ... && git commit && git push -u origin HEAD

TASK_NAME="${1:-}"
if [[ -z "$TASK_NAME" ]]; then
  echo "usage: $0 <task-name>" >&2
  exit 2
fi

# simple kebab-case check
if ! [[ "$TASK_NAME" =~ ^[a-z0-9]+([a-z0-9-]*[a-z0-9]+)?$ ]]; then
  echo "error: task name should be kebab-case (lowercase letters/numbers/hyphens)" >&2
  exit 2
fi

if [[ -e "$TASK_NAME" ]]; then
  echo "error: path already exists: $TASK_NAME" >&2
  exit 1
fi

mkdir -p "$TASK_NAME"/{code,data/raw,data/processed,results/figures,results/reports}

ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$TASK_NAME/notes.md" <<EOF
# Notes — $TASK_NAME

## $ts — start

- Objective:
- Constraints:
- Plan:

EOF

cat > "$TASK_NAME/README.md" <<EOF
# $TASK_NAME

## Objective

## Background

## Method

## Setup

## Results

## Conclusions

## Next steps
EOF

echo "Created task scaffold at: $TASK_NAME"
