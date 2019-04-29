set -o errexit
script_dir="${SCRIPT_DIR:-$(dirname $0)/../}"
train_dir="${TRAIN_DIR:-$script_dir/train/}"

# shellcheck source=./util.sh
echo -n "Loading utils from $train_dir..." 
source "$train_dir/util.sh"
echo "Done\!"

echo -n "Loading env..." 
load_env "$train_dir/config/environ"
echo "Done\!"

corpus_name="${1:-$CORPUS_NAME}"
activate_debug

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
data_dir="${DATA_DIR:-/data/4dahmen/}"
config_dir="${CONFIG_DIR:-${data_dir}/config}"
corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"

echo -n "Loading corpus specifc env..." 
load_env "$config_dir/$corpus_name/environ"
echo "Done\!"

target_dir="${TARGET_DIR:-${corpus_dir}/preprocess/}"
mkdir --parent "$target_dir"

onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}

echo -n "Running preprocess..."
$pipenv_bin run python $onmt_dir/preprocess.py  --config "$corpus_dir/preprocess.config"
echo "All set!"
