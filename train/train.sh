set -o errexit
script_dir="${SCRIPT_DIR:-$(dirname $0)/../}"
train_dir="${TRAIN_DIR:-$script_dir/train/}"

echo -n "Loading utils from $train_dir..." 
# shellcheck source=./util.sh
source "$train_dir/util.sh"
echo "Done!"

load_env "$train_dir/config/environ"

corpus_name="${1:-$CORPUS_NAME}"
activate_debug

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
work_dir="${WORK_DIR:-$tmp_dir/workbench}"
data_dir="${DATA_DIR:-/data/4dahmen/}"
config_dir="${CONFIG_DIR:-${data_dir}/config}"
corpus_dir="${CORPUS_DIR:-$data_dir/$corpus_name/}"

load_env "$config_dir/$corpus_name/environ"

target_dir="${TARGET_DIR:-${corpus_dir}/preprocess/}"
mkdir --parent "$target_dir"

pip_dir="${PIP_DIR:-$(dirname $script_dir)}"
pipenv_bin="${pip_dir}/bin/pipenv"
onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}

echo -n "Running train..."
mkdir --parent "$work_dir"
cd "$work_dir"
export PYTHONPATH="$PYTHONPATH:$pip_dir/lib/$(ls $pip_dir/lib)/site-packages/"
$pipenv_bin run python "$onmt_dir/train.py"  --config "$config_dir/$corpus_name/train.config"
echo "All set!"
