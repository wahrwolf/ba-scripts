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

	for domain in ECB EMEA Europarl mixed
	do
		echo "[$run]:Gathering text..."
		cp "$corpus_dir/$TEST_SRC.$domain" "$run/source-$domain.raw"
		echo "[$run]: Removing BPE..."
		sed --regexp-extended 's/(@@ |@@ ?$)//g' "$corpus_dir/$TEST_TARGET.$domain" > "$run/reference-$domain.txt"

		for model in "$run"/*.pt
		do
			if [ ! -f "$model" ]; then
				echo "[$run]: Model ($model) is not a valid file!"
				continue
			else
				echo "[$run]: Testing $model..."
			fi
			model_name=$(basename --suffix .pt "$model")
			if [ -f "$run/translation-$domain-$model_name.txt" ]
			then
				echo "[$run]: Found existing translation!"
			else
				if [ -z ${skip_training+x} ]
				then
					return
				fi
				$pipenv_bin run python "$onmt_dir/translate.py"  \
					--src "$run/source-$domain.raw" \
					--config "$config_dir/$corpus_name/score.config" \
					--model "$model" \
					--output "$run/translation.raw"
				echo "[$run]: Removing BPE..."
				sed --regexp-extended 's/(@@ |@@ ?$)//g' "$run/translation.raw" > "$run/translation.txt"
				echo "Done"
				mv --verbose "$run/translation.raw" "$run/translation-$domain-$model_name.raw"
				mv --verbose "$run/translation.txt" "$run/translation-$domain-$model_name.txt"
			fi
			echo "[$run]: Calculating BLEU for $domain:"
			echo "[$run]: " $("$onmt_dir/tools/multi-bleu-detok.perl" \
				"$run/reference-$domain.txt" \
				< "$run/translation-$domain-$model_name.txt" \
				> "$run/bleu-$domain-$model_name.score")
			echo -n "LC-" >> "$run/bleu-$domain-$model_name.score"
			echo "[$run]: " $("$onmt_dir/tools/multi-bleu-detok.perl" \
				-lc "$run/reference-$domain.txt" \
				< "$run/translation-$domain-$model_name.txt" \
				>> "$run/bleu-$domain-$model_name.score")
			echo "[$run]: Calculating ROUGE for $domain:"
			echo "[$run]: " $($pipenv_bin run python \
					-m rouge.rouge \
					--output_filename="$run/rouge-$domain-$model_name.score" \
					--target_filepattern="$run/reference-$domain.txt" \
					--prediction_filepattern="$run/translation-$domain-$model_name.txt")
			echo "[$run]: Calculating nlg for $domain:"
			echo "[$run]: " $($pipenv_bin run nlg-eval \
					--references="$run/reference-$domain.txt" \
					--hypothesis="$run/translation-$domain-$model_name.txt" \
					> "$run/nlg_eval-$domain-$model_name.score")
		done

	done
}

while [[ $index -lt $max_jobs ]]
do
	add_next_job
done
