#!/bin/bash

function load_env(){
	local env_file=${1:-environ}
	echo -n "Loading $env_file..."
	while read key; do
		export "${key?}"
	done < <(grep --invert-match --regexp '^#' --regexp '^$' "$env_file")
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

		Current Env:
		------------
		$(printenv)
		------------
		
		Current disc usage:
		-------------------
		$(df --human)
		-------------------
		EOF
	else
		echo "[${module_name}@${line_number}]: $msg"
	fi
}

function activate_debug() {
	echo "Activating debug..."
	if [ -n "$DEBUG_ACTIVATED" ]
	then
		return
	fi 

	set -o functrace
	trap 'notify_on_failure ${LINENO} "$BASH_COMMAND"' ERR
	export DEBUG_ACTIVATED=1
	echo "Done"
}

function disable_debug() {
	echo "Activating debug..."
	if [ -n "$DEBUG_ACTIVATED" ]
	then
		set +o functrace
		trap - ERR
		unset DEBUG_ACTIVATED
		echo "Done"
	fi 
		echo "Not active! Quitting"
		return 1
	echo "Done"
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

function save_env() {
	local target="${1:-./environ}"
	mkdir --parent "$(dirname $target)"
	{
	cat \
		<<-EOF
		# general dirs
		TMP_DIR=$tmp_dir
		WORK_DIR=$work_dir
		DATA_DIR=$data_dir
		CONFIG_DIR=$config_dir

		# remote urls
		SCRIPT_URL=$script_url
		PIP_URL=$pip_url
		ONMT_URL=$onmt_url
		BISH_URL=$bish_url

		# util path
		SCRIPT_DIR=$script_dir
		BISH_DIR=$bish_dir
		ONMT_DIR=$onmt_dir
		PIP_DIR=$pip_dir

		PIP_BIN=$pip_bin
		PIPENV_BIN=$pipenv_bin

		# python specific settings
		PYTHONPATH=$PYTHONPATH
		PIPENV_VENV_IN_PROJECT=enabled
		EOF
	} | envsubst > "$target"
}
