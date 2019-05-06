#!/bin/bash
function load_runtime(){
	echo -n "Looking for config file..."
	if [ -f "$1" ]
	then
		config_file=$1
	elif [ -f "$1/environ" ]
	then
		config_file="$1/environ"
	elif [ -f "${CONFIG_DIR:-$(pwd)}/environ" ]
	then
		config_file="${CONFIG_DIR:-$(pwd)}/environ" 
	else
		echo "Fail!"
		return 1
	fi
	echo "Done"
	load_env "$config_file" || true
	echo -n "Setting up runtime config..."
	readonly tmp_dir=${TMP_DIR:-"$(mktemp --directory)"}
	readonly work_dir=${WORK_DIR:-$tmp_dir/workbench}
	readonly data_dir="${DATA_DIR:-/data/4dahmen/}"
	readonly config_dir="${CONFIG_DIR:-${data_dir}/config}"

	readonly script_dir=${SCRIPT_DIR:-$tmp_dir/scripts/}
	readonly script_url=${SCRIPT_URL:-git://wolfpit.net/university/BA/scripts}
	readonly pip_url=${PIP_URL:-https://bootstrap.pypa.io/get-pip.py}
	readonly onmt_url=${ONMT_URL:-git://github.com/OpenNMT/OpenNMT-py}
	readonly onmt_dir=${ONMT_DIR:-$tmp_dir/onmt/}
	readonly bish_url=${BISH_URL:-git://github.com/raphaelcohn/bish-bosh}
	readonly bish_dir=${BISH_DIR:-$tmp_dir/bish/}
	echo "Done"

	readonly config_file=$config_file
}

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

function repo_was_force_pushed(){
	local dir=$1
	local local_commit=${2:-HEAD}
	local remote_branch=${3:-origin/master}

	# https://stackoverflow.com/questions/10319110/how-to-detect-a-forced-update
	local new_commits
	new_commits=$(git -C "$dir" rev-list "$local_commit" "^${remote_branch}")
	if [ -z "$new_commits" ]; then
		exit 1
	fi
}

function repo_is_valid(){
	local dir=$1
	local remotes
	remotes=$(git ls-remote "$dir" 2>/dev/null)
	if [ -z "$remotes" ]
	then
		return 1
	fi
	return
}

function get_repo() {
	local url=${1}
	local dir=${2:-$(mktemp --directory)}
	local log_file=${3:-/dev/null}

	if (repo_is_valid "$dir") && (! repo_was_force_pushed "$dir")
	then
		git -C "$dir" pull
	else
		rm --recursive --force "$dir"
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
