#!/usr/bin/env bash
# Clone upstream tpprl and apply the one-item patch.
set -euo pipefail

cd "$(dirname "$0")"

if [ -d upstream ]; then
    echo "upstream/ already exists. Remove it first if you want a clean apply." >&2
    exit 1
fi

git clone https://github.com/Networks-Learning/tpprl.git upstream
cd upstream
git apply --3way ../one_item.patch
echo
echo "Patch applied. See ../README.md for the run commands."
