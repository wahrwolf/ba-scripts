#!/bin/bash
set -o errexit
script_dir="${SCRIPT_DIR:-$(dirname $0)/../}"
train_dir="${TRAIN_DIR:-$script_dir/train/}"
corpus_name="${1:-$CORPUS_NAME}"

# shellcheck source=./util.sh
echo -n "Loading utils from $train_dir..." 
source "$train_dir/util.sh"
echo "Done!"

activate_debug
load_runtime "$CONFIG_DIR"

corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"
target_dir="${TARGET_DIR:-${corpus_dir}/preprocess/}"
mkdir --parent "$target_dir"

load_env "$config_dir/$corpus_name/environ"

echo "Running preprocess..."
echo "Using config from $config_dir/$corpus_name/preprocess.config"
cat  "$config_dir/$corpus_name/preprocess.config"
cd "$work_dir"
$pipenv_bin run python "$onmt_dir/preprocess.py"  --config "$config_dir/$corpus_name/preprocess.config"
