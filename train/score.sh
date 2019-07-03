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
if [ ! -f   "$config_dir/$corpus_name/score.config" ]
then
	echo "Config not found!"
	exit 1
else
	echo "Using config from $config_dir/$corpus_name/score.config"
	cat  "$config_dir/$corpus_name/score.config"
fi

cd "$work_dir"

for model in "$corpus_dir"/train.*/*
do
	echo "Testing $model..."
	model_name=$(basename "$model")
	experiment=$(basename "$(dirname "$model")")
	model_dir="$target_dir/$experiment/$model_name"
	mkdir --parent "$model_dir"
	$pipenv_bin run python "$onmt_dir/translate.py"  --config "$config_dir/$corpus_name/score.config" --model "$model" --output "$model_dir/translation.out"
	echo -n "Removing BPE..."
	sed --regexp-extended 's/(@@ |@@ ?$)//g' --in-place "$model_dir/translation.out"
	echo "Done"
	echo "Calculating BLEU..."
	echo "==================="
	"$onmt_dir/tools/multi-bleu-detok.perl" <(sed --regexp-extended 's/(@@ |@@ ?$)//g' "$corpus_dir/$VALID_TARGET") < "$model_dir/translation.out"
	echo "-------------------"
done

echo -n "Finished translateing! Backup files..."
mv "$target_dir" "$corpus_dir/translate.$TIME"
echo "Done"
