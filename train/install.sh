#/bin/bash
set -e

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
script_dir="${SCRIPT_DIR:-$tmp_dir/scripts/}"
script_url="${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}"
pip_url="${PIP_URL:-https://bootstrap.pypa.io/get-pip.py}"
onmt_url="${ONMT_URL:-git://github.com/OpenNMT/OpenNMT-py}"
onmt_dir="${ONMT_DIR:-$tmp_dir/onmt/}"
# get and update net-trainer

# install files
# install the script {{{
if git ls-remote "$script_dir" 2>/dev/null
then
	git -c "$script_dir" pull
else
	git clone "$script_url" "${script_dir}"
fi
#}}}

# install python
# install pip {{{
if [ -z "$PIP_PATH" ] ; then
	pip_path="${tmp_dir}/bin/pip"
fi
pip_dir="$(dirname $PIP_PATH)"

if [ -x "$PIP_PATH" ] ; then

	curl "$pip_url" --output "${tmp_dir}/get-pip.py"
	python3 "${tmp_dir}/get-pip.py" --ignore-installed "--prefix=${pip_dir}"
else
	pip_path="$PIP_PATH"
fi

# }}}

# install pipenv {{{
"$pip_path" install --ignore-installed --install-option="--prefix=${pip_dir}" pipenv
penv="${pip_dir}/bin/pipenv"
# }}}

# install OpenNMT-py {{{
if git ls-remote "$onmt_dir" 2>/dev/null
then
	git -c "$onmt_dir" pull
else
	git clone "$onmt_url" "${onmt_dir}"
fi

# install all requirements for onmt (including pyyaml for use of conifgs
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install --requirements "${onmt_dir}/requirements.txt"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install pyyaml
#}}}

# activate long running units
loginctl enable-linger "$(whoami)"

# vim: foldmethod=marker
