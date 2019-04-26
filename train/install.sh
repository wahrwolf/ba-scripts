#/bin/bash
set -e

# enable debug {{{
set -o functrace
failure() {
	local line_number=$1
	local msg=$2
	echo "Failed at $line_number $msg"
}
trap 'failure ${LINENO} "$BASH_COMMAND"' ERR
# }}}

systemd_version="$(systemctl --version|grep systemd|awk '{print $2}')" 
tmp_dir="${TMP_DIR:-$(mktemp --directory)}"

script_dir="${SCRIPT_DIR:-$tmp_dir/scripts/}"
script_url="${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}"
pip_url="${PIP_URL:-https://bootstrap.pypa.io/get-pip.py}"
onmt_url="${ONMT_URL:-git://github.com/OpenNMT/OpenNMT-py}"
onmt_dir="${ONMT_DIR:-$tmp_dir/onmt/}"
# get and update net-trainer

if [ "$systemd_version" -gt "236" ]
then
	echo "Current systemd version ($systemd_version) does not support tmpfiles for user!"
	echo 'Creating tmpdirectory now!'
	mkdir --parent $tmp_dir
fi

# install files
# install the script {{{
if git ls-remote "$script_dir" 1>2 2>/dev/null
then
	git -C "$script_dir" pull
else
	git clone "$script_url" "${script_dir}"
fi
#}}}

# install python
# install pip {{{
pip_path="${PIP_PATH:-${tmp_dir}/bin/pip}"
pip_dir="$(dirname $pip_path)"

if [[ -x "$PIP_PATH" ]] ; then

	curl "$pip_url" --output "${tmp_dir}/get-pip.py"
	python3 "${tmp_dir}/get-pip.py" --ignore-installed "--prefix=${pip_dir}"
else
	pip_path="$PIP_PATH"
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

# activate long running units
loginctl enable-linger "$(whoami)"

# vim: foldmethod=marker
