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

# stolen from: https://stackoverflow.com/questions/6593531/running-a-limited-number-of-child-processes-in-parallel-in-bash

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

todo_array=("$corpus_dir"/*train.*/)

index=0
max_jobs=${MAX_JOBS:-10}

function add_next_job {
	# if still jobs to do then add one
	if [[ $index -lt ${#todo_array[*]} ]]
		# the hash in the if is not a comment - rather it's bash awkward way of getting its length
	then
		echo adding job "${todo_array[$index]}"
		do_job "${todo_array[$index]}" & 
		index=$(($index+1))
		fi
	}

set -o monitor 
# means: run background processes in a separate processes...
trap add_next_job CHLD 
# execute add_next_job when we receive a child complete signal

function do_job {
	run=$1
	if [ ! -d "$run" ]; then
		echo "[$run]: Run (§run) is not a valid directory! Skipping..."
		return
	else
		echo "Translating models from $run"
	fi

	echo "[$run]:Gathering reference text..."
	head --lines 1000 "$corpus_dir/$VALID_SRC" > "$run/source.raw"
	head --lines 1000 "$corpus_dir/$VALID_TARGET" > "$run/reference.raw"
	echo "Done"

	echo "[$run]: Removing BPE..."
	for data in source reference
	do
		sed --regexp-extended 's/(@@ |@@ ?$)//g' "$run/$data.raw" > "$run/$data.txt"
	done
	echo "Done"

	for model in "$run"/*.pt
	do
		if [ ! -f "$model" ]; then
			echo "[$run]: Model ($model) is not a valid file!"
			continue
		else
			echo "[$run]: Testing $model..."
		fi
		if [ -f ""$run/translation-$(basename --suffix .pt "$model").raw"" ]
		then
			echo "[$run]: Found existing translation!"
		else
			$pipenv_bin run python "$onmt_dir/translate.py"  \
				--src "$run/source.raw" \
				--config "$config_dir/$corpus_name/score.config" \
				--model "$model" \
				--output "$run/translation.raw"
		fi
		echo "[$run]: Removing BPE..."
		sed --regexp-extended 's/(@@ |@@ ?$)//g' "$run/translation.raw" > "$run/translation.txt"
		echo "Done"
		mv "$run/translation.raw" "$run/translation-$(basename --suffix .pt "$model").raw"
		mv "$run/translation.txt" "$run/translation-$(basename --suffix .pt "$model").txt"
		echo "[$run]: Calculating Scores..."
		echo "[$run]: Calculating BLEU:"
		echo "[$run]: " $("$onmt_dir/tools/multi-bleu-detok.perl" \
		   	"$run/reference.txt" \
			< "$run/translation-$(basename --suffix .pt "$model").txt")
		echo "[$run]: " $("$onmt_dir/tools/multi-bleu-detok.perl" \
			-lc "$run/reference.txt" \
			< "$run/translation-$(basename --suffix .pt "$model").txt")
		echo "[$run]: Calculating ROUGE:"
		echo "[$run]: " $($pipenv_bin run python \
			"$onmt_dir/tools/test_rouge.py" \
				-r "$run/reference.txt" \
				-c "$run/translation-$(basename --suffix .pt "$model").txt")
		echo "[$run]: Finished $model"

	done
}

while [[ $index -lt $max_jobs ]]
do
	add_next_job
done



