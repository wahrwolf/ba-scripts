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

echo -n "Downloading BA scripts..."
get_repo "$script_url" "$script_dir" 1>/dev/null
echo "Done"
echo -n "Installing configs..."
mkdir --parent "$config_dir"
cp --recursive --backup=numbered --update "$script_dir/config"/* "$config_dir"
echo "Done"
echo "============="
