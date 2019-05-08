#!/bin/bash
set -o errexit
script_dir="${SCRIPT_DIR:-$(dirname $0)/../}"
train_dir="${TRAIN_DIR:-$script_dir/train/}"
corpus_name="${1:-$CORPUS_NAME}"

echo -n "Loading utils from $train_dir..." 
# shellcheck source=./util.sh
source "$train_dir/util.sh"
echo "Done!"

activate_debug
load_runtime "$CONFIG_DIR"

corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"
target_dir="${TARGET_DIR:-${corpus_dir}/preprocess/}"
mkdir --parent "$target_dir"

load_env "$config_dir/$corpus_name/environ"
echo "Running preprocess..."
if [ ! -f   "$config_dir/$corpus_name/preprocess.config" ]
then
	echo "Config not found!"
	return 1
elif [ -n "$(ls "$target_dir")" ]
then
	echo "Target dir not empty!"
	return 1
else
echo "Using config from $config_dir/$corpus_name/preprocess.config"
cat  "$config_dir/$corpus_name/preprocess.config"
fi

cd "$work_dir"
$pipenv_bin run python "$onmt_dir/preprocess.py"  --config "$config_dir/$corpus_name/preprocess.config"
