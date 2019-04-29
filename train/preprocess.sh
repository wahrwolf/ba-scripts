set -o errexit
script_dir="${SCRIPT_DIR:-$(dirname $0)/../}"
train_dir="${TRAIN_DIR:-$script_dir/train/}"

echo "Loading $train_dir..."

# shellcheck source=./util.sh
source "$train_dir/util.sh"

load_env "$train_dir/config/environ"

corpus_name="${1:-$CORPUS_NAME}"
activate_debug

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
data_dir="${DATA_DIR:-/data/4dahmen/}"
config_dir="${CONFIG_DIR:-${data_dir}/config}"
corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"

load_env "$config_dir/$corpus_name/environ"

target_dir="${TARGET_DIR:-${corpus_dir}/preprocess/}"
mkdir --parent "$target_dir"

onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}

$pipenv_bin run python $onmt_dir/preprocess.py  --config "$corpus_dir/preprocess.config"
