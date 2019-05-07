#!/bin/bash
set -o errexit
echo "Initialising:"
echo "============="
# shellcheck source=./util.sh
echo -n "Loading additional scripts..."
source "$(dirname $0)/util.sh"
echo  "Done"
activate_debug

DATA_DIR=${1:-$DATA_DIR}
TMP_DIR=${2:-$TMP_DIR}
CONFIG_DIR=${3:-$CONFIG_DIR}
WORK_DIR=${4:-$WORK_DIR}

load_runtime "$CONFIG_DIR/environ"

echo -n "Creating directories..."
mkdir --parent "$tmp_dir"
mkdir --parent "$work_dir"
mkdir --parent "$data_dir"
mkdir --parent "$config_dir"
echo "Done"

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
bash "$script_dir/test/bishbosh_test.sh" "$bish_bin" 1>/dev/null
echo "Done"
echo "====================="
# }}}

# install python
echo "Installing python:"
echo "=================="
# install pip {{{
if [ ! -x "$pip_bin" ]
then
	echo -n "Downloading pip"
	curl "$pip_url" --output "${tmp_dir}/get-pip.py" 1>/dev/null
	echo "Done"
	echo -n "Installing pip..."
	python3 "${tmp_dir}/get-pip.py" -qq --target "${pip_dir}" pip 
	echo "Done"
	rm "${tmp_dir}/get-pip.py" 
else
	echo "Found existing pip installation!"
fi

export PYTHONPATH=$pip_dir
echo "New path: pip@[$pip_bin] PYTHONPATH@[$PYTHONPATH]"
# }}}

# install pipenv {{{
if [ ! -x "$pipenv_bin" ]
then
	echo -n "Installing pipenv..."
	$pip_bin -qq install --upgrade --target "${pip_dir}" pipenv
	export PIPENV_VENV_IN_PROJECT='enabled'
	export PIPENV_HIDE_EMOJIS=1
	export PIPENV_QUIET=1
	echo "Done"
else
	echo "Found existing pipenv!"
fi
# }}}

# install OpenNMT-py {{{
echo -n "Downloading OpenNMT..."
get_repo "$onmt_url" "$onmt_dir" 1>/dev/null
echo "Done"

# install onmt (including pyyaml for use of configs)
cd "$work_dir"
echo "Installing OpenNMT..."
"$pipenv_bin" install -e "${onmt_dir}" 1>/dev/null
echo "Downloading dependencies..."
"$pipenv_bin" install pyyaml 1>/dev/null
"$pipenv_bin" run pip -qq install -r "${onmt_dir}"/requirements.txt 1>/dev/null

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
