#!/bin/bash
set -o errexit

onmt_dir=${1}
pipenv_bin=${2:-pipenv}
test_dir=${3}

if [ -d "test_dir" ]
then
	test_dir=$(mktemp --directory)
	trap 'rm -rf "$test_dir"' ERR
	cleaup_temp_dir=1
	mkdir --parent "$test_dir"
fi


# test nmt preprocessing
$pipenv_bin run python $onmt_dir/preprocess.py -train_src $onmt_dir/data/src-train.txt -train_tgt $onmt_dir/data/tgt-train.txt -valid_src $onmt_dir/data/src-val.txt -valid_tgt $onmt_dir/data/tgt-val.txt -save_data $test_dir/data -src_vocab_size 1000 -tgt_vocab_size 1000 && rm -rf $test_dir/data*.pt
# test nmt translation
head $onmt_dir/data/src-test.txt > $test_dir/src-test.txt; $pipenv_bin run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model.pt -src $test_dir/src-test.txt -verbose
# test nmt ensemble translation
head $onmt_dir/data/src-test.txt > $test_dir/src-test.txt; $pipenv_bin run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model.pt $onmt_dir/onmt/tests/test_model.pt -src $test_dir/src-test.txt -verbose
# test nmt preprocessing and training
head $onmt_dir/data/src-val.txt > $test_dir/src-val.txt; head $onmt_dir/data/tgt-val.txt > $test_dir/tgt-val.txt; $pipenv_bin run python $onmt_dir/preprocess.py -train_src $test_dir/src-val.txt -train_tgt $test_dir/tgt-val.txt -valid_src $test_dir/src-val.txt -valid_tgt $test_dir/tgt-val.txt -save_data $test_dir/q -src_vocab_size 1000 -tgt_vocab_size 1000; $pipenv_bin run python $onmt_dir/train.py -data $test_dir/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -train_steps 10 && rm -rf $test_dir/q*.pt
# test nmt preprocessing w/ sharding and training w/copy
head $onmt_dir/data/src-val.txt > $test_dir/src-val.txt; head $onmt_dir/data/tgt-val.txt > $test_dir/tgt-val.txt; $pipenv_bin run python $onmt_dir/preprocess.py -train_src $test_dir/src-val.txt -train_tgt $test_dir/tgt-val.txt -valid_src $test_dir/src-val.txt -valid_tgt $test_dir/tgt-val.txt -shard_size 1 -dynamic_dict -save_data $test_dir/q -src_vocab_size 1000 -tgt_vocab_size 1000; $pipenv_bin run python $onmt_dir/train.py -data $test_dir/q -rnn_size 2 -batch_size 10 -word_vec_size 5 -report_every 5 -rnn_size 10 -copy_attn -train_steps 10 && rm -rf $test_dir/q*.pt

# test nmt translation
$pipenv_bin run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model2.pt  -src  $onmt_dir/data/morph/src.valid  -verbose -batch_size 10 -beam_size 10 -tgt $onmt_dir/data/morph/tgt.valid -out $test_dir/trans; diff  $onmt_dir/data/morph/tgt.valid $test_dir/trans
# test nmt translation with random sampling
$pipenv_bin run python $onmt_dir/translate.py -model $onmt_dir/onmt/tests/test_model2.pt  -src  $onmt_dir/data/morph/src.valid  -verbose -batch_size 10 -beam_size 1 -seed 1 -random_sampling_topk "-1" -random_sampling_temp 0.0001 -tgt $onmt_dir/data/morph/tgt.valid -out $test_dir/trans; diff  $onmt_dir/data/morph/tgt.valid $test_dir/trans
# test tool
PYTHONPATH=$PYTHONPATH:. $pipenv_bin run python $onmt_dir/tools/extract_embeddings.py -model $onmt_dir/onmt/tests/test_model.pt

# cleanup
if [ $cleaup_temp_dir -eq 1 ]
then
	rm -rf "$test_dir"
fi

