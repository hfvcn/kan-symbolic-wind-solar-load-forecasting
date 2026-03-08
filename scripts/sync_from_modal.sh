#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

VOLUME_NAME="${VOLUME_NAME:-kan-sr}"
REMOTE_BASE="${REMOTE_BASE:-/runs}"
LOCAL_BASE="${LOCAL_BASE:-"$REPO_ROOT/runs"}"
FILE_GET_RETRIES="${FILE_GET_RETRIES:-3}"

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

find_payload_root() {
  local search_root="$1"
  local count="0"
  local payload_path=""

  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    count="$((count + 1))"
    payload_path="$path"
    if [[ "$count" -gt 1 ]]; then
      break
    fi
  done < <(find "$search_root" -maxdepth 3 -type f -name payload.json 2>/dev/null)

  if [[ "$count" -ne 1 ]]; then
    echo "ERROR: Could not uniquely locate payload.json after download (found=${count})." >&2
    echo "Temp dir: $search_root" >&2
    return 1
  fi

  dirname -- "$payload_path"
}

download_remote_file() {
  local remote_file="$1"
  local local_dir="$2"
  local attempt="1"
  local local_file=""

  mkdir -p "$local_dir"
  local_file="$local_dir/$(basename -- "$remote_file")"
  while true; do
    rm -f "$local_file"
    if modal volume get "$VOLUME_NAME" "$remote_file" "$local_dir" --force; then
      return 0
    fi
    if [[ "$attempt" -ge "$FILE_GET_RETRIES" ]]; then
      echo "ERROR: Failed to download file after ${FILE_GET_RETRIES} attempts: ${VOLUME_NAME}:${remote_file}" >&2
      return 1
    fi
    echo "Retrying file download (${attempt}/${FILE_GET_RETRIES}) for ${VOLUME_NAME}:${remote_file}" >&2
    attempt="$((attempt + 1))"
    sleep 1
  done
}

sync_remote_tree() {
  local remote_path="${1%/}"
  local local_path="$2"
  local listing=""
  local line_count=""

  if ! listing="$(modal volume ls "$VOLUME_NAME" "$remote_path" 2>/dev/null)"; then
    if download_remote_file "$remote_path" "$(dirname -- "$local_path")" >/dev/null 2>&1; then
      return 0
    fi
    echo "ERROR: Failed to list remote path during recursive sync: ${VOLUME_NAME}:${remote_path}" >&2
    return 1
  fi

  listing="$(printf '%s\n' "$listing" | sed '/^[[:space:]]*$/d')"
  if [[ -z "$listing" ]]; then
    mkdir -p "$local_path"
    return 0
  fi

  line_count="$(printf '%s\n' "$listing" | wc -l | tr -d ' ')"
  if [[ "$line_count" == "1" && "$listing" == "$remote_path" ]]; then
    download_remote_file "$remote_path" "$(dirname -- "$local_path")"
    return 0
  fi

  mkdir -p "$local_path"
  while IFS= read -r child; do
    [[ -z "$child" ]] && continue
    sync_remote_tree "$child" "$local_path/$(basename -- "$child")"
  done <<< "$listing"
}

sync_run_minimal_paths() {
  local remote_run_dir="${1%/}"
  local local_run_dir="$2"
  local optional_dir=""

  mkdir -p "$local_run_dir"

  if modal volume ls "$VOLUME_NAME" "$remote_run_dir/payload.json" >/dev/null 2>&1; then
    download_remote_file "$remote_run_dir/payload.json" "$local_run_dir"
  else
    echo "ERROR: Missing payload.json in ${VOLUME_NAME}:${remote_run_dir}" >&2
    return 1
  fi

  for optional_dir in processed artifacts checkpoint reports; do
    if modal volume ls "$VOLUME_NAME" "$remote_run_dir/$optional_dir" >/dev/null 2>&1; then
      sync_remote_tree "$remote_run_dir/$optional_dir" "$local_run_dir/$optional_dir"
    fi
  done
}

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
local_dest="${LOCAL_BASE%/}/$run_name"

echo "Syncing ${VOLUME_NAME}:${remote_path} -> ${local_dest}"

if [[ "$is_dir_sync" == "1" ]]; then
  # Robust directory sync:
  # - Download into a temp directory (Modal CLI may nest paths differently)
  # - Detect the actual run root (payload.json location)
  # - Replace local_dest atomically-ish (rm + copy)
  tmp_dir="$(mktemp -d "${LOCAL_BASE%/}/.tmp_modal_sync_${run_name}_XXXXXX")"
  cleanup() {
    rm -rf "$tmp_dir"
  }
  trap cleanup EXIT

  if ! modal volume get "$VOLUME_NAME" "$remote_path" "$tmp_dir" --force; then
    echo "Retrying without --force (clearing temp dir first)..." >&2
    rm -rf "$tmp_dir"
    tmp_dir="$(mktemp -d "${LOCAL_BASE%/}/.tmp_modal_sync_${run_name}_XXXXXX")"
    trap cleanup EXIT
    if ! modal volume get "$VOLUME_NAME" "$remote_path" "$tmp_dir"; then
      echo "Directory sync failed again; switching to minimal recursive sync (payload/processed/artifacts/checkpoint/reports)." >&2
      rm -rf "$tmp_dir"
      tmp_dir="$(mktemp -d "${LOCAL_BASE%/}/.tmp_modal_sync_${run_name}_XXXXXX")"
      trap cleanup EXIT
      sync_run_minimal_paths "${remote_path%/}" "$tmp_dir/$run_name"
    fi
  fi

  content_root=""
  if [[ -f "$tmp_dir/payload.json" ]]; then
    content_root="$tmp_dir"
  elif [[ -f "$tmp_dir/$run_name/payload.json" ]]; then
    content_root="$tmp_dir/$run_name"
  elif [[ -f "$tmp_dir/runs/$run_name/payload.json" ]]; then
    content_root="$tmp_dir/runs/$run_name"
  else
    content_root="$(find_payload_root "$tmp_dir")" || exit 3
  fi

  rm -rf "$local_dest"
  mkdir -p "$local_dest"
  cp -a "$content_root/." "$local_dest/"

  trap - EXIT
  rm -rf "$tmp_dir"
else
  mkdir -p "$local_dest"
  if ! modal volume get "$VOLUME_NAME" "$remote_path" "$local_dest" --force; then
    echo "Retrying without --force (clearing destination first)..." >&2
    rm -rf "$local_dest"
    mkdir -p "$local_dest"
    modal volume get "$VOLUME_NAME" "$remote_path" "$local_dest"
  fi
fi
