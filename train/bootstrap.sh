#/bin/bash
set -e

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
script_dir="${SCRIPT_DIR:-$tmp_dir/scripts/}"
script_url="${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}"

# install files
# install the script {{{
if git ls-remote "$script_dir" 1>2 2>/dev/null
then
	git pull --verbose -c "$script_dir"
else
	git clone "$script_url" "${script_dir}"
fi
#}}}

mkdir --parents "${HOME}/.config/systemd/user"
# install systemd units {{{
cp --recursive --update "${script_dir}/train/units/*" "${HOME}/.config/systemd/user"
systemctl --user daemon-reload

cp --recursive --update "${script_dir}/train/tmpfiles/*" "${HOME}/.config/user-tmpfiles.d"
systemctl --user enable --now systemd-tmpfiles-setup.service systemd-tmpfiles-clean.timer
# }}}
