#!/bin/bash
set -e

debug_mail=${DEBUG_MAIL:-vincent.dahmen@gmail.com}
mail_tag=${DEBUG_MAIL_TAG:-[BA]}
machine=${MASCHINE:-"$(whoami)@$(hostname)"}
module_name=$0

# enable debug {{{
set -o functrace
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

tmp_dir=${TMP_DIR:-$(mktemp --directory)}
script_dir=${SCRIPT_DIR:-$tmp_dir/scripts/}
script_url=${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}

# install files
# install the script {{{
if git ls-remote "$script_dir" 2>/dev/null 1>&2
then
	git -C "$script_dir" pull
else
	git clone "$script_url" "${script_dir}"
fi
source "$script_dir/train/util.sh"
#}}}

# import target environ {{{
load_env() "${script_dir}/train/config/environ"
#}}}

$script_dir/train/install.sh

# vim: foldmethod=marker
