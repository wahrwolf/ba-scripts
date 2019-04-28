#!/bin/bash
set -e

debug_mail=${DEBUG_MAIL:-vincent.dahmen@gmail.com}
mail_tag=${DEBUG_MAIL_TAG:-[BA]}
machine=${MASCHINE:-"$(whoami)@$(hostname)"}
module_name=$0

# enable debug {{{
failure() {
	local line_number=$1
	local msg=$2
	if [ -z "$debug_mail" ]
	then
		echo "[${module_name}@${line_number}]: $msg"
	else
		sendmail "$debug_mail" \
<<EOF
Subject:$mail_tag: $machine
$module_name failed at $line_number
$msg
EOF
	fi

}

trap 'failure ${LINENO} "$BASH_COMMAND"' ERR
# }}}
# }}}

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
	python3 "${tmp_dir}/get-pip.py" --ignore-installed --no-cache-dir --isolated --prefix="${pip_dir}" pip wheel setuptools
fi

echo "Using $pip_path --version)"

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

# install all requirements for onmt (including pyyaml for use of conifgs
mkdir -p "$work_dir"
cd "$work_dir"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install "${onmt_dir}"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install pyyaml

# test onmt (everything here is stolen from the github travis) {{{
test_dir=$(mktemp --directory)

PIPENV_VENV_IN_PROJECT='enabled' "$penv" shell
cd "$onmt_dir"

wget -O $test_dir/im2text.tgz http://lstm.seas.harvard.edu/latex/im2text_small.tgz; tar zxf $test_dir/im2text.tgz -C $test_dir/; head $test_dir/im2text/src-train.txt > $test_dir/im2text/src-train-head.txt; head $test_dir/im2text/tgt-train.txt > $test_dir/im2text/tgt-train-head.txt; head $test_dir/im2text/src-val.txt > $test_dir/im2text/src-val-head.txt; head $test_dir/im2text/tgt-val.txt > $test_dir/im2text/tgt-val-head.txt
wget -O $test_dir/speech.tgz http://lstm.seas.harvard.edu/latex/speech.tgz; tar zxf $test_dir/speech.tgz -C $test_dir/; head $test_dir/speech/src-train.txt > $test_dir/speech/src-train-head.txt; head $test_dir/speech/tgt-train.txt > $test_dir/speech/tgt-train-head.txt; head $test_dir/speech/src-val.txt > $test_dir/speech/src-val-head.txt; head $test_dir/speech/tgt-val.txt > $test_dir/speech/tgt-val-head.txt
 wget -O $test_dir/test_model_speech.pt http://lstm.seas.harvard.edu/latex/model_step_2760.pt
 wget -O $test_dir/test_model_im2text.pt http://lstm.seas.harvard.edu/latex/test_model_im2text.pt
 python -m unittest discover
# test nmt preprocessing
 python preprocess.py -train_src data/src-train.txt -train_tgt data/tgt-train.txt -valid_src data/src-val.txt -valid_tgt data/tgt-val.txt -save_data $test_dir/data -src_vocab_size 1000 -tgt_vocab_size 1000 && rm -rf $test_dir/data*.pt
# test im2text preprocessing
 python preprocess.py -data_type img -shard_size 3 -src_dir $test_dir/im2text/images -train_src $test_dir/im2text/src-train.txt -train_tgt $test_dir/im2text/tgt-train.txt -valid_src $test_dir/im2text/src-val.txt -valid_tgt $test_dir/im2text/tgt-val.txt -save_data $test_dir/im2text/data && rm -rf $test_dir/im2text/data*.pt
# test speech2text preprocessing
 python preprocess.py -data_type audio -shard_size 300 -src_dir $test_dir/speech/an4_dataset -train_src $test_dir/speech/src-train.txt -train_tgt $test_dir/speech/tgt-train.txt -valid_src $test_dir/speech/src-val.txt -valid_tgt $test_dir/speech/tgt-val.txt -save_data $test_dir/speech/data && rm -rf $test_dir/speech/data*.pt
# test nmt translation
head data/src-test.txt > $test_dir/src-test.txt; python translate.py -model onmt/tests/test_model.pt -src $test_dir/src-test.txt -verbose
# test nmt ensemble translation
 head data/src-test.txt > $test_dir/src-test.txt; python translate.py -model onmt/tests/test_model.pt onmt/tests/test_model.pt -src $test_dir/src-test.txt -verbose
