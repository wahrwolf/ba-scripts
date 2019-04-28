#!/bin/bash
set -e

debug_mail="${DEBUG_MAIL:-vincent.dahmen@gmail.com}"
mail_tag="${DEBUG_MAIL_TAG:-[BA]}"
machine="${MASCHINE:-$(whoami)@$(hostname)}"
module_name="$0"

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

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"

script_dir="${SCRIPT_DIR:-$tmp_dir/scripts/}"
script_url="${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}"
pip_url="${PIP_URL:-https://bootstrap.pypa.io/get-pip.py}"
onmt_url="${ONMT_URL:-git://github.com/OpenNMT/OpenNMT-py}"
onmt_dir="${ONMT_DIR:-$tmp_dir/onmt/}"
bish_url="${BISH_URL:-git://github.com/raphaelcohn/bish-bosh}"
bish_dir="${BISH_DIR:-$tmp_dir/bish/}"
# get and update net-trainer


# install files
# install the script {{{
if git ls-remote "$script_dir" 1>2 2>/dev/null
then
	git -C "$script_dir" pull
else
	git clone "$script_url" "${script_dir}"
fi
#}}}

# install bish-bosh {{{
if git ls-remote "$bish_dir" 1>2 2>/dev/null
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
pip_path="${PIP_PATH:-${tmp_dir}/bin/pip}"
pip_dir=$(dirname "$pip_path")

if [[ -x "$PIP_PATH" ]] ; then

	pip_path="$PIP_PATH"
else
	curl "$pip_url" --output "${tmp_dir}/get-pip.py"
	python3 "${tmp_dir}/get-pip.py" --ignore-installed "--prefix=${pip_dir}"
fi

# }}}

# install pipenv {{{
$pip_path install --ignore-installed --install-option="--prefix=${pip_dir}" pipenv
penv="${pip_dir}/bin/pipenv"
# }}}

# install OpenNMT-py {{{
if git ls-remote "$onmt_dir" 2>/dev/null
then
	git -C "$onmt_dir" pull
else
	git clone "$onmt_url" "${onmt_dir}"
fi

# install all requirements for onmt (including pyyaml for use of conifgs
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install --requirements "${onmt_dir}/requirements.txt"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install pyyaml
#}}}

# vim: foldmethod=marker
