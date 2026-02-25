#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

VOLUME_NAME="${VOLUME_NAME:-kan-sr}"
REMOTE_BASE="${REMOTE_BASE:-/runs}"
LOCAL_BASE="${LOCAL_BASE:-"$REPO_ROOT/runs"}"

usage() {
  cat <<'EOF'
Usage:
  scripts/sync_from_modal.sh ls
  scripts/sync_from_modal.sh latest
  scripts/sync_from_modal.sh <run_id>
  scripts/sync_from_modal.sh <remote_path>

Defaults (override via env):
  VOLUME_NAME=kan-sr
  REMOTE_BASE=/runs
  LOCAL_BASE=<repo>/runs

Examples:
  scripts/sync_from_modal.sh ls
  scripts/sync_from_modal.sh latest
  scripts/sync_from_modal.sh 2026-02-25_001
  VOLUME_NAME=my-vol scripts/sync_from_modal.sh /runs/2026-02-25_001
EOF
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing command: $1" >&2
    exit 1
  fi
}

require_cmd modal

action="${1:-}"
if [[ -z "$action" || "$action" == "-h" || "$action" == "--help" ]]; then
  usage
  exit 0
fi

mkdir -p "$LOCAL_BASE"

if [[ "$action" == "ls" ]]; then
  modal volume ls "$VOLUME_NAME" "$REMOTE_BASE"
  exit 0
fi

remote_path=""
is_dir_sync="0"
if [[ "$action" == "latest" ]]; then
  is_dir_sync="1"
  # Pick the lexicographically-latest entry under REMOTE_BASE.
  # Assumes your run directories are named with sortable timestamps (e.g., YYYY-MM-DD_HHMM).
  latest_name="$(
    modal volume ls "$VOLUME_NAME" "$REMOTE_BASE" 2>/dev/null \
      | awk '{print $NF}' \
      | sed 's:/*$::' \
      | awk 'NF' \
      | sort \
      | tail -n 1
  )"

  if [[ -z "$latest_name" ]]; then
    echo "No runs found under ${VOLUME_NAME}:${REMOTE_BASE}" >&2
    exit 2
  fi

  remote_base_no_slash="${REMOTE_BASE#/}" # e.g. "/runs" -> "runs"
  if [[ "$latest_name" == /* ]]; then
    remote_path="$latest_name"
  elif [[ "$latest_name" == "$remote_base_no_slash/"* ]]; then
    remote_path="/$latest_name"
  else
    remote_path="${REMOTE_BASE%/}/$latest_name"
  fi
else
  if [[ "$action" == /* ]]; then
    remote_path="$action"
  elif [[ "$action" == */* ]]; then
    # If user passes something like "runs/<id>", treat it as a full remote path.
    remote_path="/$action"
  else
    is_dir_sync="1"
    remote_path="${REMOTE_BASE%/}/$action"
  fi
fi

if [[ "$is_dir_sync" == "1" && "$remote_path" != */ ]]; then
  remote_path="${remote_path}/"
fi

run_name="$(basename -- "$remote_path")"
local_dest="$LOCAL_BASE"
if [[ "$is_dir_sync" != "1" ]]; then
  local_dest="${LOCAL_BASE%/}/$run_name"
fi

echo "Syncing ${VOLUME_NAME}:${remote_path} -> ${local_dest}"
if ! modal volume get "$VOLUME_NAME" "$remote_path" "$local_dest" --force; then
  echo "Retrying without --force (clearing destination first)..." >&2
  cleanup_target="$local_dest"
  if [[ "$is_dir_sync" == "1" ]]; then
    cleanup_target="${LOCAL_BASE%/}/$run_name"
  fi
  rm -rf "$cleanup_target"
  modal volume get "$VOLUME_NAME" "$remote_path" "$local_dest"
fi