# test im2text translation
head $test_dir/im2text/src-val.txt > $test_dir/im2text/src-val-head.txt; head $test_dir/im2text/tgt-val.txt > $test_dir/im2text/tgt-val-head.txt; python translate.py -data_type img -src_dir $test_dir/im2text/images -model $test_dir/test_model_im2text.pt -src $test_dir/im2text/src-val-head.txt -tgt $test_dir/im2text/tgt-val-head.txt -verbose -out $test_dir/im2text/trans
# test speech2text translation
head $test_dir/speech/src-val.txt > $test_dir/speech/src-val-head.txt; head $test_dir/speech/tgt-val.txt > $test_dir/speech/tgt-val-head.txt; python translate.py -data_type audio -src_dir $test_dir/speech/an4_dataset -model $test_dir/test_model_speech.pt -src $test_dir/speech/src-val-head.txt -tgt $test_dir/speech/tgt-val-head.txt -verbose -out $test_dir/speech/trans; diff $test_dir/speech/tgt-val-head.txt $test_dir/speech/trans
# test nmt preprocessing and training
head data/src-val.txt > $test_dir/src-val.txt; head data/tgt-val.txt > $test_dir/tgt-val.txt; python preprocess.py -train_src $test_dir/src-val.txt -train_tgt $test_dir/tgt-val.txt -valid_src $test_dir/src-val.txt -valid_tgt $test_dir/tgt-val.txt -save_data $test_dir/q -src_vocab_size 1000 -tgt_vocab_size 1000; python train.py -data $test_dir/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -train_steps 10 && rm -rf $test_dir/q*.pt
# test nmt preprocessing w/ sharding and training w/copy
head data/src-val.txt > $test_dir/src-val.txt; head data/tgt-val.txt > $test_dir/tgt-val.txt; python preprocess.py -train_src $test_dir/src-val.txt -train_tgt $test_dir/tgt-val.txt -valid_src $test_dir/src-val.txt -valid_tgt $test_dir/tgt-val.txt -shard_size 1 -dynamic_dict -save_data $test_dir/q -src_vocab_size 1000 -tgt_vocab_size 1000; python train.py -data $test_dir/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -copy_attn -train_steps 10 && rm -rf $test_dir/q*.pt

# test im2text preprocessing and training
head $test_dir/im2text/src-val.txt > $test_dir/im2text/src-val-head.txt; head $test_dir/im2text/tgt-val.txt > $test_dir/im2text/tgt-val-head.txt; python preprocess.py -data_type img -src_dir $test_dir/im2text/images -train_src $test_dir/im2text/src-val-head.txt -train_tgt $test_dir/im2text/tgt-val-head.txt -valid_src $test_dir/im2text/src-val-head.txt -valid_tgt $test_dir/im2text/tgt-val-head.txt -save_data $test_dir/im2text/q; python train.py -model_type img -data $test_dir/im2text/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -train_steps 10 && rm -rf $test_dir/im2text/q*.pt
# test speech2text preprocessing and training
head $test_dir/speech/src-val.txt > $test_dir/speech/src-val-head.txt; head $test_dir/speech/tgt-val.txt > $test_dir/speech/tgt-val-head.txt; python preprocess.py -data_type audio -src_dir $test_dir/speech/an4_dataset -train_src $test_dir/speech/src-val-head.txt -train_tgt $test_dir/speech/tgt-val-head.txt -valid_src $test_dir/speech/src-val-head.txt -valid_tgt $test_dir/speech/tgt-val-head.txt -save_data $test_dir/speech/q; python train.py -model_type audio -data $test_dir/speech/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -train_steps 10 && rm -rf $test_dir/speech/q*.pt
# test nmt translation
python translate.py -model onmt/tests/test_model2.pt  -src  data/morph/src.valid  -verbose -batch_size 10 -beam_size 10 -tgt data/morph/tgt.valid -out $test_dir/trans; diff  data/morph/tgt.valid $test_dir/trans
# test nmt translation with random sampling
python translate.py -model onmt/tests/test_model2.pt  -src  data/morph/src.valid  -verbose -batch_size 10 -beam_size 1 -seed 1 -random_sampling_topk "-1" -random_sampling_temp 0.0001 -tgt data/morph/tgt.valid -out $test_dir/trans; diff  data/morph/tgt.valid $test_dir/trans
# test tool
PYTHONPATH=$PYTHONPATH:. python tools/extract_embeddings.py -model onmt/tests/test_model.pt
#}}}
#}}}

# vim: foldmethod=marker
