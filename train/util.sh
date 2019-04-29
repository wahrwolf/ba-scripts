#!/bin/bash

function load_env(){
	local env_file=${1:-environ}
	while read key; do
		export "${key?}"
	done < <(grep -v '^#' "$env_file")
}

function notify_on_failure() {
	local debug_mail=${DEBUG_MAIL:-vincent.dahmen@gmail.com}
	local mail_tag=${DEBUG_MAIL_TAG:-[BA]}
	local machine=${MASCHINE:-"$(whoami)@$(hostname)"}
	local module_name=$0

	local line_number=$1
	local msg=$2
	if [ -z "$debug_mail" ]
	then
		echo "[${module_name}@${line_number}]: $msg"
	else
		sendmail "$debug_mail" \
		<<-EOF
		Subject:$mail_tag: $machine Failure!
		$module_name failed at $line_number
		$msg
		EOF
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
