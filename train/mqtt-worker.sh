#!/bin/bash
set -o errexit

# shellcheck source=./util.sh
source "$(dirname $0)/util.sh"
activate_debug

export tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
export work_dir="${WORK_DIR:-$tmp_dir/workbench}"
export data_dir="${DATA_DIR:-/data/4dahmen/}"
export config_dir="${CONFIG_DIR:-${data_dir}/config}"
export corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"

export script_dir=${SCRIPT_DIR:-$tmp_dir/scripts/}
export onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}
export bish_dir=${BISH_DIR:-$tmp_dir/bish/}

mkdir --parent "$work_dir"
cd "$work_dir"
$bish_dir/bish-bosh --verbose 1 -- "$config_dir/mqtt/gpu-worker.snippet"
