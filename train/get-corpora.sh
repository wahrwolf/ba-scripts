#!/bin/bash
set -o errexit
echo "Initialising:"
echo "============="
export corpus_name="${1:-$CORPUS_NAME}"
export DEBUG_MAIL_TAG="[BA][$corpus_name]"

# shellcheck source=./util.sh
source "$(dirname $0)/util.sh"
activate_debug
load_runtime $CONFIG_DIR

#expose_runtime
export target_dir="${data_dir}/${corpus_name}"
export target_config="${config_dir}/$corpus_name"/$(basename --suffix=.template "${config_template}")
export tmp_file="${tmp_dir}/${corpus_name}.tar.gz"

corpus_host="${CORPUS_HOST:-https://wolfpit.net/share/archive/corpora/}"

echo "${corpus_host}/${corpus_name}.tar.gz --[${tmp_dir}]--> ${target_dir}"
curl "${corpus_host}/${corpus_name}.tar.gz" --out "${tmp_file}"
mkdir --parent "$target_dir"
tar --extract --gzip --file "${tmp_file}" --one-top-level="${target_dir}"

echo "Installing config templates:"
load_env "$config_dir/$corpus_name/environ"
for config_template in "${template_dir}"/*.template;
do	
	echo -n "  $config_template"
	if [ -f "$config_dir/$corpus_name/$(basename "$target_config")" ]
	then
		# use corpora specif config if available
		config_template="$config_dir/$corpus_name/$(basename $target_config)"
		echo "Using $config_template instead of global template"
	elif [ -f "$target_config" ]
	then	# use existing config if available
		echo "Reusing existing config at $target_config"
		config_template=$target_config
	fi
	envsubst <"${config_template}" | tee "${target_config}" > /dev/null
done
