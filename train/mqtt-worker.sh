#!/bin/bash
set -o errexit

# shellcheck source=./util.sh
source "$(dirname "$0")/util.sh"
activate_debug
load_runtime "$1"

mkdir --parent "$work_dir"
cd "$work_dir"
"$bish_dir/bish-bosh" --verbose 1 -- "$config_dir/mqtt/gpu-worker.snippet"
