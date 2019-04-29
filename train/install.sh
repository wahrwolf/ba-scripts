#!/bin/bash
set -o errexit

source "$(dirname $0)/util.sh"
activate_debug

tmp_dir=${TMP_DIR:-"$(mktemp --directory)"}
work_dir=${WORK_DIR:-$tmp_dir/workbench}

script_dir=${SCRIPT_DIR:-$tmp_dir/scripts/}
script_url=${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}
pip_url=${PIP_URL:-https://bootstrap.pypa.io/get-pip.py}
onmt_url=${ONMT_URL:-git://github.com/OpenNMT/OpenNMT-py}
onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}
bish_url=${BISH_URL:-git://github.com/raphaelcohn/bish-bosh}
bish_dir=${BISH_DIR:-$tmp_dir/bish/}

# get and update net-trainer

# install files
# install the script {{{
if git ls-remote "$script_dir" 2>/dev/null 1>&2
then
	git -C "$script_dir" pull
else
	git clone "$script_url" "${script_dir}"
fi
#}}}

# install bish-bosh {{{
if git ls-remote "$bish_dir" 2>/dev/null 1>&2
then
	git -C "$bish_dir" pull
else
	git clone "$bish_url" "${bish_dir}"
fi
git -C "$bish_dir" submodule update --init --recursive

bish_bin="${bish_dir}/bish-bosh"
chmod +x "$bish_bin"
# }}}

# install python
# install pip {{{
pip_path=${PIP_PATH:-${tmp_dir}/bin/pip}
pip_dir=$(dirname $(dirname $pip_path))

if [[ -x "$PIP_PATH" ]] ; then

	pip_path="$PIP_PATH"
else
	curl "$pip_url" --output "${tmp_dir}/get-pip.py"
	python3 "${tmp_dir}/get-pip.py" --prefix="${pip_dir}" pip
fi

export PYTHONPATH=$PYTHONPATH:$pip_dir/lib/$(ls $pip_dir/lib)/site-packages/

echo "New path: pip@[$pip_path] PYTHONPATH@[$PYTHONPATH]"
echo "Using $(python3 $pip_path --version)"

# }}}

# install pipenv {{{
$pip_path install --ignore-installed --install-option="--prefix=${pip_dir}" pipenv
penv="${pip_dir}/bin/pipenv"
# }}}

# install OpenNMT-py {{{
if git ls-remote "$onmt_dir" 2>/dev/null 1>&2
then
	git -C "$onmt_dir" pull
else
	git clone "$onmt_url" "${onmt_dir}"
fi

# install onmt (including pyyaml for use of configs)
mkdir -p "$work_dir"
cd "$work_dir"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install -e "${onmt_dir}"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install pyyaml
PIPENV_VENV_IN_PROJECT='enabled' "$penv" run pip install -r "${onmt_dir}"/requirements.txt



# test onmt {{{
test_dir=$(mktemp --directory)

#pipenv run python -m unittest discover
# test nmt preprocessing
pipenv run python $onmt_dir/preprocess.py -train_src $onmt_dir/data/src-train.txt -train_tgt $onmt_dir/data/tgt-train.txt -valid_src $onmt_dir/data/src-val.txt -valid_tgt $onmt_dir/data/tgt-val.txt -save_data $test_dir/data -src_vocab_size 1000 -tgt_vocab_size 1000 && rm -rf $test_dir/data*.pt
# test nmt translation
head $onmt_dir/data/src-test.txt > $test_dir/src-test.txt; pipenv run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model.pt -src $test_dir/src-test.txt -verbose
# test nmt ensemble translation
head $onmt_dir/data/src-test.txt > $test_dir/src-test.txt; pipenv run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model.pt $onmt_dir/onmt/tests/test_model.pt -src $test_dir/src-test.txt -verbose
# test nmt preprocessing and training
head $onmt_dir/data/src-val.txt > $test_dir/src-val.txt; head $onmt_dir/data/tgt-val.txt > $test_dir/tgt-val.txt; pipenv run python $onmt_dir/preprocess.py -train_src $test_dir/src-val.txt -train_tgt $test_dir/tgt-val.txt -valid_src $test_dir/src-val.txt -valid_tgt $test_dir/tgt-val.txt -save_data $test_dir/q -src_vocab_size 1000 -tgt_vocab_size 1000; pipenv run python $onmt_dir/train.py -data $test_dir/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -train_steps 10 && rm -rf $test_dir/q*.pt
# test nmt preprocessing w/ sharding and training w/copy
head $onmt_dir/data/src-val.txt > $test_dir/src-val.txt; head $onmt_dir/data/tgt-val.txt > $test_dir/tgt-val.txt; pipenv run python $onmt_dir/preprocess.py -train_src $test_dir/src-val.txt -train_tgt $test_dir/tgt-val.txt -valid_src $test_dir/src-val.txt -valid_tgt $test_dir/tgt-val.txt -shard_size 1 -dynamic_dict -save_data $test_dir/q -src_vocab_size 1000 -tgt_vocab_size 1000; pipenv run python $onmt_dir/train.py -data $test_dir/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -copy_attn -train_steps 10 && rm -rf $test_dir/q*.pt

# test nmt translation
pipenv run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model2.pt  -src  $onmt_dir/data/morph/src.valid  -verbose -batch_size 10 -beam_size 10 -tgt $onmt_dir/data/morph/tgt.valid -out $test_dir/trans; diff  $onmt_dir/data/morph/tgt.valid $test_dir/trans
# test nmt translation with random sampling
pipenv run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model2.pt  -src  $onmt_dir/data/morph/src.valid  -verbose -batch_size 10 -beam_size 1 -seed 1 -random_sampling_topk "-1" -random_sampling_temp 0.0001 -tgt $onmt_dir/data/morph/tgt.valid -out $test_dir/trans; diff  $onmt_dir/data/morph/tgt.valid $test_dir/trans
# test tool
PYTHONPATH=$PYTHONPATH:. pipenv run python $onmt_dir/tools/extract_embeddings.py -model $onmt_dir/onmt/tests/test_model.pt

#}}}
#}}}

# vim: foldmethod=marker
