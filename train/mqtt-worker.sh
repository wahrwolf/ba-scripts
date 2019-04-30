#!/bin/bash
set -o errexit

# shellcheck source=./util.sh
source "$(dirname $0)/util.sh"
activate_debug

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
work_dir="${WORK_DIR:-$tmp_dir/workbench}"
data_dir="${DATA_DIR:-/data/4dahmen/}"
config_dir="${CONFIG_DIR:-${data_dir}/config}"
corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"

script_dir=${SCRIPT_DIR:-$tmp_dir/scripts/}
onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}
bish_dir=${BISH_DIR:-$tmp_dir/bish/}

mkdir --parent "$work_dir"
cd "$work_dir"
$bish_dir/bish-bosh --verbose 1 -- "$config_dir/mqtt-worker.snippet"
