#!/bin/bash
set -o errexit
echo "Initialising:"
echo "============="
# shellcheck source=./util.sh
echo -n "Loading additional scripts..."
source "$(dirname $0)/util.sh"
echo -n "Done"
activate_debug


DATA_DIR=${1:-$DATA_DIR}
TMP_DIR=${2:-$TMP_DIR}
CONFIG_DIR=${3:-$CONFIG_DIR}
WORK_DIR=${4:-$WORK_DIR}

if [ -f "$config_dir/environ" ]
then
	echo -n "Found config file! Loading it up..."
	load_env "$config_dir/environ"
	echo "Done"
fi

tmp_dir=${TMP_DIR:-"$(mktemp --directory)"}
work_dir=${WORK_DIR:-$tmp_dir/workbench}
data_dir="${DATA_DIR:-/data/4dahmen/}"
config_dir="${CONFIG_DIR:-${data_dir}/config}"

script_dir=${SCRIPT_DIR:-$tmp_dir/scripts/}
script_url=${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}
pip_url=${PIP_URL:-https://bootstrap.pypa.io/get-pip.py}
onmt_url=${ONMT_URL:-git://github.com/OpenNMT/OpenNMT-py}
onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}
bish_url=${BISH_URL:-git://github.com/raphaelcohn/bish-bosh}
bish_dir=${BISH_DIR:-$tmp_dir/bish/}

echo -n "Creating directories..."
mkdir --parent "$tmp_dir"
mkdir --parent "$work_dir"
mkdir --parent "$data_dir"
mkdir --parent "$config_dir"
echo "Done"


# get and update net-trainer

# install files
# install the script {{{
echo -n "Downloading BA scripts..."
get_repo "$script_url" "$script_dir" 1>/dev/null
echo "Done"
echo -n "Installing configs..."
mkdir --parent "$config_dir"
cp --recursive "$script_dir/config"/* "$config_dir"
echo "Done"
echo "============="
#}}}

# install bish-bosh {{{
echo "Installing bish-bosh:"
echo "====================="
echo -n "Downloading bish-bosh..."
get_repo "$bish_url" "$bish_dir" 1>/dev/null
echo "Done"
echo -n "Downloading dependencies..."
git -C "$bish_dir" submodule update --init --recursive 1>/dev/null
echo "Done"
echo -n "Running tests..."
bish_bin="${bish_dir}/bish-bosh"
chmod +x "$bish_bin"
bash "$script_dir/test/bishbosh_test.sh" "$bish_bin"
echo "Done"
echo "====================="
# }}}

# install python
echo "Installing python:"
echo "=================="
# install pip {{{
pip_path=${PIP_PATH:-${tmp_dir}/bin/pip}
pip_dir=$(dirname $(dirname $pip_path))
if [[ -x "$PIP_PATH" ]] ; then

	pip_path="$PIP_PATH"
else
	echo -n "Downloading pip"
	curl "$pip_url" --output "${tmp_dir}/get-pip.py" 1>/dev/null
	echo "Done"
	echo -n "Installing pip..."
	python3 "${tmp_dir}/get-pip.py" --prefix="${pip_dir}" pip 1>/dev/null
	echo "Done"
fi

export PYTHONPATH=$PYTHONPATH:$pip_dir/lib/$(ls $pip_dir/lib)/site-packages/
echo "New path: pip@[$pip_path] PYTHONPATH@[$PYTHONPATH]"
# }}}

# install pipenv {{{
echo -n "Installing pipenv..."
$pip_path install --ignore-installed --install-option="--prefix=${pip_dir}" pipenv 1/dev/null
pipenv_bin="${pip_dir}/bin/pipenv"
export PIPENV_VENV_IN_PROJECT='enabled'
echo "Done"
# }}}

# install OpenNMT-py {{{
echo -n "Downloading OpenNMT..."
get_repo "$onmt_url" "$onmt_dir" 1>/dev/null
echo "Done"

# install onmt (including pyyaml for use of configs)
cd "$work_dir"
echo -n "Installing OpenNMT..."
"$pipenv_bin" install -e "${onmt_dir}" 1>/dev/null
echo "Done"
echo -n "Downloading dependencies..."
"$pipenv_bin" install pyyaml 1>/dev/null
"$pipenv_bin" run pip install -r "${onmt_dir}"/requirements.txt 1>/dev/null
echo "Done"

# test onmt {{{
echo -n "Running OpenNMT tests..."
test_dir=$(mktemp --directory)
"$script_dir/test/onmt_test.sh" "$onmt_dir" "$pipenv_bin" "$test_dir" 1>/dev/null
echo 'Done'
echo "=================="
#}}}

echo "Cleanup and configuration:"
echo "=========================="
echo -n "Exporting env..."
save_env "$config_dir/environ"
echo 'Done'
echo "=========================="
# vim: foldmethod=marker
