#!/bin/sh
set -e

if [ "$#" -ne 1 ] || ! case "$1" in parth|kshitij|prajjwal) true ;; *) false ;; esac; then
    printf '%s\n' "usage: $0 {parth|kshitij|prajjwal}" >&2
    exit 1
fi

role=$1
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

printf '%s\n' "$role" > .role
git config core.hooksPath .githooks
uv sync
pnpm -C apps/web install
printf '%s\n' "setup done for $role"
