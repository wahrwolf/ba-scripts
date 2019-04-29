#!/bin/bash

function load_env(){
	local env_file=${1:-environ}
	echo -n "Loading $env_file..."
	while read key; do
		export "${key?}"
	done < <(grep -v '^#' "$env_file")
	echo "Done"
}

function notify_on_failure() {
	local debug_mail=${DEBUG_MAIL:-vincent.dahmen@gmail.com}
	local mail_tag=${DEBUG_MAIL_TAG:-[BA]}
	local machine=${MASCHINE:-"$(whoami)@$(hostname)"}
	local module_name=$0

	local line_number=$1
	local msg=$2
	if [ -n "$debug_mail" ]
	then
		sendmail "$debug_mail" \
		<<-EOF
		Subject:$mail_tag: $machine Failure!
		$module_name failed at $line_number
		$msg
		EOF
	else
		echo "[${module_name}@${line_number}]: $msg"
	fi
}

function activate_debug() {
	if [ -n "$DEBUG_ACTIVATED" ]
	then
		return
	fi 

	set -o functrace
	trap 'notify_on_failure ${LINENO} "$BASH_COMMAND"' ERR
	export DEBUG_ACTIVATED=1
}

function disable_debug() {
	if [ -n "$DEBUG_ACTIVATED" ]
	then
		set +o functrace
		trap - ERR
		unset DEBUG_ACTIVATED
	fi 
		return
}

function get_repo() {
	local url=${1}
	local dir=${2:-$(mktemp --directory)}
	local log_file=${3:-/dev/null}

	if git ls-remote "$dir" 2>"$log_file" 1>&2
	then
		git -C "$dir" pull
	else
		git clone "$url" "${dir}"
	fi
	echo "$dir"
}
