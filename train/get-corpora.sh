#/bin/bash
set -e

corpus_name="${1:-$CORPUS_NAME}"
corpus_host="${CORPUS_HOST:-https://wolfpit.net/share/archive/corpora/}"
tmp_dir="${TMP_DIR:-$(mktemp --directory)}"
data_dir="${DATA_DIR:-/data/4dahmen/}"
config_dir="${CONFIG_DIR:-${data_dir}/configs}"

target_dir="${data_dir}/${corpus_name}"
tmp_file="${tmp_dir}/${corpus_name}.tar.gz"

echo "${corpus_name}: ${corpus_host} --[${tmp_dir}]--> ${target_dir}"
curl "${corpus_host}/${corpus_name}.tar.gz" --out "${tmp_file}"
tar --extract --gzip --file ${tmp_file} --one-top-level="${target_dir}"

for config_template in $(ls "${config_dir}/*.template");
do	
	target_config="${target_dir}"/$(basename --suffix=.template "${config_template}")
	if [ -f "$target_config" ]; then	# use existing config if available
		config_template=$target_config
	fi
	envsubst <"${config_template}" > "${target_config}"
done
