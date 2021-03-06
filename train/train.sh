#!/bin/bash
set -o errexit
script_dir="${SCRIPT_DIR:-$(dirname "$0")/../}"
train_dir="${TRAIN_DIR:-$script_dir/train/}"
corpus_name="${1:-$CORPUS_NAME}"

echo -n "Loading utils from $train_dir..." 
# shellcheck source=./util.sh
source "$train_dir/util.sh"
echo "Done!"

activate_debug
load_runtime "$CONFIG_DIR"

corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"
target_dir="${TARGET_DIR:-${corpus_dir}/train/}"
mkdir --parent "$target_dir"

load_env "$config_dir/$corpus_name/environ"

for config in "$config_dir/$corpus_name/queue/"*
do
	time="$(date --iso-8601=hours)"
	echo "Running train with config $config..."
	if [ ! -f   "$config_dir/$corpus_name/train.config" ]
	then
		echo "Config not found! Loading next from queue"
		envsubst < "$config" | tee  "$config_dir/$corpus_name/train.config"
		echo "Using config from $config_dir/$corpus_name/train.config"
		
	elif [ -n "$(ls "$target_dir")" ]
	then
		echo "Target dir not empty!"
		exit 1
	else
	echo "Using config from $config_dir/$corpus_name/train.config"
	cat  "$config_dir/$corpus_name/train.config"
	fi

	cd "$work_dir"
	set +o errexit
		$pipenv_bin run python "$onmt_dir/train.py"  --config "$config_dir/$corpus_name/train.config"
	set -o errexit
	echo -n "Finished training! Backup files..."
		mkdir --parent "$corpus_dir/train.$time"
		mv "$target_dir" "$config_dir/$corpus_name/train.config" "$corpus_dir/train.$time"
	echo "Done"
	echo -n "Removing last used config..."
		rm "$config"
	echo "Done"
done
