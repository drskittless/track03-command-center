#!/bin/sh
set -e

uv run python -m scripts.gen_contract
pnpm -C apps/web gen:types
