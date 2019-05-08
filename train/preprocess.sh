#!/bin/bash
set -o errexit
script_dir="${SCRIPT_DIR:-$(dirname $0)/../}"
train_dir="${TRAIN_DIR:-$script_dir/train/}"

# shellcheck source=./util.sh
echo -n "Loading utils from $train_dir..." 
source "$train_dir/util.sh"
echo "Done!"

load_env "$train_dir/config/environ"

corpus_name="${1:-$CORPUS_NAME}"
activate_debug
load_runtime "$CONFIG_DIR"

corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"

load_env "$config_dir/$corpus_name/environ"

target_dir="${TARGET_DIR:-${corpus_dir}/preprocess/}"
mkdir --parent "$target_dir"

echo "Running preprocess..."
mkdir --parent "$work_dir"
cd "$work_dir"
export PYTHONPATH="$PYTHONPATH:$pip_dir/lib/$(ls $pip_dir/lib)/site-packages/"
$pipenv_bin run python "$onmt_dir/preprocess.py"  --config "$config_dir/$corpus_name/preprocess.config"
