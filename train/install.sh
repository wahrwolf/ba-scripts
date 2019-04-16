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
if [ $(git ls-remote "$script_dir")]
then
	git -c "$script_dir" pull
else
	git clone "$script_url" "${script_dir}"
fi
#}}}

# install systemd units {{{
install -D --directory "${script_dir}/train/units" "${HOME}/.config/systemd/user"
systemctl --user daemon-reload

install -D --directory "${script_dir}/train/tmpfiles" "${HOME}/.config/user-tmpfiles.d"
systemctl --user enable --now systemd-tmpfiles-setup.service systemd-tmpfiles-clean.timer

# }}}

# install python
# install pip {{{
if [ -z "$PIP_PATH" ]
then
	curl "$pip_url" --output "${tmp_dir}/get-pip.py"
	python3 "${tmp_dir}/get-pip.py" --ignore-installed "--prefix=${tmp_dir}"
	pip_path="${tmp_dir}/bin/pip"
else
	pip_path="$PIP_PATH"
fi

# }}}

# install pipenv {{{
"$pip_path" install --ignore-installed --install-option="--prefix=${tmp_dir}" pipenv
penv="${tmp_dir}/bin/pipenv"
# }}}

# install OpenNMT-py {{{
if [ $(git ls-remote "$onmt_dir")]
then
	git -c "$onmt_dir" pull
else
	git clone "$onmt_url" "${onmt_dir}"
fi

PIPENV_VENV_IN_PROJECT='enabled' "$penv" install --requirements "${onmt_dir}/requirements.txt"
PIPENV_VENV_IN_PROJECT='enabled' "$penv" install --requirements "${onmt_dir}/requirements.opt.txt"
#}}}

# activate long running units
loginctl enable-linger "$(whoami)"

loginctl disable-linger "$(whoami)"

# vim: foldmethod=marker
