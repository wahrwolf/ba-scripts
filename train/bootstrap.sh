#/bin/bash
set -e

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
script_dir="${SCRIPT_DIR:-$tmp_dir/scripts/}"
script_url="${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}"

# install files
# install the script {{{
if [ $(git ls-remote "$script_dir" 2>/dev/null)]
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
