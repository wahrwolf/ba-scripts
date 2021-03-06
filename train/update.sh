#!/bin/bash
set -o errexit
echo "Initialising:"
echo "============="
echo -n "Loading additional scripts..."
# shellcheck source=./util.sh
source "$(dirname "$0")/util.sh"
echo  "Done"
activate_debug
load_runtime "$1"

echo "============="

echo "Downloading BA scripts..."
get_repo "$script_url" "$script_dir"
echo "Done"
echo "Downloading OpenNMT..."
get_repo "$onmt_url" "$onmt_dir"
echo "Done"
echo -n "Backup old config..."
old_config=$(mktemp)
cp "$config_file" "$old_config"
echo "Done"
echo -n "Installing configs..."
mkdir --parent "$config_dir"
cp --recursive --update "$script_dir/config"/* "$config_dir"
echo "Done"
echo -n "Restoring runtime config..."
cp "$old_config" "$config_file" 
rm "$old_config"
echo "Done"
echo "============="
