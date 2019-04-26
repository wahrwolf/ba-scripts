#/bin/bash
set -e

tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
script_dir="${SCRIPT_DIR:-$tmp_dir/scripts/}"
script_url="${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}"
systemd_version="$(systemctl --version|grep systemd|awk '{print $2}')" 

# install files
# install the script {{{
if git ls-remote "$script_dir" 1>2 2>/dev/null
then
	git -C "$script_dir" pull
else
	git clone "$script_url" "${script_dir}"
fi
#}}}

mkdir --parents "${HOME}/.config/systemd/user"
# install systemd units {{{

echo 'Installing systemd units'
cp --update "${script_dir}/train/units/"* --target-directory "${HOME}/.config/systemd/user"
systemctl --user daemon-reload

echo 'Installing tmpfiles'
if [ "$systemd_version" -gt "236" ]
then
	cp --update "${script_dir}/train/tmpfiles/"* --target-directory "${HOME}/.config/user-tmpfiles.d"
	systemctl --user enable --now systemd-tmpfiles-setup.service systemd-tmpfiles-clean.timer
else
	echo "Current systemd version ($systemd_version) does not support tmpfiles for user... Skipping!"
fi
# }}}
