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
get_repo "$script_url" "$script_dir"
#}}}

# install bish-bosh {{{
get_repo "$bish_url" "$bish_dir"
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
get_repo "$onmt_url" "$onmt_dir"

# install onmt (including pyyaml for use of configs)
mkdir -p "$work_dir"
cd "$work_dir"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install -e "${onmt_dir}"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install pyyaml
PIPENV_VENV_IN_PROJECT='enabled' "$penv" run pip install -r "${onmt_dir}"/requirements.txt



# test onmt {{{
test_dir=$(mktemp --directory)
if $script_dir/train/test/onmt_test.sh "$onmt_dir" "$penv" "$test_dir" 1>/dev/null 2>&1
then
	echo "OpenNMT in $onmt_dir passed all tests!"
fi

#}}}

# vim: foldmethod=marker
