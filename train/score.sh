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
target_dir="${TARGET_DIR:-${corpus_dir}/translate/}"
load_env "$config_dir/$corpus_name/environ"

echo "Loading up config..."
if [ ! -f   "$config_dir/$corpus_name/translate.config" ]
then
	echo "Config not found!"
	exit 1
else
	echo "Using config from $config_dir/$corpus_name/translate.config"
	cat  "$config_dir/$corpus_name/translate.config"
fi

cd "$work_dir"

for model in "$corpus_dir"/train.*/*
do
	echo "Testing $model..."
	mkdir --parent "$(dirname "$model")"
	$pipenv_bin run python "$onmt_dir/translate.py"  --config "$config_dir/$corpus_name/translate.config" --model "$model" --output "$target_dir/$model.out"
	echo -n "Removing BPE..."
	sed --regexp-extended 's/(@@ |@@ ?$)//g' --in-place "$target_dir/$model.out"
	echo "Done"
	echo "Calculating BLEU..."
	echo "==================="
	"$onmt_dir/tools/multi-bleu-detok.perl" <(sed --regexp-extended 's/(@@ |@@ ?$)//g' "$corpus_dir/$VALID_TARGET") < "$target_dir/$model.out"
	echo "-------------------"
done

echo -n "Finished translateing! Backup files..."
mv "$target_dir" "$corpus_dir/translate.$TIME"
echo "Done"
