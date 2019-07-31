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

for run in "$corpus_dir"/*train.*/
do
	if [ ! -d "$run" ]; then
		"Run (§run) is not a valid directory! Skipping..."
		continue
	else
		echo "Translating models from $run"
	fi

	echo -n "Gathering reference text..."
	cp "$corpus_dir/$VALID_SRC" "$run/source.raw"
	cp "$corpus_dir/$VALID_TARGET" "$run/reference.raw"
	echo "Done"

	echo -n "Removing BPE..."
	for data in source reference
	do
		sed --regexp-extended 's/(@@ |@@ ?$)//g' "$run/$data.raw" > "$run/$data.txt"
	done
	echo "Done"

	for model in "$run"/*.pt
	do (
		if [ ! -f "$model" ]; then
			echo "Model ($model) is not a valid file!"
			continue
		else
			echo "Testing $model..."
		fi
		if [ -f "$model_dir/translation.raw" ]
		then
			echo "Found existing translation!"
		else
			$pipenv_bin run python "$onmt_dir/translate.py"  \
				--config "$config_dir/$corpus_name/score.config" \
				--model "$model" \
				--output "$run/translation.raw"
		fi
		echo -n "Removing BPE..."
		sed --regexp-extended 's/(@@ |@@ ?$)//g' "$run/translation.raw" > "$run/translation.txt"
		echo "Done"
		rename translation "translation-$(basename --suffix .pt "$model")" "$run/translation."{raw,txt}
		echo "Calculating Scores..."
		echo "==================="
		echo "Calculating BLEU:"
		"$onmt_dir/tools/multi-bleu-detok.perl"     "$run/reference.txt" "$run/translation-$model.txt"
		"$onmt_dir/tools/multi-bleu-detok.perl" -lc "$run/reference.txt" "$run/translation-$model.txt"
		echo "Calculating ROUGE:"
		"$onmt_dir/tools/test_rouge.py" -r "$run/reference.txt" -c "$run/translation-$model.txt"
		echo "-------------------"

		)& done
done

echo "Done"
