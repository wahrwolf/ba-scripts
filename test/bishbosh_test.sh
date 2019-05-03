#!/bin/bash
set -o errexit

bish_bin=${1}
test_server=${2:-test.mosquitto.org}
test_dir=${3}

if [ -d "test_dir" ]
then
	test_dir=$(mktemp --directory)
	trap 'rm -rf "$test_dir"' ERR
	cleaup_temp_dir=1
	mkdir --parent "$test_dir"
fi

"$bish_bin" --version

# cleanup
if [ $cleaup_temp_dir -eq 1 ]
then
	rm -rf "$test_dir"
fi
